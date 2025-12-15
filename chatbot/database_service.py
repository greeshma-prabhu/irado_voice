"""
Database service voor bedrijfsklanten (voormalig KOAD blacklist)
Vervangt CSV-based KOAD systeem met PostgreSQL database
"""

import psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values
from typing import Dict, List, Optional, Tuple, Any
import logging
import os
from config import Config

logger = logging.getLogger(__name__)

class BedrijfsklantenDatabaseService:
    """Service voor bedrijfsklanten database operaties"""
    
    def __init__(self):
        self.config = Config()
        self.connection = None
        self._schema_ready = False
        self._session_configured = False

    def _ensure_table_schema(self, conn):
        """Ensure bedrijfsklanten table structure matches CSV schema"""
        if self._schema_ready:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bedrijfsklanten (
                    "KOAD-nummer" VARCHAR(255),
                    "KOAD-str" VARCHAR(255),
                    "KOAD-pc" VARCHAR(10),
                    "KOAD-huisaand" VARCHAR(50),
                    "KOAD-huisnr" VARCHAR(20),
                    "KOAD-etage" VARCHAR(50),
                    "KOAD-naam" VARCHAR(255),
                    "KOAD-actief" VARCHAR(1) DEFAULT '1',
                    "KOAD-inwoner" VARCHAR(1) DEFAULT '1'
                )
            """)

            columns = [
                ("KOAD-nummer", "VARCHAR(255)"),
                ("KOAD-str", "VARCHAR(255)"),
                ("KOAD-pc", "VARCHAR(10)"),
                ("KOAD-huisaand", "VARCHAR(50)"),
                ("KOAD-huisnr", "VARCHAR(20)"),
                ("KOAD-etage", "VARCHAR(50)"),
                ("KOAD-naam", "VARCHAR(255)"),
                ("KOAD-actief", "VARCHAR(1) DEFAULT '1'"),
                ("KOAD-inwoner", "VARCHAR(1) DEFAULT '1'")
            ]

            for column_name, column_type in columns:
                cursor.execute(
                    f'ALTER TABLE bedrijfsklanten ADD COLUMN IF NOT EXISTS "{column_name}" {column_type}'
                )

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bedrijfsklanten_lookup
                ON bedrijfsklanten ("KOAD-pc", "KOAD-huisnr")
            """)

            conn.commit()
            self._schema_ready = True
        finally:
            cursor.close()

    def _configure_session(self):
        if not self.connection or self._session_configured:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SET TIME ZONE %s", (self.config.APP_TIMEZONE,))
            self.connection.commit()
        except Exception as e:
            logger.warning(f"Failed to set database timezone: {e}")
            self.connection.rollback()
        finally:
            self._session_configured = True

    def _get_connection(self):
        """Krijg database verbinding - now uses main chat database"""
        if not self.connection or self.connection.closed:
            try:
                if not self.config.POSTGRES_PASSWORD:
                    raise ValueError("POSTGRES_PASSWORD is not configured. Set it via app settings or connection string.")

                host = self.config.POSTGRES_HOST
                port = int(self.config.POSTGRES_PORT or 5432)
                database = self.config.POSTGRES_DB
                user = self.config.POSTGRES_USER
                password = self.config.POSTGRES_PASSWORD
                
                logger.info(f"🔍 DatabaseService database connection attempt:")
                logger.info(f"   Host: {host}")
                logger.info(f"   Port: {port}")
                logger.info(f"   Database: {database}")
                logger.info(f"   User: {user}")
                logger.info(f"   Password: {'*' * len(password) if password else 'None'}")
                
                self.connection = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password,
                    sslmode=self.config.POSTGRES_SSL_MODE or 'require'
                )
                self.connection.autocommit = False
                self._configure_session()
                self._ensure_table_schema(self.connection)
                logger.info("✅ DatabaseService database connection successful!")
            except Exception as e:
                logger.error(f"❌ DatabaseService database connection failed: {e}")
                logger.error(f"   Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                raise
        return self.connection
    
    def is_bedrijfsklant(self, postcode: str, huisnummer: str) -> bool:
        """
        Controleer of een adres een bedrijfsklant is
        
        Args:
            postcode: Nederlandse postcode
            huisnummer: Huisnummer
            
        Returns:
            True als het een bedrijfsklant is, False anders
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Normaliseer postcode (hoofdletters, geen spaties)
            normalized_postcode = postcode.strip().upper().replace(' ', '')
            normalized_huisnummer = str(huisnummer).strip()
            
            # Check if address exists in bedrijfsklanten table
            # If it exists -> bedrijfsklant, if not -> particulier
            cursor.execute(
                """
                SELECT EXISTS(
                    SELECT 1
                    FROM bedrijfsklanten 
                    WHERE REPLACE(UPPER("KOAD-pc"), ' ', '') = %s 
                      AND TRIM(COALESCE("KOAD-huisnr", '')) = %s
                )
                """,
                (normalized_postcode, normalized_huisnummer)
            )
            
            result = cursor.fetchone()[0]
            cursor.close()
            
            is_bedrijf = bool(result)
            print(f"🏢 Bedrijfsklant check: {normalized_postcode} {normalized_huisnummer} -> {'JA (bedrijf)' if is_bedrijf else 'NEE (particulier)'}")
            
            return is_bedrijf
            
        except Exception as e:
            logger.error(f"Bedrijfsklant check gefaald: {e}")
            print(f"⚠️  Bedrijfsklant check gefaald: {e}")
            print(f"   Assuming particulier (not in database)")
            # If database check fails, assume particulier (not bedrijfsklant)
            return False
    
    def get_bedrijfsklant_info(self, postcode: str, huisnummer: str) -> Optional[Dict[str, Any]]:
        """
        Krijg bedrijfsklant informatie
        
        Args:
            postcode: Nederlandse postcode
            huisnummer: Huisnummer
            
        Returns:
            Dict met bedrijfsklant info of None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Normaliseer postcode
            normalized_postcode = postcode.strip().upper().replace(' ', '')
            normalized_huisnummer = str(huisnummer).strip()
            
            cursor.execute(
                """
                SELECT 
                    "KOAD-nummer" AS koad_nummer,
                    "KOAD-str" AS straat,
                    "KOAD-pc" AS postcode,
                    "KOAD-huisaand" AS huisnummer_toevoeging,
                    "KOAD-huisnr" AS huisnummer,
                    "KOAD-etage" AS etage,
                    "KOAD-naam" AS naam,
                    "KOAD-actief" AS actief,
                    "KOAD-inwoner" AS inwoner
                FROM bedrijfsklanten
                WHERE REPLACE(UPPER("KOAD-pc"), ' ', '') = %s
                  AND TRIM(COALESCE("KOAD-huisnr", '')) = %s
                LIMIT 1
                """,
                (normalized_postcode, normalized_huisnummer)
            )
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            logger.error(f"Bedrijfsklant info ophalen gefaald: {e}")
            return None
    
    def search_bedrijfsklanten(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Zoek bedrijfsklanten
        
        Args:
            query: Zoekterm
            limit: Maximum aantal resultaten
            
        Returns:
            Lijst van bedrijfsklanten
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            search_query = f"%{query.strip()}%"
            
            cursor.execute("""
                SELECT 
                    "KOAD-nummer", "KOAD-str", "KOAD-pc", "KOAD-huisaand",
                    "KOAD-huisnr", "KOAD-etage", "KOAD-naam", "KOAD-actief", "KOAD-inwoner"
                FROM bedrijfsklanten 
                WHERE 
                    LOWER("KOAD-str") LIKE LOWER(%s) OR
                    LOWER("KOAD-pc") LIKE LOWER(%s) OR
                    LOWER("KOAD-huisnr") LIKE LOWER(%s) OR
                    LOWER("KOAD-naam") LIKE LOWER(%s)
                ORDER BY "KOAD-str", "KOAD-huisnr"
                LIMIT %s
            """, (search_query, search_query, search_query, search_query, limit))
            
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Bedrijfsklanten zoeken gefaald: {e}")
            return []
    
    def get_bedrijfsklanten_stats(self) -> Dict[str, Any]:
        """
        Krijg statistieken over bedrijfsklanten
        
        Returns:
            Dict met statistieken
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Count total
            cursor.execute('SELECT COUNT(*) FROM bedrijfsklanten')
            total = cursor.fetchone()[0]
            
            # Count active
            cursor.execute('SELECT COUNT(*) FROM bedrijfsklanten WHERE "KOAD-actief" = \'1\'')
            active = cursor.fetchone()[0]
            
            # Count unique postcodes
            cursor.execute('SELECT COUNT(DISTINCT "KOAD-pc") FROM bedrijfsklanten')
            unique_postcodes = cursor.fetchone()[0]
            
            # Count unique streets
            cursor.execute('SELECT COUNT(DISTINCT "KOAD-str") FROM bedrijfsklanten')
            unique_streets = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'total_entries': total,
                'active_entries': active,
                'inactive_entries': total - active,
                'unique_postcodes': unique_postcodes,
                'unique_streets': unique_streets
            }
            
        except Exception as e:
            logger.error(f"Statistieken ophalen gefaald: {e}")
            print(f"❌ Stats error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'total_entries': 0,
                'active_entries': 0,
                'inactive_entries': 0,
                'unique_postcodes': 0,
                'unique_streets': 0
            }
    
    def add_bedrijfsklant(self, koad_data: Dict[str, Any]) -> bool:
        """
        Voeg nieuwe bedrijfsklant toe
        
        Args:
            koad_data: Dict met bedrijfsklant data
            
        Returns:
            True als succesvol, False anders
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO bedrijfsklanten 
                (koad_nummer, straat, postcode, huisnummer, huisnummer_toevoeging, 
                 etage, naam, actief, inwoner)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                koad_data.get('koad_nummer', ''),
                koad_data.get('straat', ''),
                koad_data.get('postcode', '').strip().upper(),
                koad_data.get('huisnummer', ''),
                koad_data.get('huisnummer_toevoeging', ''),
                koad_data.get('etage', ''),
                koad_data.get('naam', ''),
                koad_data.get('actief', True),
                koad_data.get('inwoner', True)
            ))
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Bedrijfsklant toevoegen gefaald: {e}")
            if conn:
                conn.rollback()
            return False
    
    def update_bedrijfsklant(self, bedrijfsklant_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update bedrijfsklant
        
        Args:
            bedrijfsklant_id: ID van bedrijfsklant
            update_data: Dict met te updaten data
            
        Returns:
            True als succesvol, False anders
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Bouw UPDATE query dynamisch
            set_clauses = []
            values = []
            
            for key, value in update_data.items():
                if key in ['straat', 'postcode', 'huisnummer', 'huisnummer_toevoeging', 
                          'etage', 'naam', 'actief', 'inwoner']:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(bedrijfsklant_id)
            
            cursor.execute(f"""
                UPDATE bedrijfsklanten 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """, values)
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Bedrijfsklant updaten gefaald: {e}")
            if conn:
                conn.rollback()
            return False
    
    def delete_bedrijfsklant(self, bedrijfsklant_id: int) -> bool:
        """
        Verwijder bedrijfsklant
        
        Args:
            bedrijfsklant_id: ID van bedrijfsklant
            
        Returns:
            True als succesvol, False anders
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM bedrijfsklanten WHERE id = %s", (bedrijfsklant_id,))
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Bedrijfsklant verwijderen gefaald: {e}")
            if conn:
                conn.rollback()
            return False
    
    def upload_csv_data(self, csv_data: List[Dict[str, Any]], filename: str) -> Dict[str, int]:
        """
        Upload CSV data naar database (overschrijft bestaande data)
        Table structure now matches CSV exactly
        
        Args:
            csv_data: Lijst van dicts met CSV data
            filename: Naam van CSV bestand
            
        Returns:
            Dict met import statistieken
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verwijder alle bestaande data
            cursor.execute("DELETE FROM bedrijfsklanten")
            deleted_count = cursor.rowcount
            print(f"🗑️ Deleted {deleted_count} old records")
            
            # Import nieuwe data in batches (memory efficient!)
            imported_count = 0
            batch_size = 1000  # Increased batch size for better performance
            total_rows = len(csv_data)
            
            print(f"📊 Starting batch import: {total_rows} total records")
            
            for batch_start in range(0, total_rows, batch_size):
                batch_end = min(batch_start + batch_size, total_rows)
                batch = csv_data[batch_start:batch_end]
                
                # Calculate progress percentage
                progress_percent = int((batch_start / total_rows) * 100)
                print(f"🔄 Processing batch {batch_start//batch_size + 1}: records {batch_start+1}-{batch_end} ({progress_percent}%)")
                
                # Build batch insert
                values = []
                for row in batch:
                    try:
                        values.append((
                            str(row.get('KOAD-nummer', '')),
                            str(row.get('KOAD-str', '')),
                            str(row.get('KOAD-pc', '')),
                            str(row.get('KOAD-huisaand', '')),
                            str(row.get('KOAD-huisnr', '')),
                            str(row.get('KOAD-etage', '')),
                            str(row.get('KOAD-naam', '')),
                            str(row.get('KOAD-actief', '1')),
                            str(row.get('KOAD-inwoner', '1'))
                        ))
                    except Exception as e:
                        logger.warning(f"Row skipped in batch: {e}")
                        continue
                
                # Execute batch insert
                if values:
                    try:
                        execute_values(
                            cursor,
                            """
                            INSERT INTO bedrijfsklanten 
                            ("KOAD-nummer", "KOAD-str", "KOAD-pc", "KOAD-huisaand", 
                             "KOAD-huisnr", "KOAD-etage", "KOAD-naam", "KOAD-actief", "KOAD-inwoner")
                            VALUES %s
                            """,
                            values
                        )
                        imported_count += len(values)
                        
                        # Commit every batch to free memory
                        conn.commit()
                        
                        # Progress logging
                        progress_pct = int((imported_count / total_rows) * 100)
                        print(f"  ✅ Progress: {imported_count:,}/{total_rows:,} ({progress_pct}%)")
                        
                        # Log progress to dashboard logs
                        try:
                            from logging_service import log_info
                            log_info('CSV_UPLOAD', 'batch_progress', f'Batch {batch_start//batch_size + 1} completed', {
                                'batch_number': batch_start//batch_size + 1,
                                'total_batches': (total_rows // batch_size) + 1,
                                'records_imported': imported_count,
                                'total_records': total_rows,
                                'progress_percent': progress_pct
                            })
                        except ImportError:
                            pass  # Logging service not available
                        
                    except Exception as e:
                        logger.error(f"Batch insert failed: {e}")
                        conn.rollback()
                        # Try individual inserts as fallback
                        for val in values:
                            try:
                                cursor.execute("""
                                    INSERT INTO bedrijfsklanten 
                                    ("KOAD-nummer", "KOAD-str", "KOAD-pc", "KOAD-huisaand", 
                                     "KOAD-huisnr", "KOAD-etage", "KOAD-naam", "KOAD-actief", "KOAD-inwoner")
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, val)
                                imported_count += 1
                            except:
                                pass
                        conn.commit()
            
            cursor.close()
            print(f"✅ Total imported: {imported_count:,} records (deleted {deleted_count:,} old)")
            
            return {
                'imported': imported_count,
                'deleted': deleted_count,
                'updated': 0
            }
            
        except Exception as e:
            logger.error(f"CSV upload gefaald: {e}")
            print(f"❌ CSV upload error: {e}")
            import traceback
            traceback.print_exc()
            if 'conn' in locals() and conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise  # Re-raise to let dashboard handler catch it
    
    def close(self):
        """Sluit database verbinding"""
        if self.connection and not self.connection.closed:
            self.connection.close()
