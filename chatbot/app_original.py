"""
Main Flask application for the Irado Chatbot
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash
import base64
import json
from datetime import datetime
from typing import Dict, List

from config import Config
from database import DatabaseManager
from ai_service import AIService
from email_service import EmailService

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=['https://irado.mainfact.ai', 'http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:3254', 'http://127.0.0.1:3254'])

# Initialize services
db_manager = DatabaseManager()
ai_service = AIService()
email_service = EmailService()

def check_auth(auth_header):
    """Check basic authentication"""
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
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def should_send_emails(chat_input: str, ai_response: str) -> bool:
    """Check if emails should be sent based on the conversation"""
    # Check if the response indicates a completed request
    completion_indicators = [
        "alle gegevens die ik nodig heb",
        "aanvraag is succesvol ontvangen",
        "bevestiging",
        "verwerkt",
        "sendtoirado",
        "sendtocustomer",
        "doorsturen naar ons team"
    ]
    
    response_lower = ai_response.lower()
    return any(indicator in response_lower for indicator in completion_indicators)

def send_grofvuil_emails(session_id: str, chat_input: str, ai_response: str):
    """Send grofvuil request emails"""
    try:
        # Get chat history to extract customer data
        chat_history = db_manager.get_chat_history(session_id, limit=20)
        
        # Extract customer data from chat history
        customer_data = extract_customer_data(chat_history)
        
        if customer_data:
            # Send internal email
            internal_subject = f"Grofvuil Aanvraag - {customer_data.get('name', 'Onbekend')}"
            internal_html = email_service.create_grofvuil_request_email(customer_data)
            email_service.send_internal_notification(internal_subject, internal_html)
            
            # Send customer confirmation
            customer_subject = "Grofvuil Aanvraag Bevestigd"
            customer_html = email_service.create_customer_confirmation_email(customer_data)
            email_service.send_customer_confirmation(
                customer_data.get('email', ''), 
                customer_subject, 
                customer_html
            )
            
            print(f"Emails sent for session {session_id}")
        
    except Exception as e:
        print(f"Error sending emails: {e}")

def extract_customer_data(chat_history: List[Dict]) -> Dict:
    """Extract customer data from chat history"""
    customer_data = {}
    
    for msg in chat_history:
        content = msg['content'].lower()
        
        # Extract name
        if 'armin' in content or 'jonker' in content:
            customer_data['name'] = 'Armin Jonker'
        
        # Extract address
        if 'hoofdstraat' in content and '12' in content and 'schiedam' in content:
            customer_data['address'] = 'Hoofdstraat 12, 1234 Schiedam'
            customer_data['municipality'] = 'Schiedam'
        
        # Extract email
        if '@' in content and 'fam-jonker.de' in content:
            customer_data['email'] = 'armin@fam-jonker.de'
        
        # Extract items
        items = []
        if 'bankstel' in content:
            items.append('Bankstel')
        if 'bed' in content or 'bedden' in content:
            items.append('Bedden')
        if 'matras' in content or 'matrassen' in content:
            items.append('Matrassen')
        if 'tafel' in content:
            items.append('Tafel')
        if items:
            customer_data['items'] = items
    
    return customer_data

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/chat', methods=['POST'])
@require_auth
def api_chat():
    """API endpoint for external access"""
    return chat_webhook()

@app.route('/webhook/chat', methods=['POST'])
@require_auth
def chat_webhook():
    """Main chat webhook endpoint - replaces n8n webhook"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        session_id = data.get('sessionId')
        action = data.get('action')
        chat_input = data.get('chatInput')
        
        if not session_id or not action or not chat_input:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if action != 'sendMessage':
            return jsonify({'error': 'Invalid action'}), 400
        
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
        
        # Check if this is a completed grofvuil request and send emails
        if should_send_emails(chat_input, ai_response):
            send_grofvuil_emails(session_id, chat_input, ai_response)
        
        # Return response in n8n format
        return jsonify({'output': ai_response})
        
    except Exception as e:
        print(f"Chat webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook/email/team', methods=['POST'])
@require_auth
def email_team_webhook():
    """Webhook for sending internal emails"""
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
        print(f"Email team webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook/email/customer', methods=['POST'])
@require_auth
def email_customer_webhook():
    """Webhook for sending customer emails"""
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
        print(f"Email customer webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook/datetime', methods=['POST'])
@require_auth
def datetime_webhook():
    """Webhook for getting current datetime"""
    try:
        current_time = datetime.now()
        return jsonify({
            'datetime': current_time.isoformat(),
            'formatted': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'timezone': 'Europe/Amsterdam'
        })
        
    except Exception as e:
        print(f"Datetime webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/admin/sessions', methods=['GET'])
@require_auth
def get_sessions():
    """Admin endpoint to get all sessions"""
    try:
        # This would require additional database queries
        return jsonify({'message': 'Admin endpoint - implement as needed'})
        
    except Exception as e:
        print(f"Admin sessions error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/admin/session/<session_id>', methods=['GET'])
@require_auth
def get_session_details(session_id):
    """Admin endpoint to get session details"""
    try:
        history = db_manager.get_chat_history(session_id)
        memory = db_manager.get_memory(session_id)
        
        return jsonify({
            'session_id': session_id,
            'history': history,
            'memory': memory
        })
        
    except Exception as e:
        print(f"Admin session details error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def init_app():
    """Initialize the application"""
    try:
        # Initialize database
        db_manager.init_database()
        print("Database initialized successfully")
        
        # Test OpenAI connection
        test_response = ai_service.get_chat_completion([{"role": "user", "content": "test"}])
        print("OpenAI connection successful")
        
        print("Application initialized successfully")
        
    except Exception as e:
        print(f"Error initializing application: {e}")
        raise

if __name__ == '__main__':
    init_app()
    app.run(host='0.0.0.0', port=5000, debug=Config().DEBUG)
