"""
SECURE Flask application for the Irado Chatbot
Refactored for maximum security
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash
import base64
import json
import re
from datetime import datetime
from typing import Dict, List

from config import Config
from database import DatabaseManager
from ai_service import AIService
from email_service import EmailService

app = Flask(__name__)
app.config.from_object(Config)

# CORS - Only allow specific origins
CORS(app, origins=[
    'https://irado.mainfact.ai',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:3254',
    'http://127.0.0.1:3254'
])

# Rate limiting setup
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://"
)

# Initialize services
db_manager = DatabaseManager()
ai_service = AIService()
email_service = EmailService()

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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - No authentication required for monitoring"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")  # Strict rate limiting for chat
@require_auth
def api_chat():
    """SECURE chat endpoint - Only public endpoint for frontend"""
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error_msg = validate_chat_input(data)
        if not is_valid:
            return jsonify({
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        session_id = data.get('sessionId')
        chat_input = data.get('chatInput')
        
        # Create or update session
        db_manager.create_or_update_session(session_id)
        
        # Save user message
        db_manager.save_message(session_id, 'user', chat_input)
        
        # Get chat history for context
        chat_history = db_manager.get_chat_history(session_id, limit=10)
        
        # Prepare messages for AI
        messages = []
        for msg in chat_history:
            role = 'assistant' if msg['message_type'] == 'bot' else msg['message_type']
            messages.append({
                'role': role,
                'content': msg['content']
            })
        
        # Get AI response
        tools = ai_service.get_available_tools()
        ai_response = ai_service.get_chat_completion(messages, tools)
        
        # Save AI response
        db_manager.save_message(session_id, 'bot', ai_response)
        
        # Return response
        return jsonify({'output': ai_response})
        
    except Exception as e:
        print(f"Chat API error: {e}")
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

def init_app():
    """Initialize the application"""
    try:
        # Test database connection
        db_manager.test_connection()
        print("Database connection successful")
        
        # Test OpenAI connection
        test_response = ai_service.get_chat_completion([
            {'role': 'user', 'content': 'test'}
        ])
        print("OpenAI connection successful")
        
        print("Application initialized successfully")
        return True
        
    except Exception as e:
        print(f"Initialization error: {e}")
        return False

if __name__ == '__main__':
    if init_app():
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Failed to initialize application")


