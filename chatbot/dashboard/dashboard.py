#!/usr/bin/env python3
"""
Irado Chatbot Dashboard
Web-based dashboard for managing KOAD blacklist and system configuration
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import csv
import os
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import sys
import psycopg2
import psycopg2.extras

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database service
from database_service import BedrijfsklantenDatabaseService

# Import database config
from config import Config

# Import system prompt service
from system_prompt_service import SystemPromptService

# Import logging service (relative import)
try:
    from logging_service import get_logger, log_info, log_warning, log_error
except ImportError:
    # Fallback logging functions if service not available
    def get_logger():
        class DummyLogger:
            def log(self, *args, **kwargs): print(f"LOG: {args}")
            def get_recent_logs(self, *args, **kwargs): return []
        return DummyLogger()
    def log_info(log_type, action, message, details=None, user_ip=None):
        print(f"ℹ️ [{log_type}] {action}: {message}")
    def log_warning(log_type, action, message, details=None, user_ip=None):
        print(f"⚠️ [{log_type}] {action}: {message}")
    def log_error(log_type, action, message, details=None, user_ip=None):
        print(f"❌ [{log_type}] {action}: {message}")

app = Flask(__name__)
app.secret_key = 'irado_chatbot_dashboard_secret_key_2024'

# Configure CORS for all routes
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
})

# Configuration - paths relative to chatbot root
CHATBOT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOAD_FILE = os.path.join(CHATBOT_ROOT, 'koad.csv')
BACKUP_DIR = os.path.join(CHATBOT_ROOT, 'backups')

# Database configuration
config = Config()
APP_TIMEZONE = ZoneInfo(config.APP_TIMEZONE)

# Simple in-memory log storage for dashboard debugging
dashboard_logs = []

def now_tz():
    return datetime.now(APP_TIMEZONE)


def log_dashboard_event(action, message, level="INFO", error=None):
    """Log dashboard events for debugging"""
    import traceback

    log_entry = {
        'timestamp': now_tz().isoformat(),
        'level': level,
        'action': action,
        'message': message,
        'error': str(error) if error else None,
        'traceback': traceback.format_exc() if error else None
    }

    dashboard_logs.append(log_entry)

    # Keep only last 1000 entries
    if len(dashboard_logs) > 1000:
        dashboard_logs.pop(0)

    print(f"[{level}] {action}: {message}")
    if error:
        print(f"Error: {error}")
        traceback.print_exc()

def ensure_backup_dir():
    """Ensure backup directory exists"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def _mask_secret(secret: str | None) -> str:
    """Return a masked representation of a secret value."""
    return '*' * len(secret) if secret else 'None'


def _database_connection_params():
    """Build shared connection parameters from configuration."""
    return {
        'host': config.POSTGRES_HOST,
        'port': int(config.POSTGRES_PORT or 5432),
        'database': config.POSTGRES_DB,
        'user': config.POSTGRES_USER,
        'password': config.POSTGRES_PASSWORD,
    }


def get_db_connection():
    """Get database connection - shared with chatbot service."""
    params = _database_connection_params()
    ssl_mode = config.POSTGRES_SSL_MODE or 'require'

    missing = [key for key, value in params.items() if key != 'password' and not value]
    if not params.get('password'):
        missing.append('password')

    if missing:
        message = f"Database configuration missing required keys: {', '.join(sorted(set(missing)))}"
        log_dashboard_event("DB_CONNECT", message, "ERROR")
        raise ValueError(message)

    log_dashboard_event(
        "DB_CONNECT",
        f"Attempting connection to {params['host']}:{params['port']}/{params['database']} as {params['user']} (sslmode={ssl_mode})"
    )

    print("🔍 Database connection attempt:")
    print(f"   Host: {params['host']}")
    print(f"   Port: {params['port']}")
    print(f"   Database: {params['database']}")
    print(f"   User: {params['user']}")
    print(f"   Password: {_mask_secret(params['password'])}")
    print(f"   SSL Mode: {ssl_mode}")
    print("   Connect Timeout: 10")

    try:
        conn = psycopg2.connect(
            host=params['host'],
            port=params['port'],
            database=params['database'],
            user=params['user'],
            password=params['password'],
            sslmode=ssl_mode,
            connect_timeout=10
        )
        log_dashboard_event("DB_CONNECT", "Database connection successful with configured SSL mode")
        print("✅ Database connection successful!")
        return conn
    except Exception as e:
        log_dashboard_event("DB_CONNECT", f"Database connection failed: {str(e)}", "ERROR", e)
        print(f"❌ Database connection failed: {e}")
        raise

