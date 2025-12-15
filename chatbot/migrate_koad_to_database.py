#!/usr/bin/env python3
"""
Migratie script om KOAD CSV naar PostgreSQL database te verplaatsen
Van blacklist naar bedrijfsklanten database
"""

import os
import sys
import csv
import psycopg2
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/irado/chatbot/migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KOADDatabaseMigrator:
    """Migreert KOAD CSV data naar PostgreSQL database"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None
        
    def connect(self) -> bool:
        """Maak verbinding met PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.connection.autocommit = False
            logger.info("Database verbinding succesvol")
            return True
        except Exception as e:
            logger.error(f"Database verbinding gefaald: {e}")
            return False
    
    def disconnect(self):
        """Sluit database verbinding"""
        if self.connection:
            self.connection.close()
            logger.info("Database verbinding gesloten")
    
    def create_schema(self) -> bool:
        """Maak database schema aan"""
        try:
            cursor = self.connection.cursor()
            
            # Lees schema bestand
            schema_file = '/opt/irado/chatbot/database_schema.sql'
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Voer schema uit
            cursor.execute(schema_sql)
            self.connection.commit()
            cursor.close()
            
            logger.info("Database schema succesvol aangemaakt")
            return True
            
        except Exception as e:
            logger.error(f"Schema aanmaken gefaald: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def load_csv_data(self, csv_file_path: str) -> pd.DataFrame:
        """Laad CSV data in pandas DataFrame"""
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8')
            logger.info(f"CSV geladen: {len(df)} records uit {csv_file_path}")
            return df
        except Exception as e:
            logger.error(f"CSV laden gefaald: {e}")
            return pd.DataFrame()
    
    def clear_existing_data(self) -> bool:
        """Verwijder alle bestaande bedrijfsklanten data"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT clear_all_bedrijfsklanten()")
            deleted_count = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Bestaande data verwijderd: {deleted_count} records")
            return True
            
        except Exception as e:
            logger.error(f"Data verwijderen gefaald: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def migrate_csv_to_database(self, df: pd.DataFrame, filename: str) -> Tuple[int, int, int]:
        """
        Migreer CSV data naar database
        
        Returns:
            Tuple van (imported, updated, deleted) counts
        """
        imported = 0
        updated = 0
        deleted = 0
        
        try:
            cursor = self.connection.cursor()
            
            # Voorbereid INSERT statement
            insert_sql = """
                INSERT INTO bedrijfsklanten 
                (koad_nummer, straat, postcode, huisnummer, huisnummer_toevoeging, 
                 etage, naam, actief, inwoner)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Verwerk elke rij
            for index, row in df.iterrows():
                try:
                    # Normaliseer data
                    koad_nummer = str(row.get('KOAD-nummer', '')).strip()
                    straat = str(row.get('KOAD-str', '')).strip()
                    postcode = str(row.get('KOAD-pc', '')).strip().upper()
                    huisnummer = str(row.get('KOAD-huisnr', '')).strip()
                    huisnummer_toevoeging = str(row.get('KOAD-huisaand', '')).strip()
                    etage = str(row.get('KOAD-etage', '')).strip()
                    naam = str(row.get('KOAD-naam', '')).strip()
                    actief = bool(row.get('KOAD-actief', True))
                    inwoner = bool(row.get('KOAD-inwoner', True))
                    
                    # Skip lege records
                    if not postcode or not huisnummer:
                        continue
                    
                    # Voeg record toe
                    cursor.execute(insert_sql, (
                        koad_nummer, straat, postcode, huisnummer, 
                        huisnummer_toevoeging, etage, naam, actief, inwoner
                    ))
                    imported += 1
                    
                except Exception as e:
                    logger.warning(f"Record {index} overslaan: {e}")
                    continue
            
            # Log upload in csv_uploads tabel
            upload_sql = """
                INSERT INTO csv_uploads 
                (filename, records_imported, records_updated, records_deleted, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(upload_sql, (filename, imported, updated, deleted, 'completed'))
            
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Migratie voltooid: {imported} records geïmporteerd")
            return imported, updated, deleted
            
        except Exception as e:
            logger.error(f"Migratie gefaald: {e}")
            if self.connection:
                self.connection.rollback()
            return 0, 0, 0
    
    def verify_migration(self) -> Dict[str, int]:
        """Verificeer dat migratie succesvol was"""
        try:
            cursor = self.connection.cursor()
            
            # Tel records
            cursor.execute("SELECT COUNT(*) FROM bedrijfsklanten")
            total_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM bedrijfsklanten WHERE actief = true")
            active_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT postcode) FROM bedrijfsklanten")
            unique_postcodes = cursor.fetchone()[0]
            
            cursor.close()
            
            stats = {
                'total_records': total_records,
                'active_records': active_records,
                'unique_postcodes': unique_postcodes
            }
            
            logger.info(f"Verificatie: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Verificatie gefaald: {e}")
            return {}
    
    def test_database_functions(self) -> bool:
        """Test database functies"""
        try:
            cursor = self.connection.cursor()
            
            # Test is_bedrijfsklant functie
            cursor.execute("SELECT is_bedrijfsklant('3136HN', '464')")
            is_blocked = cursor.fetchone()[0]
            logger.info(f"Test is_bedrijfsklant: {is_blocked}")
            
            # Test get_bedrijfsklant_info functie
            cursor.execute("SELECT * FROM get_bedrijfsklant_info('3136HN', '464')")
            info = cursor.fetchall()
            logger.info(f"Test get_bedrijfsklant_info: {info}")
            
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Database functies test gefaald: {e}")
            return False

def main():
    """Hoofdfunctie voor migratie"""
    logger.info("=== KOAD naar Database Migratie ===")
    
    # Database configuratie
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'irado',
        'user': 'irado',
        'password': 'irado123'
    }
    
    # CSV bestand pad
    csv_file = '/opt/irado/chatbot/koad.csv'
    
    if not os.path.exists(csv_file):
        logger.error(f"CSV bestand niet gevonden: {csv_file}")
        sys.exit(1)
    
    # Maak migrator
    migrator = KOADDatabaseMigrator(db_config)
    
    try:
        # Verbind met database
        if not migrator.connect():
            sys.exit(1)
        
        # Maak schema aan
        if not migrator.create_schema():
            sys.exit(1)
        
        # Laad CSV data
        df = migrator.load_csv_data(csv_file)
        if df.empty:
            logger.error("Geen CSV data geladen")
            sys.exit(1)
        
        # Verwijder bestaande data
        if not migrator.clear_existing_data():
            sys.exit(1)
        
        # Migreer data
        imported, updated, deleted = migrator.migrate_csv_to_database(df, 'koad.csv')
        
        if imported == 0:
            logger.error("Geen records geïmporteerd")
            sys.exit(1)
        
        # Verificeer migratie
        stats = migrator.verify_migration()
        
        # Test database functies
        migrator.test_database_functions()
        
        logger.info("=== Migratie succesvol voltooid ===")
        logger.info(f"Records geïmporteerd: {imported}")
        logger.info(f"Totaal records in database: {stats.get('total_records', 0)}")
        logger.info(f"Actieve records: {stats.get('active_records', 0)}")
        logger.info(f"Unieke postcodes: {stats.get('unique_postcodes', 0)}")
        
    except Exception as e:
        logger.error(f"Migratie gefaald: {e}")
        sys.exit(1)
    
    finally:
        migrator.disconnect()

if __name__ == '__main__':
    main()





