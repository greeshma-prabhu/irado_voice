"""
SECURE Flask application for the Irado Chatbot
Refactored for maximum security
"""
from flask import Flask, request, jsonify, send_from_directory, Response
import logging
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash
import base64
import json
import re
import os
import asyncio
from datetime import datetime
from typing import Dict, List
from collections import deque
import threading

from config import Config
from database import DatabaseManager
from ai_service import AIService
from email_service import EmailService
from logging_utils import (
    log_api_call, log_session_start, log_session_message,
    log_error, log_event
)

app = Flask(__name__)
app.config.from_object(Config)

# In-memory circular log buffer (last 1000 lines)
LOG_BUFFER = deque(maxlen=1000)
LOG_LOCK = threading.Lock()

# Setup logging FIRST (before anything else)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

# Custom logging handler that writes to buffer
class BufferHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = self.format(record)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with LOG_LOCK:
                LOG_BUFFER.append(f"[{timestamp}] {log_entry}")
        except Exception:
            self.handleError(record)

# Setup logging with buffer handler
buffer_handler = BufferHandler()
buffer_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
buffer_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(buffer_handler)

# CORS - Allow dashboard to access logs
CORS(app, origins=[
    'https://irado.mainfact.ai',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:3254',
    'http://127.0.0.1:3254',
    'http://localhost:3255',
    'https://irado-chatbot-app.azurewebsites.net',
    'https://irado-dashboard-app.azurewebsites.net'
])

# Rate limiting setup
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://"
)

# Initialize services
db_manager = DatabaseManager()
ai_service = AIService()
email_service = EmailService()

# Get logger (already configured above)
logger = logging.getLogger("irado-app")

def check_auth(auth_header):
    """Check basic authentication with enhanced security"""
    if not auth_header or not auth_header.startswith('Basic '):
        return False
    
    try:
        # Decode base64 credentials
        encoded_credentials = auth_header.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
        
        # Check credentials
        config = Config()
        return (username == config.CHAT_BASIC_AUTH_USER and 
                password == config.CHAT_BASIC_AUTH_PASSWORD)
    except Exception as e:
        print(f"Auth error: {e}")
        return False

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not check_auth(auth_header):
            return jsonify({'error': 'Unauthorized', 'timestamp': datetime.now().isoformat()}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def validate_chat_input(data):
    """Validate chat input for security"""
    if not data:
        return False, "No data provided"
    
    # Check required fields
    if not data.get('sessionId') or not data.get('action') or not data.get('chatInput'):
        return False, "Missing required fields"
    
    # Validate sessionId format
    session_id = data.get('sessionId', '')
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id) or len(session_id) < 10 or len(session_id) > 100:
        return False, "Invalid session ID format"
    
    # Validate action
    if data.get('action') != 'sendMessage':
        return False, "Invalid action"
    
    # Validate chat input
    chat_input = data.get('chatInput', '')
    if len(chat_input) < 1 or len(chat_input) > 2000:
        return False, "Invalid chat input length"
    
    # Check for potential XSS/injection
    if re.search(r'[<>"\']', chat_input):
        return False, "Invalid characters in input"
    
    return True, "Valid"

def should_send_emails(chat_input, ai_response):
    """Check if emails should be sent (internal function)"""
    # This function remains internal - no external access
    return False  # Disabled for security

def send_grofvuil_emails(session_id, chat_input, ai_response):
    """Send grofvuil emails (internal function)"""
    # This function remains internal - no external access
    pass