def create_backup():
    """Create backup of KOAD file"""
    ensure_backup_dir()
    timestamp = now_tz().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"koad_backup_{timestamp}.csv")
    
    if os.path.exists(KOAD_FILE):
        import shutil
        shutil.copy2(KOAD_FILE, backup_file)
        return backup_file
    return None

def load_koad_data():
    """Load bedrijfsklanten data from database"""
    try:
        db_service = BedrijfsklantenDatabaseService()
        # Get all bedrijfsklanten
        results = db_service.search_bedrijfsklanten("", limit=10000)  # Get all records
        return pd.DataFrame(results)
    except Exception as e:
        print(f"Error loading bedrijfsklanten data: {e}")
        return pd.DataFrame()

def save_koad_data(df):
    """Save bedrijfsklanten data to database"""
    try:
        # Convert DataFrame to list of dicts for database service
        data_list = df.to_dict('records')
        
        # Use database service to upload data
        db_service = BedrijfsklantenDatabaseService()
        result = db_service.upload_csv_data(data_list, 'dashboard_update.csv')
        
        print(f"Database update completed: {result}")
        return True
    except Exception as e:
        print(f"Error saving bedrijfsklanten data: {e}")
        return False

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'version': '2.2.0',
            'timestamp': now_tz().isoformat(),
            'environment': os.getenv('FLASK_ENV', 'production'),
            'database_configured': os.getenv('POSTGRES_HOST') is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/')
def dashboard():
    """Main dashboard page"""
    chatbot_url = os.getenv('CHATBOT_URL', 'https://irado-chatbot-app.azurewebsites.net')
    return render_template('dashboard.html', chatbot_url=chatbot_url)


@app.route('/api/config')
def api_config():
    """Expose minimal runtime config needed by the dashboard frontend."""
    return jsonify({
        'success': True,
        'chatbot_url': os.getenv('CHATBOT_URL', 'https://irado-chatbot-app.azurewebsites.net'),
        'version': '2.2.0'
    })

