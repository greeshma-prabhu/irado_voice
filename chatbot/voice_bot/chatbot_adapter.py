"""
Chatbot API Adapter - Aligned with Existing Project

Uses existing Config class and logging patterns.
"""

import requests
import base64
import uuid
from typing import Optional, Dict, Any

# Use existing project imports
from config import Config
from logging_utils import log_event, log_error

# Use existing logger
import logging
logger = logging.getLogger('irado-chatbot')


class ChatbotAdapter:
    """
    Adapter to call existing Irado chatbot API.
    
    Aligned with existing project patterns:
    - Uses existing Config class
    - Uses existing logging_utils
    - Follows existing error handling patterns
    """
    
    def __init__(self):
        config = Config()
        self.api_url = getattr(config, 'CHATBOT_API_URL', 'https://irado-chatbot-app.azurewebsites.net/api/chat')
        self.auth_username = config.CHAT_BASIC_AUTH_USER
        self.auth_password = config.CHAT_BASIC_AUTH_PASSWORD
    
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header"""
        if not self.auth_username or not self.auth_password:
            raise ValueError("Basic Auth credentials not configured")
        
        credentials = f"{self.auth_username}:{self.auth_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def send_message(
        self,
        message: str,
        language: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send message to existing chatbot API.
        
        Uses existing logging patterns and error handling.
        """
        
        # Generate session ID if not provided
        if not session_id:
            session_id = self.create_session()
        
        # Validate message (API requires 1-2000 chars, no HTML/XSS chars)
        if len(message) < 1 or len(message) > 2000:
            logger.warning(f"Message length out of range: {len(message)}")
            message = message[:2000]  # Truncate if too long
        
        # Remove invalid characters (API rejects < > " ')
        message = message.replace('<', '').replace('>', '').replace('"', '').replace("'", '')
        
        # Build request payload (exact format from app.py)
        payload = {
            'sessionId': session_id,
            'action': 'sendMessage',  # Required, must be exactly this
            'chatInput': message,
            'source': 'voice'  # Identify as voice call
        }
        
        # Build headers with Basic Auth
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self._get_auth_header()
        }
        
        try:
            # Use existing logging pattern
            log_event('VOICE_API_CALL', f'Calling chatbot API for session {session_id}', {
                'session_id': session_id,
                'message_length': len(message)
            })
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract response from API format
            output = result.get('output', {})
            response_text = output.get('text', '')
            detected_language = output.get('language', language)
            
            if not response_text:
                response_text = "I'm sorry, I didn't understand that. Could you please repeat?"
            
            # Use existing logging pattern
            log_event('VOICE_API_SUCCESS', 'Chatbot API response received', {
                'session_id': session_id,
                'response_length': len(response_text),
                'language': detected_language
            })
            
            return {
                'response': response_text,
                'language': detected_language,
                'session_id': session_id,
                'success': True,
                'full_output': output
            }
            
        except requests.exceptions.HTTPError as e:
            # Use existing error logging pattern
            error_msg = f"HTTP {e.response.status_code if e.response else 'Unknown'}: {str(e)}"
            log_error('chatbot_adapter.send_message', e, session_id)
            return {
                'response': None,
                'error': error_msg,
                'success': False
            }
        except Exception as e:
            # Use existing error logging pattern
            log_error('chatbot_adapter.send_message', e, session_id)
            return {
                'response': None,
                'error': str(e),
                'success': False
            }
    
    def create_session(self) -> str:
        """Create a new chat session ID"""
        import time
        timestamp = int(time.time())
        random_id = str(uuid.uuid4())[:8]
        session_id = f"voice_call_{timestamp}_{random_id}"
        
        log_event('VOICE_SESSION_CREATED', f'Created voice session: {session_id}', {
            'session_id': session_id
        })
        
        return session_id
    
    def get_response_text(self, api_response: Dict[str, Any]) -> str:
        """Extract response text from API response"""
        response_text = api_response.get('response', '')
        
        if not response_text:
            # Fallback message based on language
            language = api_response.get('language', 'en')
            if language == 'nl':
                response_text = "Sorry, ik begrijp het niet. Kunt u het herhalen?"
            elif language == 'ar':
                response_text = "عذراً، لم أفهم. هل يمكنك التكرار؟"
            else:
                response_text = "I'm sorry, I didn't understand that. Could you please repeat?"
        
        return response_text

