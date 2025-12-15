"""
Enhanced logging utilities for Irado Chatbot
Provides detailed structured logging for debugging and monitoring
"""
import logging
import json
from datetime import datetime
from functools import wraps
from zoneinfo import ZoneInfo
from typing import Any, Dict
from config import Config

# Setup logger
logger = logging.getLogger('irado-chatbot')
APP_TIMEZONE = ZoneInfo(Config().APP_TIMEZONE)


def now_tz():
    return datetime.now(APP_TIMEZONE)

def _json_default(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def log_event(event_type: str, message: str, data: Dict[str, Any] = None, level: str = 'info'):
    """
    Log an event with structured data
    
    Args:
        event_type: Type of event (API_CALL, TOOL_CALL, EMAIL, DATABASE, etc.)
        message: Human readable message
        data: Additional structured data
        level: Log level (debug, info, warning, error)
    """
    timestamp = now_tz().isoformat()
    
    log_data = {
        'timestamp': timestamp,
        'event_type': event_type,
        'message': message
    }
    
    if data:
        log_data['data'] = data
    
    # Format as structured log
    log_message = f"[{event_type}] {message}"
    if data:
        # Add key details inline
        if 'session_id' in data:
            log_message += f" | Session: {data['session_id']}"
        if 'tool_name' in data:
            log_message += f" | Tool: {data['tool_name']}"
        if 'status' in data:
            log_message += f" | Status: {data['status']}"
    
    # Log at appropriate level
    log_fn = getattr(logger, level.lower(), logger.info)
    log_fn(log_message)

    # Always emit structured JSON so the dashboard log viewer sees full context
    logger.log(
        getattr(logging, level.upper(), logging.INFO),
        json.dumps(log_data, default=_json_default)
    )

def log_api_call(session_id: str, user_message: str):
    """Log incoming API call"""
    log_event('API_CALL', 'Received chat message', {
        'session_id': session_id,
        'message_length': len(user_message),
        'message_preview': user_message[:100]
    })

def log_ai_request(session_id: str, model: str, message_count: int, has_tools: bool):
    """Log AI request details"""
    log_event('AI_REQUEST', 'Sending request to OpenAI', {
        'session_id': session_id,
        'model': model,
        'message_count': message_count,
        'has_tools': has_tools
    })

def log_ai_response(session_id: str, response_length: int, has_tool_calls: bool, tokens: dict = None):
    """Log AI response details"""
    data = {
        'session_id': session_id,
        'response_length': response_length,
        'has_tool_calls': has_tool_calls
    }
    if tokens:
        data.update(tokens)
    log_event('AI_RESPONSE', 'Received response from OpenAI', data)

def log_tool_call(session_id: str, tool_name: str, arguments: dict, status: str = 'started'):
    """Log tool/function call"""
    log_event('TOOL_CALL', f'Tool call: {tool_name}', {
        'session_id': session_id,
        'tool_name': tool_name,
        'arguments': arguments,
        'status': status
    })

def log_tool_result(session_id: str, tool_name: str, success: bool, result: any = None, error: str = None):
    """Log tool call result"""
    data = {
        'session_id': session_id,
        'tool_name': tool_name,
        'success': success
    }
    if result:
        data['result'] = str(result)[:200]  # Truncate long results
    if error:
        data['error'] = error
    
    level = 'info' if success else 'error'
    log_event('TOOL_RESULT', f'Tool {tool_name} {"succeeded" if success else "failed"}', data, level)

def log_email_attempt(session_id: str, email_type: str, recipient: str, has_data: bool):
    """Log email sending attempt"""
    log_event('EMAIL_ATTEMPT', f'Attempting to send {email_type} email', {
        'session_id': session_id,
        'email_type': email_type,
        'recipient': recipient,
        'has_data': has_data
    })

def log_email_result(session_id: str, email_type: str, success: bool, error: str = None):
    """Log email sending result"""
    level = 'info' if success else 'error'
    data = {
        'session_id': session_id,
        'email_type': email_type,
        'success': success
    }
    if error:
        data['error'] = error
    
    log_event('EMAIL_RESULT', f'Email {email_type} {"sent successfully" if success else "failed"}', data, level)

def log_smtp_details(host: str, port: int, user: str, has_password: bool):
    """Log SMTP configuration (without sensitive data)"""
    log_event('SMTP_CONFIG', 'SMTP configuration', {
        'host': host,
        'port': port,
        'user': user,
        'has_password': has_password,
        'has_tls': port in [587, 465]
    }, 'debug')

def log_database_operation(operation: str, table: str, success: bool, row_count: int = None, error: str = None):
    """Log database operations"""
    level = 'info' if success else 'error'
    data = {
        'operation': operation,
        'table': table,
        'success': success
    }
    if row_count is not None:
        data['row_count'] = row_count
    if error:
        data['error'] = error
    
    log_event('DATABASE', f'Database {operation} on {table}', data, level)

def log_validation(validation_type: str, input_data: str, result: bool, details: str = None):
    """Log validation attempts"""
    log_event('VALIDATION', f'{validation_type} validation', {
        'validation_type': validation_type,
        'input': input_data[:100],
        'valid': result,
        'details': details
    })

def log_error(context: str, error: Exception, session_id: str = None):
    """Log errors with context"""
    data = {
        'context': context,
        'error_type': type(error).__name__,
        'error_message': str(error)
    }
    if session_id:
        data['session_id'] = session_id
    
    log_event('ERROR', f'Error in {context}: {str(error)}', data, 'error')
    logger.exception(f"Full traceback for {context}:")

def log_session_start(session_id: str, source: str = None):
    """Log new session start"""
    log_event('SESSION_START', 'New chat session started', {
        'session_id': session_id,
        'source': source or 'unknown'
    })

def log_session_message(session_id: str, message_type: str, content_length: int):
    """Log message saved to session"""
    log_event('SESSION_MESSAGE', f'Saved {message_type} message', {
        'session_id': session_id,
        'message_type': message_type,
        'content_length': content_length
    }, 'debug')

# Decorator for function logging
def log_function_call(func):
    """Decorator to log function entry/exit"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"→ Entering {func_name}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"← Exiting {func_name} (success)")
            return result
        except Exception as e:
            logger.error(f"← Exiting {func_name} (error: {e})")
            raise
    return wrapper