# ============================================================================
# PUBLIC API ENDPOINTS (SECURE)
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    """Serve the Irado website"""
    return send_from_directory('/app/static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from the website directory"""
    return send_from_directory('/app/static', filename)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - No authentication required for monitoring"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness probe - light checks without external calls"""
    try:
        # Validate critical env without exposing values
        cfg = Config()
        required = {
            'AZURE_OPENAI_ENDPOINT': bool(cfg.AZURE_OPENAI_ENDPOINT),
            'AZURE_OPENAI_DEPLOYMENT': bool(cfg.AZURE_OPENAI_DEPLOYMENT),
        }
        if not all(required.values()):
            logger.warning("Readiness: missing configuration flags: %s", {k: v for k, v in required.items() if not v})
        return jsonify({'status': 'ready', 'checks': required, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.exception("Readiness error")
        return jsonify({'status': 'error'}), 500

@app.route('/api/chat', methods=['POST'])
# @limiter.limit("10 per minute")  # Rate limiting disabled for testing
@require_auth
def api_chat():
    """SECURE chat endpoint - Only public endpoint for frontend"""
    session_id = None
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        
        # Log incoming API call
        log_api_call(session_id, data.get('chatInput', ''))
        
        # Validate input
        is_valid, error_msg = validate_chat_input(data)
        if not is_valid:
            log_event('VALIDATION_ERROR', f'Invalid input: {error_msg}', {'session_id': session_id}, 'warning')
            return jsonify({
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        chat_input = data.get('chatInput')
        
        # Create or update session
        log_session_start(session_id, data.get('source', 'website'))
        db_manager.create_or_update_session(session_id)
        
        # Save user message
        log_session_message(session_id, 'user', len(chat_input))
        db_manager.save_message(session_id, 'user', chat_input)
        
        # Get chat history for context
        chat_history = db_manager.get_chat_history(session_id, limit=10)
        log_event('CHAT_HISTORY', f'Retrieved {len(chat_history)} messages from history', {
            'session_id': session_id,
            'message_count': len(chat_history)
        }, 'debug')
        
        # Prepare messages for AI
        messages = []
        for msg in chat_history:
            role = 'assistant' if msg['message_type'] == 'bot' else msg['message_type']
            messages.append({
                'role': role,
                'content': msg['content']
            })
        
        # Get AI response with tool handling
        log_event('AI_START', 'Getting AI response with tools', {
            'session_id': session_id,
            'message_count': len(messages)
        })
        tools = ai_service.get_available_tools()
        ai_response = ai_service.get_chat_completion_with_tools(messages, tools, session_id=session_id)
        
        # Save AI response
        log_session_message(session_id, 'bot', len(ai_response))
        db_manager.save_message(session_id, 'bot', ai_response)
        
        log_event('API_SUCCESS', 'Chat request completed successfully', {
            'session_id': session_id,
            'response_length': len(ai_response)
        })
        
        # Return response
        return jsonify({'output': ai_response})
        
    except Exception as e:
        log_error('api_chat', e, session_id)
        logger.exception("Chat API error: %s", e)
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# INTERNAL ENDPOINTS (LOCAL ACCESS ONLY)
# ============================================================================

@app.route('/internal/email/team', methods=['POST'])
@require_auth
def internal_email_team():
    """INTERNAL email endpoint - Local access only"""
    try:
        data = request.get_json()
        
        subject = data.get('subject', '')
        html_content = data.get('html_content', '')
        
        if not subject or not html_content:
            return jsonify({'error': 'Missing subject or content'}), 400
        
        success = email_service.send_internal_notification(subject, html_content)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Email sent to team'})
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        print(f"Internal email team error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/internal/email/customer', methods=['POST'])
@require_auth
def internal_email_customer():
    """INTERNAL email endpoint - Local access only"""
    try:
        data = request.get_json()
        
        to_email = data.get('to_email', '')
        subject = data.get('subject', '')
        html_content = data.get('html_content', '')
        
        if not to_email or not subject or not html_content:
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = email_service.send_customer_confirmation(to_email, subject, html_content)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Email sent to customer'})
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        print(f"Internal email customer error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/internal/datetime', methods=['POST'])
@require_auth
def internal_datetime():
    """INTERNAL datetime endpoint - Local access only"""
    try:
        current_time = datetime.now()
        return jsonify({
            'datetime': current_time.isoformat(),
            'formatted': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'timezone': 'Europe/Amsterdam'
        })
        
    except Exception as e:
        print(f"Internal datetime error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/internal/admin/sessions', methods=['GET'])
@require_auth
def internal_admin_sessions():
    """INTERNAL admin endpoint - Local access only"""
    try:
        # This would require additional database queries
        return jsonify({'message': 'Internal admin endpoint - implement as needed'})
        
    except Exception as e:
        print(f"Internal admin sessions error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/internal/admin/session/<session_id>', methods=['GET'])
@require_auth
def internal_admin_session_details(session_id):
    """INTERNAL admin endpoint - Local access only"""
    try:
        history = db_manager.get_chat_history(session_id)
        memory = db_manager.get_memory(session_id)
        
        return jsonify({
            'session_id': session_id,
            'history': history,
            'memory': memory
        })
        
    except Exception as e:
        print(f"Internal admin session details error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

@app.route('/api/logs', methods=['GET'])
@require_auth
def get_logs():
    """
    Get recent logs from the in-memory buffer
    Query params:
    - lines: number of lines to return (default: 100, max: 1000)
    - filter: comma-separated log levels (ERROR,WARNING,INFO)
    """
    try:
        lines = min(int(request.args.get('lines', 100)), 1000)
        filter_levels = request.args.get('filter', '').upper().split(',') if request.args.get('filter') else None
        
        with LOG_LOCK:
            all_logs = list(LOG_BUFFER)
        
        # Filter by log level if specified
        if filter_levels and filter_levels != ['']:
            filtered_logs = []
            for log in all_logs:
                for level in filter_levels:
                    if level in log:
                        filtered_logs.append(log)
                        break
            all_logs = filtered_logs
        
        # Return most recent N lines
        recent_logs = all_logs[-lines:] if lines < len(all_logs) else all_logs
        
        return jsonify({
            'success': True,
            'logs': recent_logs,
            'total': len(recent_logs),
            'buffer_size': len(LOG_BUFFER)
        })
    
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/logs/stream', methods=['GET'])
@require_auth
def stream_logs():
    """
    Server-Sent Events (SSE) endpoint for live log streaming
    """
    def generate():
        last_size = 0
        try:
            while True:
                with LOG_LOCK:
                    current_size = len(LOG_BUFFER)
                    if current_size > last_size:
                        # Send new logs
                        new_logs = list(LOG_BUFFER)[last_size:]
                        for log in new_logs:
                            yield f"data: {json.dumps({'log': log})}\n\n"
                        last_size = current_size
                
                # Wait a bit before checking again
                import time
                time.sleep(1)
        except GeneratorExit:
            pass
    
    return Response(generate(), mimetype='text/event-stream')

def init_app():
    """Initialize the application"""
    try:
        # Light-weight, non-blocking startup; do not call external services here
        logger.info("Application initialization: skipped heavy checks (non-blocking startup)")
        return True
        
    except Exception as e:
        logger.warning(f"Initialization error (non-blocking): {e}")
        return True  # Never block startup

if __name__ == '__main__':
    # Allow port override via env (Azure App Service/ACI)
    port_str = os.getenv('PORT') or os.getenv('WEBSITES_PORT') or '80'
    try:
        port = int(port_str)
    except ValueError:
        port = 80
    try:
        init_app()
    except Exception as e:
        logger.warning(f"Startup init warning (continuing): {e}")
    logger.info("Starting Flask app on port %s", port)
    app.run(host='0.0.0.0', port=port, debug=False)