@app.route('/api/koad')
def api_koad_list():
    """API endpoint to get bedrijfsklanten list"""
    try:
        db_service = BedrijfsklantenDatabaseService()
        results = db_service.search_bedrijfsklanten("", limit=10000)
        
        # Clean data before JSON serialization
        clean_koad_list = []
        for item in results:
            clean_item = {}
            for key, value in item.items():
                if pd.isna(value) or (isinstance(value, float) and str(value) == 'nan'):
                    clean_item[key] = None
                else:
                    clean_item[key] = value
            clean_koad_list.append(clean_item)
        
        return jsonify({
            'success': True,
            'data': clean_koad_list,
            'total': len(clean_koad_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/search')
def api_koad_search():
    """API endpoint to search bedrijfsklanten list"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': True, 'data': [], 'total': 0})
        
        db_service = BedrijfsklantenDatabaseService()
        results = db_service.search_bedrijfsklanten(query, limit=1000)
        
        # Clean data before JSON serialization
        clean_koad_list = []
        for item in results:
            clean_item = {}
            for key, value in item.items():
                if pd.isna(value) or (isinstance(value, float) and str(value) == 'nan'):
                    clean_item[key] = None
                else:
                    clean_item[key] = value
            clean_koad_list.append(clean_item)
        
        return jsonify({
            'success': True,
            'data': clean_koad_list,
            'total': len(clean_koad_list),
            'query': query
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/add', methods=['POST'])
def api_koad_add():
    """API endpoint to add new KOAD entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['KOAD-str', 'KOAD-pc', 'KOAD-huisnr']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Field {field} is required'
                }), 400
        
        # Load existing data
        df = load_koad_data()
        
        # Check if entry already exists
        postcode = data['KOAD-pc']
        huisnummer = data['KOAD-huisnr']
        existing = df[(df['KOAD-pc'] == postcode) & (df['KOAD-huisnr'] == huisnummer)]
        
        if not existing.empty:
            return jsonify({
                'success': False,
                'error': 'Entry already exists with this postcode and house number'
            }), 400
        
        # Add new entry
        new_entry = {
            'KOAD-nummer': data.get('KOAD-nummer', ''),
            'KOAD-str': data['KOAD-str'],
            'KOAD-pc': data['KOAD-pc'],
            'KOAD-huisaand': data.get('KOAD-huisaand', ''),
            'KOAD-huisnr': data['KOAD-huisnr'],
            'KOAD-etage': data.get('KOAD-etage', ''),
            'KOAD-naam': data.get('KOAD-naam', ''),
            'KOAD-actief': data.get('KOAD-actief', '1'),
            'KOAD-inwoner': data.get('KOAD-inwoner', '1')
        }
        
        # Add to dataframe
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        
        # Save
        if save_koad_data(df):
            return jsonify({
                'success': True,
                'message': 'Entry added successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/update', methods=['POST'])
def api_koad_update():
    """API endpoint to update KOAD entry"""
    try:
        data = request.get_json()
        entry_id = data.get('id')
        
        if not entry_id:
            return jsonify({
                'success': False,
                'error': 'Entry ID is required'
            }), 400
        
        # Load existing data
        df = load_koad_data()
        
        # Update entry
        for key, value in data.items():
            if key != 'id' and key in df.columns:
                df.loc[df.index == entry_id, key] = value
        
        # Save
        if save_koad_data(df):
            return jsonify({
                'success': True,
                'message': 'Entry updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/delete', methods=['POST'])
def api_koad_delete():
    """API endpoint to delete KOAD entry"""
    try:
        data = request.get_json()
        entry_id = data.get('id')
        
        if not entry_id:
            return jsonify({
                'success': False,
                'error': 'Entry ID is required'
            }), 400
        
        # Load existing data
        df = load_koad_data()
        
        # Delete entry
        df = df.drop(df.index[entry_id])
        df = df.reset_index(drop=True)
        
        # Save
        if save_koad_data(df):
            return jsonify({
                'success': True,
                'message': 'Entry deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/upload', methods=['POST'])
def api_koad_upload():
    """API endpoint to upload new KOAD CSV file"""
    user_ip = request.remote_addr

    try:
        log_dashboard_event("KOAD_UPLOAD", "Starting KOAD CSV upload")
        log_info('CSV_UPLOAD', 'upload_start', 'CSV upload initiated', 
                {'ip': user_ip}, user_ip)
        
        if 'file' not in request.files:
            log_warning('CSV_UPLOAD', 'no_file', 'No file in request', None, user_ip)
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            log_warning('CSV_UPLOAD', 'empty_filename', 'Empty filename', None, user_ip)
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not file.filename.endswith('.csv'):
            log_warning('CSV_UPLOAD', 'invalid_type', f'Invalid file type: {file.filename}', None, user_ip)
            return jsonify({
                'success': False,
                'error': 'File must be a CSV file'
            }), 400
        
        log_info('CSV_UPLOAD', 'reading_file', f'Reading CSV: {file.filename}', None, user_ip)
        
        # Read the uploaded file
        df = pd.read_csv(file)
        
        log_info('CSV_UPLOAD', 'file_read', f'CSV read successfully', {
            'filename': file.filename,
            'rows': len(df),
            'columns': list(df.columns)
        }, user_ip)
        
        # Validate required columns (simplified for basic CSV)
        required_columns = ['KOAD-str', 'KOAD-pc', 'KOAD-huisnr']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            log_error('CSV_UPLOAD', 'missing_columns', f'Missing required columns', {
                'missing': missing_columns,
                'found': list(df.columns)
            }, user_ip)
            return jsonify({
                'success': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400
        
        # Convert to list of dicts for database service
        data_list = df.to_dict('records')
        
        log_info('CSV_UPLOAD', 'uploading_to_db', f'Uploading {len(data_list)} records to database', {
            'filename': file.filename,
            'record_count': len(data_list),
            'estimated_batches': (len(data_list) // 1000) + 1,
            'batch_size': 1000
        }, user_ip)
        
        # Use database service to upload data (overschrijft bestaande data)
        db_service = BedrijfsklantenDatabaseService()
        
        print(f"📤 Starting CSV upload: {file.filename} ({len(data_list)} records)")
        result = db_service.upload_csv_data(data_list, file.filename)
        print(f"✅ Upload complete: {result}")
        
        if result['imported'] > 0:
            log_info('CSV_UPLOAD', 'upload_success', f'CSV uploaded successfully', {
                'filename': file.filename,
                'imported': result['imported'],
                'deleted': result['deleted']
            }, user_ip)
            
            return jsonify({
                'success': True,
                'message': f'CSV uploaded successfully. {result["imported"]} records imported, {result["deleted"]} old records removed.',
                'total': result['imported']
            })
        else:
            log_error('CSV_UPLOAD', 'no_records_imported', 'No records were imported', {
                'filename': file.filename,
                'result': result
            }, user_ip)
            
            return jsonify({
                'success': False,
                'error': 'Failed to import any records'
            }), 400
            
    except Exception as e:
        log_error('CSV_UPLOAD', 'upload_failed', f'CSV upload failed: {str(e)}', {
            'error': str(e),
            'type': type(e).__name__
        }, user_ip)
        
        print(f"❌ Upload API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint to get system statistics"""
    try:
        # Use database service for accurate stats (not limited to 10k)
        db_service = BedrijfsklantenDatabaseService()
        stats = db_service.get_bedrijfsklanten_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        print(f"❌ Stats API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Chat History API endpoints
@app.route('/api/chat/sessions')
def api_chat_sessions():
    """API endpoint to get chat sessions"""
    try:
        log_dashboard_event("CHAT_SESSIONS", "Getting chat sessions")
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get sessions with message counts - use correct column names from chatbot schema
        cursor.execute("""
            SELECT 
                s.session_id,
                s.created_at,
                s.last_activity,
                COUNT(m.id) as message_count,
                MAX(m.timestamp) as last_message_time
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON s.session_id = m.session_id
            GROUP BY s.session_id, s.created_at, s.last_activity
            ORDER BY COALESCE(s.last_activity, s.created_at) DESC
            LIMIT 100
        """)
        
        sessions = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert sessions to dict and handle timestamp serialization
        session_data = []
        for session in sessions:
            session_dict = dict(session)
            # Convert timestamps to ISO format for JSON serialization
            for key, value in session_dict.items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    session_dict[key] = value.isoformat()
                elif value is None:
                    session_dict[key] = None
            session_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': session_data,
            'total': len(session_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/sessions/<session_id>')
def api_chat_session_detail(session_id):
    """API endpoint to get chat session details"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get session info
        cursor.execute("""
            SELECT session_id, created_at, last_activity
            FROM chat_sessions 
            WHERE session_id = %s
        """, (session_id,))
        
        session = cursor.fetchone()
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Get messages for this session - use correct column names from chatbot schema
        cursor.execute("""
            SELECT message_type, content, timestamp, metadata
            FROM chat_messages 
            WHERE session_id = %s 
            ORDER BY timestamp ASC
        """, (session_id,))
        
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'session': dict(session),
                'messages': [dict(msg) for msg in messages]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/search')
def api_chat_search():
    """API endpoint to search chat messages"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': True, 'data': [], 'total': 0})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Search in messages - use correct column names from chatbot schema
        cursor.execute("""
            SELECT 
                m.session_id,
                m.message_type,
                m.content,
                m.timestamp,
                s.created_at as session_created
            FROM chat_messages m
            JOIN chat_sessions s ON m.session_id = s.session_id
            WHERE m.content ILIKE %s
            ORDER BY m.timestamp DESC
            LIMIT 50
        """, (f'%{query}%',))
        
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Clean data before JSON serialization
        clean_messages = []
        for msg in messages:
            clean_msg = {}
            for key, value in dict(msg).items():
                if value is None or (isinstance(value, float) and str(value) == 'nan'):
                    clean_msg[key] = None
                else:
                    clean_msg[key] = value
            clean_messages.append(clean_msg)
        
        return jsonify({
            'success': True,
            'data': clean_messages,
            'total': len(clean_messages),
            'query': query
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/routes')
def api_dashboard_routes():
    """API endpoint to list all available routes"""
    try:
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })

        log_dashboard_event("ROUTES_API", f"Returning {len(routes)} routes")

        return jsonify({
            'success': True,
            'routes': routes,
            'count': len(routes)
        })
    except Exception as e:
        log_dashboard_event("ROUTES_API", f"Error getting routes: {str(e)}", "ERROR", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/env-check')
def api_env_check():
    """API endpoint to check environment variables and configuration"""
    try:
        log_dashboard_event("ENV_CHECK", "Checking environment variables and configuration")

        # Check all environment variables
        env_vars = {}
        db_vars = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD',
                  'BEDRIJFSKLANTEN_DB_HOST', 'BEDRIJFSKLANTEN_DB_PORT', 'BEDRIJFSKLANTEN_DB_NAME',
                  'BEDRIJFSKLANTEN_DB_USER', 'BEDRIJFSKLANTEN_DB_PASSWORD']

        for var in db_vars:
            value = os.getenv(var)
            if var.endswith('PASSWORD'):
                env_vars[var] = _mask_secret(value)
            else:
                env_vars[var] = value

        # Check if we can import required modules
        imports_ok = {}
        try:
            import psycopg2
            imports_ok['psycopg2'] = True
        except ImportError as e:
            imports_ok['psycopg2'] = f"Failed: {e}"

        # Check database connectivity without connecting
        connectivity_tests = []

        # Test 1: DNS resolution
        try:
            import socket
            host = config.POSTGRES_HOST or os.getenv('POSTGRES_HOST', 'irado-chat-db.postgres.database.azure.com')
            ip = socket.gethostbyname(host)
            connectivity_tests.append({
                'test': 'dns_resolution',
                'success': True,
                'result': f"{host} -> {ip}"
            })
        except Exception as e:
            connectivity_tests.append({
                'test': 'dns_resolution',
                'success': False,
                'error': str(e)
            })

        # Test 2: Port connectivity (without connecting to database)
        try:
            import socket
            host = config.POSTGRES_HOST or os.getenv('POSTGRES_HOST', 'irado-chat-db.postgres.database.azure.com')
            port = int(config.POSTGRES_PORT or os.getenv('POSTGRES_PORT', '5432'))

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                connectivity_tests.append({
                    'test': 'port_connectivity',
                    'success': True,
                    'result': f"Port {port} is open on {host}"
                })
            else:
                connectivity_tests.append({
                    'test': 'port_connectivity',
                    'success': False,
                    'result': f"Port {port} is closed or filtered on {host} (error code: {result})"
                })
        except Exception as e:
            connectivity_tests.append({
                'test': 'port_connectivity',
                'success': False,
                'error': str(e)
            })

        return jsonify({
            'success': True,
            'environment_variables': env_vars,
            'imports': imports_ok,
            'connectivity_tests': connectivity_tests,
            'current_time': now_tz().isoformat(),
            'app_config': {
                'python_version': sys.version,
                'working_directory': os.getcwd(),
                'files_in_directory': len(os.listdir('.')) if os.path.exists('.') else 0,
                'resolved_config': {
                    'host': config.POSTGRES_HOST,
                    'port': config.POSTGRES_PORT,
                    'database': config.POSTGRES_DB,
                    'user': config.POSTGRES_USER,
                    'password_set': bool(config.POSTGRES_PASSWORD),
                    'ssl_mode': config.POSTGRES_SSL_MODE
                }
            }
        })
    except Exception as e:
        log_dashboard_event("ENV_CHECK", f"Environment check error: {str(e)}", "ERROR", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/db-info')
def api_db_info():
    """API endpoint to get database configuration information"""
    try:
        log_dashboard_event("DB_INFO", "Getting database configuration info")

        # Get current environment variables
        db_config = {
            'host': config.POSTGRES_HOST or os.getenv('POSTGRES_HOST'),
            'port': config.POSTGRES_PORT or os.getenv('POSTGRES_PORT'),
            'database': config.POSTGRES_DB or os.getenv('POSTGRES_DB'),
            'user': config.POSTGRES_USER or os.getenv('POSTGRES_USER'),
            'password_set': bool(config.POSTGRES_PASSWORD or os.getenv('POSTGRES_PASSWORD')),
            'password_length': len(config.POSTGRES_PASSWORD or os.getenv('POSTGRES_PASSWORD', '')) if (config.POSTGRES_PASSWORD or os.getenv('POSTGRES_PASSWORD')) else 0,
            'ssl_mode': config.POSTGRES_SSL_MODE
        }

        # Check if psycopg2 is available
        psycopg2_available = False
        psycopg2_version = None
        try:
            import psycopg2
            psycopg2_available = True
            psycopg2_version = psycopg2.__version__
        except ImportError:
            pass

        # Try to get connection info without connecting
        connection_info = {}
        try:
            import socket
            host = db_config['host']
            port = int(db_config['port'])

            # DNS lookup
            try:
                ip = socket.gethostbyname(host)
                connection_info['dns_lookup'] = f"{host} -> {ip}"
            except Exception as e:
                connection_info['dns_lookup'] = f"Failed: {e}"

            # Port check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                connection_info['port_check'] = f"Port {port} is open"
            else:
                connection_info['port_check'] = f"Port {port} is closed (error: {result})"

        except Exception as e:
            connection_info['socket_check'] = f"Failed: {e}"

        return jsonify({
            'success': True,
            'database_config': db_config,
            'psycopg2_available': psycopg2_available,
            'psycopg2_version': psycopg2_version,
            'connection_info': connection_info,
            'recommendations': [
                "Check if the database server is running",
                "Verify the username and password are correct",
                "Ensure the IP address is whitelisted in pg_hba.conf",
                "Check if SSL is required or disabled",
                "Verify the database name exists"
            ]
        })
    except Exception as e:
        log_dashboard_event("DB_INFO", f"Database info error: {str(e)}", "ERROR", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/test-db')
def api_test_db():
    """API endpoint to test database connection"""
    try:
        log_dashboard_event("TEST_DB", "Testing database connection")

        test_results = []
        params = _database_connection_params()
        ssl_mode = config.POSTGRES_SSL_MODE or 'require'

        # Test 1: Standard connection using configured parameters
        try:
            conn = psycopg2.connect(
                host=params['host'],
                port=params['port'],
                database=params['database'],
                user=params['user'],
                password=params['password'],
                sslmode=ssl_mode,
                connect_timeout=5
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS connectivity_test")
            result = cursor.fetchone()
            conn.close()
            test_results.append({
                'method': 'configured_params',
                'success': True,
                'result': result[0] if result else None
            })
        except Exception as e:
            test_results.append({
                'method': 'configured_params',
                'success': False,
                'error': str(e)
            })

        # Test 2: Connection via DATABASE_URL if available
        if config.DATABASE_URL:
            try:
                conn = psycopg2.connect(config.DATABASE_URL, connect_timeout=5)
                cursor = conn.cursor()
                cursor.execute("SELECT current_database()")
                result = cursor.fetchone()
                conn.close()
                test_results.append({
                    'method': 'database_url',
                    'success': True,
                    'result': result[0] if result else None
                })
            except Exception as e:
                test_results.append({
                    'method': 'database_url',
                    'success': False,
                    'error': str(e)
                })

        log_dashboard_event("TEST_DB", "Database tests completed")

        return jsonify({
            'success': True,
            'test_results': test_results,
            'environment_variables': {
                'POSTGRES_HOST': params['host'],
                'POSTGRES_PORT': params['port'],
                'POSTGRES_DB': params['database'],
                'POSTGRES_USER': params['user'],
                'POSTGRES_PASSWORD': _mask_secret(params['password']),
                'POSTGRES_SSL_MODE': ssl_mode,
                'DATABASE_URL_present': bool(config.DATABASE_URL)
            }
        })
    except Exception as e:
        log_dashboard_event("TEST_DB", f"Database test failed: {str(e)}", "ERROR", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/logs')
def api_dashboard_logs():
    """API endpoint to get dashboard logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        log_type = request.args.get('type', None)

        log_dashboard_event("LOGS_API", f"Requesting {limit} logs of type {log_type}")

        # Return our in-memory logs
        logs_to_return = dashboard_logs[-limit:] if limit > 0 else dashboard_logs

        # Filter by type if specified
        if log_type:
            logs_to_return = [log for log in logs_to_return if log.get('action') == log_type]

        return jsonify({
            'success': True,
            'logs': logs_to_return,
            'count': len(logs_to_return)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/stats')
def api_chat_stats():
    """API endpoint to get chat statistics"""
    try:
        log_dashboard_event("CHAT_STATS", "Getting chat statistics")
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get chat statistics
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT s.session_id) as total_sessions,
                COUNT(m.id) as total_messages,
                COUNT(CASE WHEN m.message_type = 'user' THEN 1 END) as user_messages,
                COUNT(CASE WHEN m.message_type = 'bot' THEN 1 END) as bot_messages,
                COUNT(CASE WHEN s.created_at >= CURRENT_DATE THEN 1 END) as sessions_today,
                COUNT(CASE WHEN s.created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as sessions_week
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON s.session_id = m.session_id
        """)
        
        stats = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': dict(stats)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# System Prompt API endpoints
@app.route('/api/system-prompt')
def api_system_prompt_list():
    """API endpoint to get all system prompts"""
    try:
        log_dashboard_event("SYSTEM_PROMPT_LIST", "Getting all system prompts")
        prompt_service = SystemPromptService()
        prompts = prompt_service.get_all_prompts()
        
        # Handle timestamp serialization
        for prompt in prompts:
            for key, value in prompt.items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    prompt[key] = value.isoformat()
                elif value is None:
                    prompt[key] = None
        
        return jsonify({
            'success': True,
            'data': prompts
        })
    except Exception as e:
        log_dashboard_event("SYSTEM_PROMPT_LIST_ERROR", f"Error getting system prompts: {str(e)}", "ERROR")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system-prompt/active')
def api_system_prompt_active():
    """API endpoint to get the currently active system prompt"""
    try:
        log_dashboard_event("SYSTEM_PROMPT_ACTIVE", "Getting active system prompt")
        prompt_service = SystemPromptService()
        # Use get_active_prompt_full() to get the complete object with content
        active_prompt = prompt_service.get_active_prompt_full()
        
        if active_prompt:
            # Handle timestamp serialization
            for key, value in active_prompt.items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    active_prompt[key] = value.isoformat()
                elif value is None:
                    active_prompt[key] = None
            
            return jsonify({
                'success': True,
                'data': active_prompt
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No active system prompt found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system-prompt/create', methods=['POST'])
def api_system_prompt_create():
    """API endpoint to create a new system prompt"""
    try:
        data = request.get_json()
        
        # Accept both 'content' and 'prompt_content' for compatibility
        content = data.get('content') or data.get('prompt_content')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'content is required'
            }), 400
        
        prompt_service = SystemPromptService()
        
        prompt_id = prompt_service.create_prompt(
            content=content,
            version=data.get('version', 'v1.0'),
            created_by=data.get('created_by', 'dashboard'),
            notes=data.get('notes', '')
        )
        
        return jsonify({
            'success': True,
            'message': 'System prompt created successfully',
            'prompt_id': prompt_id
        })
    except Exception as e:
        print(f"❌ Create prompt error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system-prompt/update/<int:prompt_id>', methods=['POST'])
def api_system_prompt_update(prompt_id):
    """API endpoint to update an existing system prompt"""
    try:
        data = request.get_json()
        
        # Accept both 'content' and 'prompt_content' for compatibility
        content = data.get('content') or data.get('prompt_content')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'content is required'
            }), 400
        
        prompt_service = SystemPromptService()
        
        prompt_service.update_prompt(
            prompt_id=prompt_id,
            content=content,
            version=data.get('version'),
            notes=data.get('notes')
        )
        
        return jsonify({
            'success': True,
            'message': 'System prompt updated successfully'
        })
    except Exception as e:
        print(f"❌ Update prompt error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system-prompt/activate/<int:prompt_id>', methods=['POST'])
def api_system_prompt_activate(prompt_id):
    """API endpoint to activate a system prompt"""
    try:
        prompt_service = SystemPromptService()
        prompt_service.activate_prompt(prompt_id)
        
        return jsonify({
            'success': True,
            'message': 'System prompt activated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system-prompt/delete/<int:prompt_id>', methods=['POST'])
def api_system_prompt_delete(prompt_id):
    """API endpoint to delete a system prompt"""
    try:
        prompt_service = SystemPromptService()
        prompt_service.delete_prompt(prompt_id)
        
        return jsonify({
            'success': True,
            'message': 'System prompt deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Ensure backup directory exists
    ensure_backup_dir()
    
    # Run the dashboard on port 3255
    app.run(host='0.0.0.0', port=3255, debug=False)
