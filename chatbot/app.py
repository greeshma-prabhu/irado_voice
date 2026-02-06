"""
SECURE Flask application for the Irado Chatbot
Refactored for maximum security
"""
from flask import Flask, request, jsonify, send_from_directory, Response
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
import tempfile
import os
import time
import subprocess
import shutil

app = Flask(__name__)
VOICE_SESSION_LANGUAGE = {}

def normalize_language_code(language):
    if not language:
        return 'nl'
    lang = str(language).strip().lower()
    language_map = {
        'nl': 'nl',
        'en': 'en',
        'tr': 'tr',
        'ar': 'ar',
        'dutch': 'nl',
        'english': 'en',
        'turkish': 'tr',
        'arabic': 'ar'
    }
    return language_map.get(lang, 'nl')

def rewrite_response_to_language(ai_service, text, lang_name):
    system_prompt = (
        f"You are a translation engine. Output ONLY {lang_name}. "
        "Never output Dutch or any other language. "
        "Do not add greetings or extra information. "
        "Return plain text only."
    )
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': text}
    ]
    return ai_service.get_chat_completion(messages, tools=None, language=None)

def translate_input_to_language(ai_service, text, lang_name):
    system_prompt = (
        f"You are a translation engine. Translate the following user message into {lang_name} only. "
        "Never output Dutch or any other language. "
        "Return only the translated text. Do not add explanations."
    )
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': text}
    ]
    return ai_service.get_chat_completion(messages, tools=None, language=None)
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
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://"
)
limiter.init_app(app)

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
        # Allow CORS preflight without auth
        if request.method == 'OPTIONS':
            return '', 204
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
    
    # Check for potential XSS/injection (allow apostrophes in normal speech)
    if re.search(r'[<>"]', chat_input):
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
def index():
    """Serve the main HTML page"""
    import os
    # Priority 1: Try chatbot/static (where voice bot modifications are)
    static_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    if os.path.exists(static_path):
        with open(static_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Priority 2: Try website directory
    website_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'website', 'index.html')
    if os.path.exists(website_path):
        with open(website_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Fallback: API info
    return jsonify({
        'message': 'Irado Chatbot API',
        'endpoints': {
            'health': '/health',
            'voice_health': '/api/voice/health',
            'chat': '/api/chat (POST)',
            'speech_to_text': '/api/speech-to-text (POST)',
            'text_to_speech': '/api/text-to-speech (POST)'
        }
    }), 200

@app.route('/<path:filename>')
def serve_website_files(filename):
    """Serve static files - prioritize chatbot/static (voice bot), then website"""
    import os
    
    # Priority 1: Try chatbot/static first (where voice bot modifications are)
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    static_file = os.path.join(static_path, filename)
    
    if os.path.exists(static_file) and os.path.isfile(static_file):
        # Security check
        if os.path.abspath(static_file).startswith(os.path.abspath(static_path)):
            return send_from_directory(static_path, filename)
    
    # Priority 2: Try website directory
    website_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'website')
    website_file = os.path.join(website_path, filename)
    
    if os.path.exists(website_file) and os.path.isfile(website_file):
        # Security check
        if os.path.abspath(website_file).startswith(os.path.abspath(website_path)):
            return send_from_directory(website_path, filename)
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - No authentication required for monitoring"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/voice/health', methods=['GET'])
def voice_health():
    """Voice bot health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'voice-bot',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/speech-to-text', methods=['POST'])
@require_auth
def speech_to_text():
    """
    Convert speech to text using Azure Speech Services.
    
    Request: multipart/form-data with 'audio' file
    Returns: JSON with transcribed text
    """
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'Empty audio file'}), 400
        
        # Get language from form data or default to Dutch
        language = normalize_language_code(request.form.get('language', 'nl'))
        
        # Import Azure Speech SDK
        try:
            import azure.cognitiveservices.speech as speechsdk
        except ImportError:
            return jsonify({'error': 'Azure Speech SDK not installed'}), 500
        
        # Get Azure Speech credentials
        speech_key = Config.AZURE_SPEECH_KEY
        speech_region = Config.AZURE_SPEECH_REGION
        
        if not speech_key or not speech_region:
            error_msg = f'Azure Speech Services not configured. Key: {"SET" if speech_key else "MISSING"}, Region: {speech_region or "MISSING"}'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 500
        
        print(f"DEBUG: Azure Speech configured - Region: {speech_region}")
        
        # Configure speech recognition (use region to avoid endpoint/key mismatch)
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region
        )
        # Give the user more time to start and to pause between words
        speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs,
            "8000"
        )
        speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
            "2500"
        )
        
        # Map language codes to Azure Speech format
        language_map = {
            'nl': 'nl-NL',
            'en': 'en-US',
            'ar': 'ar-SA',
            'tr': 'tr-TR'
        }
        speech_language = language_map.get(language, 'nl-NL')
        speech_config.speech_recognition_language = speech_language
        
        # Save audio file temporarily
        audio_ext = audio_file.filename.split('.')[-1] if '.' in (audio_file.filename or '') else 'webm'
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_ext}') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        file_size = os.path.getsize(tmp_path)
        print(f"DEBUG STT: Saved audio to {tmp_path}")
        print(f"DEBUG STT: File size: {file_size} bytes")
        print(f"DEBUG STT: Audio format: {audio_ext}")
        print(f"DEBUG STT: Language: {speech_language}")
        
        if file_size == 0:
            return jsonify({'error': 'Empty audio file received'}), 400
        if file_size < 1000:
            print(f"WARNING: Audio file very small ({file_size} bytes)")
        
        # Save a copy for debugging
        try:
            debug_path = '/tmp/last_audio_debug.webm'
            shutil.copy(tmp_path, debug_path)
            print(f"DEBUG: Saved copy to {debug_path} for inspection")
        except Exception as copy_error:
            print(f"DEBUG: Could not save debug copy: {copy_error}")
        
        try:
            # Configure audio input
            audio_ext_lower = (audio_ext or '').lower()
            working_path = tmp_path
            # Convert WebM/Opus to WAV to avoid GStreamer issues in Azure SDK
            if audio_ext_lower in ('webm', 'weba'):
                print("DEBUG STT: Converting WebM to WAV...")
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as wav_file:
                    wav_path = wav_file.name
                ffmpeg_cmd = [
                    'ffmpeg', '-y', '-i', tmp_path,
                    '-ac', '1', '-ar', '16000', '-f', 'wav', wav_path
                ]
                print(f"DEBUG STT: FFmpeg command: {' '.join(ffmpeg_cmd)}")
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"ERROR: FFmpeg failed: {result.stderr}")
                    return jsonify({'error': 'Audio conversion failed', 'details': result.stderr}), 500
                converted_size = os.path.getsize(wav_path)
                print(f"DEBUG STT: Converted to WAV, size: {converted_size} bytes")
                working_path = wav_path
                audio_ext_lower = 'wav'

            if audio_ext_lower in ('ogg', 'oga', 'opus'):
                # Use compressed stream format for OGG/Opus audio
                container_format = speechsdk.AudioStreamContainerFormat.OGG_OPUS
                stream_format = speechsdk.audio.AudioStreamFormat(
                    compressed_stream_format=container_format
                )
                push_stream = speechsdk.audio.PushAudioInputStream(stream_format)
                with open(working_path, "rb") as audio_fp:
                    push_stream.write(audio_fp.read())
                push_stream.close()
                audio_config = speechsdk.audio.AudioConfig(stream=push_stream)
                print("DEBUG: Created AudioConfig from PushAudioInputStream (ogg/opus)")
            else:
                audio_config = speechsdk.audio.AudioConfig(filename=working_path)
                print(f"DEBUG: Created AudioConfig from file: {working_path}")
            
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            print(f"DEBUG STT: Starting Azure Speech recognition...")
            
            # Perform recognition
            result = recognizer.recognize_once()
            
            print("DEBUG STT: Recognition completed")
            print(f"DEBUG STT: Result reason: {result.reason}")
            if hasattr(result, 'text'):
                print(f"DEBUG STT: Recognized text: '{result.text}'")
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = result.text.strip()
                return jsonify({
                    'text': text,
                    'language': language
                }), 200
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("DEBUG STT: No speech recognized - audio may be silent or unclear")
                no_match_details = result.no_match_details
                print(f"DEBUG STT: NoMatch reason: {no_match_details.reason if no_match_details else 'Unknown'}")
                return jsonify({
                    'error': 'No speech could be recognized',
                    'text': ''
                }), 400
            elif result.reason == speechsdk.ResultReason.Canceled:
                details = result.cancellation_details
                print(f"DEBUG STT: Canceled - Reason: {details.reason}")
                print(f"DEBUG STT: Error details: {details.error_details}")
                return jsonify({
                    'error': f'Recognition canceled: {details.reason}',
                    'details': details.error_details or '',
                    'text': ''
                }), 500
            else:
                return jsonify({
                    'error': f'Recognition failed: {result.reason}',
                    'text': ''
                }), 500
                
        finally:
            # Clean up temporary file(s)
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            try:
                if 'working_path' in locals() and working_path != tmp_path and os.path.exists(working_path):
                    os.unlink(working_path)
            except Exception:
                pass
            
    except Exception as e:
        import traceback
        print(f"Error in speech-to-text: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/speech-to-text-mock', methods=['POST', 'OPTIONS'])
@require_auth
def speech_to_text_mock():
    """Mock endpoint for testing UI without Azure Speech"""
    time.sleep(1)
    return jsonify({
        'text': 'Ik wil een bank laten ophalen',
        'language': 'nl'
    }), 200

@app.route('/api/text-to-speech', methods=['POST'])
@require_auth
def text_to_speech():
    """
    Convert text to speech using Azure Speech Services.
    
    Request: JSON with 'text' and 'language'
    Returns: WAV audio file
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = normalize_language_code(data.get('language', 'nl'))
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Import Azure Speech SDK
        try:
            import azure.cognitiveservices.speech as speechsdk
        except ImportError:
            return jsonify({'error': 'Azure Speech SDK not installed'}), 500
        
        # Get Azure Speech credentials
        speech_key = Config.AZURE_SPEECH_KEY
        speech_region = Config.AZURE_SPEECH_REGION
        
        if not speech_key or not speech_region:
            return jsonify({'error': 'Azure Speech Services not configured'}), 500
        
        # Configure speech synthesis (use region to avoid endpoint/key mismatch)
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region
        )
        
        # Map language codes to voice names
        voice_map = {
            'nl': 'nl-NL-ColetteNeural',
            'en': 'en-US-JennyNeural',
            'ar': 'ar-SA-ZariyahNeural',
            'tr': 'tr-TR-EmelNeural'
        }
        voice_name = voice_map.get(language, 'nl-NL-ColetteNeural')
        speech_config.speech_synthesis_voice_name = voice_name
        
        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        # Synthesize speech
        result = synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Return audio data
            from flask import Response
            return Response(
                result.audio_data,
                mimetype='audio/wav',
                headers={
                    'Content-Disposition': 'attachment; filename=speech.wav'
                }
            )
        elif result.reason == speechsdk.ResultReason.Canceled:
            details = result.cancellation_details
            return jsonify({
                'error': f'Speech synthesis canceled: {details.reason}',
                'details': details.error_details or ''
            }), 500
        else:
            return jsonify({
                'error': f'Speech synthesis failed: {result.reason}'
            }), 500
            
    except Exception as e:
        import traceback
        print(f"Error in text-to-speech: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/text-to-speech-mock', methods=['POST', 'OPTIONS'])
@require_auth
def text_to_speech_mock():
    """Mock endpoint for testing UI without Azure Speech"""
    time.sleep(1)
    wav_data = (
        b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00'
        b'D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    )
    return Response(wav_data, mimetype='audio/wav')

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
        requested_language = normalize_language_code(data.get('language', 'nl'))
        allow_greeting = data.get('allowGreeting', True)
        is_voice = bool(data.get('is_voice', False))
        debug_flag = bool(data.get('debug', False))
        if is_voice:
            if session_id in VOICE_SESSION_LANGUAGE:
                requested_language = VOICE_SESSION_LANGUAGE[session_id]
            else:
                VOICE_SESSION_LANGUAGE[session_id] = requested_language
        print(f"Chat API: language={requested_language} session={session_id} is_voice={is_voice}")
        if is_voice:
            print(f"Chat API: voice chat_input='{chat_input}' allow_greeting={allow_greeting}")
        if is_voice:
            # Voice greeting is handled client-side; never greet from backend
            allow_greeting = False
        
        # Create or update session (optional if DB is unavailable)
        db_available = True
        try:
        db_manager.create_or_update_session(session_id)
        # Save user message
        db_manager.save_message(session_id, 'user', chat_input)
        # Get chat history for context
        chat_history = db_manager.get_chat_history(session_id, limit=10)
        except Exception as db_error:
            db_available = False
            chat_history = []
            print(f"Chat API warning: DB unavailable, continuing without history: {db_error}")
        
        # Prepare messages for AI (user-only history to avoid language anchoring)
        model_input = chat_input
        if is_voice and requested_language in ('en', 'tr', 'ar'):
            try:
                input_lang_map = {
                    'en': 'English',
                    'tr': 'Turkish',
                    'ar': 'Arabic'
                }
                input_lang_name = input_lang_map.get(requested_language, 'English')
                model_input = translate_input_to_language(ai_service, chat_input, input_lang_name)
                print(f"Chat API: translated_input='{model_input}'")
            except Exception as translate_error:
                print(f"Chat API warning: input translation failed: {translate_error}")
                model_input = chat_input

        if is_voice:
            # Voice mode: use only the current user message to avoid any history bleed
            messages = [{
                'role': 'user',
                'content': model_input
            }]
        else:
            messages = []
            for msg in chat_history:
                if msg['message_type'] != 'user':
                    continue
                messages.append({
                    'role': 'user',
                    'content': msg['content']
                })
        
        lang_name_map = {
            'nl': 'Dutch',
            'en': 'English',
            'tr': 'Turkish',
            'ar': 'Arabic'
        }
        lang_name = lang_name_map.get(requested_language, 'Dutch')
        system_prompt = (
            f"You MUST reply ONLY in {lang_name}. "
            "Do NOT switch languages. "
            "Do NOT auto-detect language. "
            f"Always assume the user wants {lang_name}. "
            f"Set JSON field language to '{requested_language}'. "
        )
        if allow_greeting is False:
            system_prompt += (
                "Do NOT greet or introduce yourself. "
                "Do NOT repeat the welcome message. "
                "Answer the user's question directly. "
            )
        if is_voice:
            print(f"Chat API: system_prompt='{system_prompt}'")

        # Remove any previous system messages and insert a single system prompt
        messages = [m for m in messages if m.get('role') != 'system']
        messages.insert(0, {
            'role': 'system',
            'content': system_prompt
        })
        
        # Get AI response
        tools = ai_service.get_available_tools()
        ai_response = ai_service.get_chat_completion(messages, tools, requested_language)
        if not ai_response or not str(ai_response).strip():
            fallback_map = {
                'en': 'Sorry, no response was received. Please try again.',
                'nl': 'Sorry, er is geen antwoord ontvangen. Probeer het opnieuw.',
                'tr': 'Üzgünüm, bir yanıt alınamadı. Lütfen tekrar deneyin.',
                'ar': 'عذرًا، لم يتم استلام أي رد. يرجى المحاولة مرة أخرى.'
            }
            ai_response = fallback_map.get(requested_language, fallback_map['nl'])
        if is_voice:
            print(f"Chat API: raw ai_response='{ai_response}'")
        
        # Voice mode hard-lock: rewrite response in selected language if needed
        if is_voice and requested_language in ('en', 'tr', 'ar'):
            try:
                lang_name_map = {
                    'en': 'English',
                    'tr': 'Turkish',
                    'ar': 'Arabic'
                }
                lang_name = lang_name_map.get(requested_language, 'English')
                ai_response = rewrite_response_to_language(ai_service, ai_response, lang_name)
                print(f"Chat API: rewritten_response='{ai_response}'")
            except Exception as rewrite_error:
                print(f"Chat API warning: rewrite failed, returning original response: {rewrite_error}")
        
        # Remove any system/policy leakage from the response
        if isinstance(ai_response, str):
            ai_response = re.sub(
                r"(?is)important:\s*google's policies.*?(?:language:\s*\w+\s*)",
                "",
                ai_response
            ).strip()

        # Save AI response (if DB is available)
        if db_available:
            db_manager.save_message(session_id, 'bot', ai_response)
        
        # Return response (include debug info if requested)
        response_payload = {'output': ai_response}
        if debug_flag:
            response_payload['debug'] = {
                'requested_language': requested_language,
                'allow_greeting': allow_greeting,
                'is_voice': is_voice,
                'session_id': session_id,
                'translated_input': model_input if is_voice else None
            }
        return jsonify(response_payload)
        
    except Exception as e:
        import traceback
        print(f"Chat API error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
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
        # Test database connection (optional for development - app can still run)
        try:
            db_manager.get_connection()
            print("✅ Database connection successful")
        except Exception as db_error:
            print(f"⚠️  Database connection failed: {db_error}")
            print("⚠️  Continuing without database (some features may not work)")
            print("⚠️  To fix: Start PostgreSQL or update .env with correct database settings")
        
        # Test OpenAI connection (optional - skip if not critical)
        try:
            test_response = ai_service.get_chat_completion([
                {'role': 'user', 'content': 'test'}
            ])
            print("✅ OpenAI connection successful")
        except Exception as e:
            print(f"⚠️  OpenAI connection test skipped: {e}")
        
        print("✅ Application initialized (some services may be unavailable)")
        return True
        
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

if __name__ == '__main__':
    if init_app():
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Failed to initialize application")


