"""
AI service for handling OpenAI interactions and system prompts
"""
import openai
import json
import os
import logging
from typing import List, Dict, Optional
from config import Config
from address_validation import AddressValidationService
from system_prompt_service import SystemPromptService
from system_log_service import SystemLogService
from logging_utils import (
    log_ai_request, log_ai_response, log_tool_call,
    log_tool_result, log_error, log_event
)

logger = logging.getLogger(__name__)

class AIService:
    """Handles OpenAI API interactions"""
    
    def __init__(self):
        self.config = Config()
        # Configure Azure OpenAI
        self.client = openai.AzureOpenAI(
            api_key=self.config.AZURE_OPENAI_API_KEY,
            api_version=self.config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT
        )
        self.address_validator = AddressValidationService()
        self.prompt_service = SystemPromptService(self.config)
        self.system_log_service = SystemLogService(self.config)
        try:
            self.system_log_service.ensure_tables()
        except Exception:
            pass

    def _classify_openai_error(self, e: Exception) -> Dict[str, Optional[object]]:
        """Map OpenAI/Azure OpenAI exceptions to stable error types."""
        error_type = type(e).__name__
        http_status = getattr(e, "status_code", None) or getattr(e, "status", None)

        # openai v1.x common errors
        if isinstance(e, getattr(openai, "RateLimitError", ())):
            error_type = "RateLimited"
        elif isinstance(e, getattr(openai, "APITimeoutError", ())):
            error_type = "Timeout"
        elif isinstance(e, getattr(openai, "APIConnectionError", ())):
            error_type = "ConnectionError"

        # Fallback heuristic for quota and connection-ish messages
        msg = str(e).lower()
        if "quota" in msg:
            error_type = "QuotaExceeded"
        elif "rate limit" in msg or "ratelimit" in msg:
            error_type = "RateLimited"
        elif "timeout" in msg:
            error_type = "Timeout"
        elif "connection" in msg or "connect" in msg:
            error_type = "ConnectionError"

        return {"error_type": error_type, "http_status": http_status}
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the Irado chatbot
        Loads from database first, with file and hardcoded fallbacks
        """
        try:
            base_prompt = self.prompt_service.get_prompt_with_fallback()
        except Exception as e:
            print(f"Error loading system prompt: {e}")
            base_prompt = "Je bent de virtuele assistent van Irado. Help klanten met vragen over afval en recycling."

        # IMPORTANT: We always append a stable UI contract description here so
        # the system prompt in the database can stay focused on domain logic.
        # This keeps all frontend-related structure in code instead of in DB.
        ui_contract_instructions = """

BELANGRIJK – ANTWOORDFORMAT EN KNOPPEN (UI CONTRACT)
====================================================

Je antwoordt ALTIJD met exact één JSON-object, zonder extra tekst eromheen,
zonder uitleg en zonder markdown-codeblokken. Het JSON-object heeft deze vorm:

{
  "text": "<hoofdtekst voor de gebruiker (mag markdown bevatten)>",
  "language": "<nl|en|tr|ar>",
  "buttons": [
    {
      "id": "<korte-stabiele-id-zonder-spaties>",
      "label": "<zichtbare tekst op de knop in de actieve taal>",
      "value": "<volledige tekst die als volgende gebruikersinvoer verstuurd moet worden>",
      "variant": "<primary|secondary>"
    }
  ],
  "showAfvalplaatsImage": <true|false>
}

Regels:
- "text": schrijf hier je normale antwoord voor de klant (mag markdown bevatten).
- "language": gebruik precies één van: "nl", "en", "tr", "ar" afhankelijk van de gesprekstaal.
- "buttons": is een lijst (array). Als je geen knoppen nodig hebt, gebruik je een lege lijst [].
- "showAfvalplaatsImage": zet op true als de klant de afbeelding moet zien waar grofvuil geplaatst moet worden, anders false.

JA/NEE-VRAGEN EN ANDERE KEUZES
- Bij ja/nee-vragen maak je ALTIJD twee knoppen met labels in de actieve taal, bijvoorbeeld:
  - Nederlands:  "Ja" / "Nee"
  - Engels:      "Yes" / "No"
  - Turks:       "Evet" / "Hayır"
  - Arabisch:    "نعم" / "لا"
- Gebruik duidelijke, toegankelijke labels die ook voor oudere of minder digitale mensen begrijpelijk zijn.
- De property "value" bevat de tekst die als volgende gebruikersinvoer verstuurd moet worden als de knop wordt aangeklikt.

TAALKEUZE
- Aan het begin van het gesprek kan de frontend speciale berichten sturen zoals:
  - "start chat - language: dutch"
  - "start chat - language: english"
  - "start chat - language: turkish"
  - "start chat - language: arabic"
- Als je zo'n bericht ziet, kies je de bijbehorende taal:
  - dutch   -> language = "nl"
  - english -> language = "en"
  - turkish -> language = "tr"
  - arabic  -> language = "ar"
- Vanaf dat moment blijf je consequent in die taal antwoorden en vul je "language" daar ook op in.

FOUTAFHANDELING
- Als je een antwoord geeft zonder knoppen, hou "buttons": [].
- Geef NOOIT een los stuk tekst buiten het JSON-object.
- Gebruik geldige JSON met dubbele aanhalingstekens en zonder comments.
"""

        return base_prompt + ui_contract_instructions
    
    def get_chat_completion(self, messages: List[Dict], tools: List[Dict] = None) -> str:
        """Get chat completion from OpenAI"""
        try:
            # Prepare messages with system prompt
            system_message = {"role": "system", "content": self.get_system_prompt()}
            all_messages = [system_message] + messages
            
            # Prepare function definitions if tools are provided
            function_definitions = []
            if tools:
                for tool in tools:
                    if tool.get('type') == 'function':
                        function_definitions.append(tool)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.config.AZURE_OPENAI_DEPLOYMENT,
                messages=all_messages,
                temperature=self.config.OPENAI_TEMPERATURE,
                max_completion_tokens=self.config.OPENAI_MAX_TOKENS
            )
            
            # Log token usage for cost monitoring
            if hasattr(response, 'usage') and response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                
                # Calculate costs (GPT-4o mini pricing)
                input_cost = (input_tokens / 1_000_000) * 0.15  # $0.15 per 1M input tokens
                output_cost = (output_tokens / 1_000_000) * 0.60  # $0.60 per 1M output tokens
                total_cost = input_cost + output_cost
                
                print(f"💰 Token Usage - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}")
                print(f"💵 Cost - Input: ${input_cost:.4f}, Output: ${output_cost:.4f}, Total: ${total_cost:.4f}")
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error getting chat completion: {e}")
            return "Sorry, er is een fout opgetreden. Probeer het later opnieuw."
    
    def get_chat_completion_with_tools(
        self,
        messages: List[Dict],
        tools: List[Dict],
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """Get chat completion with tool handling"""
        session_label = session_id or 'unknown_session'
        try:
            system_message = {"role": "system", "content": self.get_system_prompt()}
            all_messages = [system_message] + messages

            function_definitions = [
                tool for tool in tools
                if tool.get('type') == 'function'
            ]

            has_tools = bool(function_definitions)
            log_ai_request(session_label, self.config.AZURE_OPENAI_DEPLOYMENT, len(all_messages), has_tools)

            while True:
                response = self.client.chat.completions.create(
                    model=self.config.AZURE_OPENAI_DEPLOYMENT,
                    messages=all_messages,
                    tools=function_definitions if function_definitions else None,
                    tool_choice="auto" if function_definitions else None,
                    temperature=self.config.OPENAI_TEMPERATURE,
                    max_completion_tokens=self.config.OPENAI_MAX_TOKENS
                )

                message = response.choices[0].message
                usage = getattr(response, 'usage', None)
                tokens = None
                if usage:
                    tokens = {
                        'prompt_tokens': usage.prompt_tokens,
                        'completion_tokens': usage.completion_tokens,
                        'total_tokens': usage.total_tokens
                    }
                    input_cost = (usage.prompt_tokens / 1_000_000) * 0.15
                    output_cost = (usage.completion_tokens / 1_000_000) * 0.60
                    total_cost = input_cost + output_cost
                    print(f"💰 Token Usage - Input: {usage.prompt_tokens}, Output: {usage.completion_tokens}, Total: {usage.total_tokens}")
                    print(f"💵 Estimated Cost - Input: ${input_cost:.4f}, Output: ${output_cost:.4f}, Total: ${total_cost:.4f}")
                log_ai_response(session_label, len(message.content or ''), bool(message.tool_calls), tokens)

                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        try:
                            arguments = json.loads(tool_call.function.arguments or "{}")
                        except json.JSONDecodeError:
                            arguments = {"_raw": tool_call.function.arguments}

                        log_tool_call(session_label, function_name, arguments, 'started')
                        print(f"🔧 Tool call: {function_name} with args: {arguments}")

                        try:
                            function_response = self._handle_function_call(function_name, arguments, session_label)
                            log_tool_result(session_label, function_name, True, function_response)
                            preview = function_response
                            if isinstance(function_response, str) and len(function_response) > 200:
                                preview = function_response[:200] + "..."
                            print(f"✅ Tool response: {preview}")
                        except Exception as tool_error:
                            log_tool_result(session_label, function_name, False, error=str(tool_error))
                            print(f"❌ Tool error: {tool_error}")
                            raise

                        all_messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        all_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": function_response
                        })
                    continue

                content = message.content or ""
                if not content.strip():
                    print("WARNING: Empty response without tool call")
                    # Fallback: return minimal valid UI payload
                    return {
                        "text": "Hoi! Waarmee kan ik je helpen?",
                        "language": "nl",
                        "buttons": [],
                        "showAfvalplaatsImage": False,
                    }

                # Try to parse the model output as JSON according to the UI contract.
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict) and "text" in parsed:
                        # Ensure all expected fields exist so the frontend can rely on them.
                        if "language" not in parsed or not parsed["language"]:
                            parsed["language"] = "nl"
                        if "buttons" not in parsed or not isinstance(parsed["buttons"], list):
                            parsed["buttons"] = []
                        if "showAfvalplaatsImage" not in parsed:
                            parsed["showAfvalplaatsImage"] = False

                        # Accessibility: automatically add language-specific Yes/No buttons
                        # at the privacy question, based on the active language.
                        text_lower = (parsed.get("text") or "").lower()
                        if (
                            "privacyverklaring" in text_lower
                            or "https://www.irado.nl/privacyverklaring" in text_lower
                        ) and not parsed["buttons"]:
                            lang = parsed.get("language") or "nl"
                            if lang == "en":
                                yes_label = yes_value = "Yes"
                                no_label = no_value = "No"
                            elif lang == "tr":
                                yes_label = yes_value = "Evet"
                                no_label = no_value = "Hayır"
                            elif lang == "ar":
                                yes_label = yes_value = "نعم"
                                no_label = no_value = "لا"
                            else:
                                # Default to Dutch
                                yes_label = yes_value = "Ja"
                                no_label = no_value = "Nee"

                            parsed["buttons"] = [
                                {
                                    "id": "privacy_yes",
                                    "label": yes_label,
                                    "value": yes_value,
                                    "variant": "primary",
                                },
                                {
                                    "id": "privacy_no",
                                    "label": no_label,
                                    "value": no_value,
                                    "variant": "secondary",
                                },
                            ]

                        return parsed
                except Exception:
                    # If JSON parsing fails we fall back to a simple payload wrapper.
                    pass

                # Fallback: wrap plain text response in a structured payload.
                return {
                    "text": content,
                    "language": "nl",
                    "buttons": [],
                    "showAfvalplaatsImage": False,
                }
            
        except Exception as e:
            # Persist Azure OpenAI failure to DB-first logs (dashboard searchable).
            try:
                classification = self._classify_openai_error(e)
                self.system_log_service.log_exception(
                    event_name="openai.error",
                    component="openai",
                    message=str(e),
                    exc=e,
                    request_id=request_id,
                    session_id=session_id,
                    error_type=classification.get("error_type"),
                    http_status=classification.get("http_status"),
                    meta={
                        "deployment": self.config.AZURE_OPENAI_DEPLOYMENT,
                        "api_version": self.config.AZURE_OPENAI_API_VERSION,
                    },
                )
            except Exception:
                pass

            print(f"Error getting chat completion with tools: {e}")
            log_error('get_chat_completion_with_tools', e, session_label)
            # Always return a valid payload even on errors so the frontend stays simple.
            return {
                "text": "Sorry, er is een fout opgetreden. Probeer het later opnieuw.",
                "language": "nl",
                "buttons": [],
                "showAfvalplaatsImage": False,
            }

    def _handle_function_call(self, function_name: str, function_args: Dict, session_id: Optional[str] = None) -> str:
        """Handle function calls from the AI"""
        try:
            if function_name == "validate_address":
                postcode = function_args.get("postcode", "")
                huisnummer = function_args.get("huisnummer", "")
                result = self.address_validator.validate_address(postcode, huisnummer)
                
                if result.is_valid:
                    if result.is_in_service_area:
                        return f"Adres is geldig en ligt in het verzorgingsgebied van {result.service_area_municipality}. Postcode: {result.postcode}, Straat: {result.straat}, Plaats: {result.woonplaats}."
                    else:
                        return f"Dit adres ligt niet in ons verzorgingsgebied voor particuliere klanten. Postcode: {result.postcode}, Plaats: {result.woonplaats}. Dit lijkt een bedrijfsadres te zijn. Verwijs de klant door naar de zakelijke klantenservice voor bedrijfsafval."
                else:
                    return "Adres is niet geldig. Controleer de postcode en het huisnummer."
            
            elif function_name == "validate_address_from_text":
                address_text = function_args.get("address_text", "")
                result = self.address_validator.validate_address_from_text(address_text)
                
                if result.is_valid:
                    if result.is_in_service_area:
                        return f"Adres is geldig en ligt in het verzorgingsgebied van {result.service_area_municipality}. Postcode: {result.postcode}, Straat: {result.straat}, Plaats: {result.woonplaats}."
                    else:
                        return f"Dit adres ligt niet in ons verzorgingsgebied voor particuliere klanten. Postcode: {result.postcode}, Plaats: {result.woonplaats}. Dit lijkt een bedrijfsadres te zijn. Verwijs de klant door naar de zakelijke klantenservice voor bedrijfsafval."
                else:
                    return "Kon geen geldig adres uit de tekst extraheren. Geef alstublieft postcode en huisnummer op."
            
            elif function_name == "send_email_to_team":
                # Send internal email to team with XML content
                try:
                    from email_service_xml import EmailService
                    email_service = EmailService()

                    request_data = self._build_team_email_payload(function_args, session_id=session_id)

                    log_event('EMAIL_TO_TEAM', '🔵 Preparing XML email to team', {
                        'session_id': session_id,
                        'customer': request_data['customer'],
                        'route': request_data['route'],
                        'items': request_data['items'],
                        'estimated_volume_m3': request_data.get('estimated_volume_m3')
                    })

                    xml_content = email_service.create_grofvuil_request_xml(request_data)

                    log_event('XML_GENERATED', f'XML content generated ({len(xml_content)} chars)', {
                        'session_id': session_id,
                        'route_code': request_data['route']['code'],
                        'xml_preview': xml_content[:400]
                    }, 'debug')

                    subject = f"Grofvuil aanvraag - {request_data['route']['name']} ({request_data['address']['municipality']})"
                    success = email_service.send_internal_notification(
                        subject=subject,
                        content=xml_content,
                        content_type='xml'
                    )

                    if success:
                        log_event('EMAIL_TO_TEAM_SUCCESS', '✅ XML email to team sent successfully', {
                            'session_id': session_id,
                            'route_code': request_data['route']['code'],
                            'customer': request_data['customer']
                        })
                        return f"✅ Interne aanvraag verzonden naar Irado team (route: {request_data['route']['name']})"
                    else:
                        log_event('EMAIL_TO_TEAM_FAILED', '❌ Failed to send XML to team', {
                            'session_id': session_id,
                            'route_code': request_data['route']['code'],
                            'customer': request_data['customer']
                        }, 'error')
                        return "Fout bij verzenden van aanvraag naar team. Neem contact op met klantenservice."
                except Exception as e:
                    log_error('send_email_to_team', e, session_id)
                    print(f"Error sending team XML email: {e}")
                    import traceback
                    traceback.print_exc()
                    return f"Fout bij verzenden van aanvraag: {str(e)}"
            
            elif function_name == "send_email_to_customer":
                # Send confirmation email to customer
                try:
                    from email_service_xml import EmailService
                    email_service = EmailService()

                    request_data = self._build_customer_email_payload(function_args, session_id=session_id)

                    customer_email = request_data['customer']['email']
                    if not customer_email:
                        log_event('EMAIL_TO_CUSTOMER_NO_EMAIL', 'No customer email provided', {
                            'session_id': session_id
                        }, 'warning')
                        return "Geen geldig e-mailadres beschikbaar voor bevestiging."

                    log_event('EMAIL_TO_CUSTOMER', '🟢 Preparing confirmation email to customer', {
                        'session_id': session_id,
                        'customer': request_data['customer'],
                        'routes': request_data['routes'],
                        'total_items': len(request_data['items'])
                    })

                    html_content = email_service.create_customer_confirmation_html(request_data)

                    log_event('HTML_GENERATED', f'HTML confirmation generated ({len(html_content)} chars)', {
                        'session_id': session_id,
                        'customer_email': customer_email,
                        'html_preview': html_content[:400]
                    }, 'debug')

                    success = email_service.send_customer_confirmation(
                        customer_email,
                        "Bevestiging grofvuil aanvraag - Irado",
                        html_content
                    )

                    if success:
                        log_event('EMAIL_TO_CUSTOMER_SUCCESS', '✅ Confirmation email to customer sent', {
                            'session_id': session_id,
                            'customer_email': customer_email
                        })
                        return f"✅ Bevestigingsemail verzonden naar {customer_email}"
                    else:
                        log_event('EMAIL_TO_CUSTOMER_FAILED', '❌ Failed to send confirmation to customer', {
                            'session_id': session_id,
                            'customer_email': customer_email
                        }, 'error')
                        return "Fout bij verzenden van bevestigingsemail."
                except Exception as e:
                    log_error('send_email_to_customer', e, session_id)
                    print(f"Error sending customer email: {e}")
                    import traceback
                    traceback.print_exc()
                    return f"Fout bij verzenden van bevestigingsemail: {str(e)}"

            else:
                return f"Onbekende functie: {function_name}"
                
        except Exception as e:
            print(f"Error handling function call {function_name}: {e}")
            return f"Fout bij uitvoeren van functie {function_name}."

    def _build_team_email_payload(self, args: Dict, session_id: Optional[str] = None) -> Dict:
        customer = args.get('customer', {}) or {}
        if not isinstance(customer, dict):
            customer = {}
        customer.setdefault('name', args.get('name', 'Onbekend'))
        customer.setdefault('email', args.get('email', ''))
        if not customer.get('phone') and args.get('phone'):
            customer['phone'] = args.get('phone')

        address = args.get('address', {}) or {}
        if not isinstance(address, dict):
            address = {}
        address.setdefault('street', args.get('street', ''))
        address.setdefault('house_number', args.get('house_number', ''))
        address.setdefault('postal_code', args.get('postal_code', ''))
        address.setdefault('city', args.get('city', ''))
        address.setdefault('municipality', args.get('municipality', 'Onbekend'))
        address['full'] = args.get('address_text') or f"{address.get('street', '')} {address.get('house_number', '')}, {address.get('postal_code', '')} {address.get('city', '')}"

        route = args.get('route', {}) or {}
        if not isinstance(route, dict):
            route = {}
        route.setdefault('code', args.get('route_code', 'HUISRAAD'))
        route.setdefault('name', args.get('route_name', route['code'].replace('_', ' ').title()))
        if 'estimated_volume_m3' not in route and args.get('estimated_volume_m3') is not None:
            route['estimated_volume_m3'] = args.get('estimated_volume_m3')
        if 'municipal_limit_m3' not in route and args.get('municipal_limit_m3') is not None:
            route['municipal_limit_m3'] = args.get('municipal_limit_m3')
        if args.get('route_notes') and not route.get('notes'):
            route['notes'] = args['route_notes']

        raw_items = args.get('items', []) or []
        normalized_items = []
        for item in raw_items:
            if isinstance(item, dict):
                normalized_items.append({
                    'description': item.get('description') or item.get('name') or 'Onbekend item',
                    'quantity': item.get('quantity', 1),
                    'length_m': item.get('length_m'),
                    'width_m': item.get('width_m'),
                    'height_m': item.get('height_m'),
                    'weight_kg': item.get('weight_kg'),
                    'notes': item.get('notes'),
                    'category': item.get('category')
                })
            else:
                normalized_items.append({'description': str(item), 'quantity': 1})

        constraints = args.get('constraints', {}) or {}
        if not isinstance(constraints, dict):
            constraints = {}
        constraints.setdefault('max_piece_length_m', 1.8)
        constraints.setdefault('max_piece_width_m', 0.9)
        constraints.setdefault('max_piece_weight_kg', 30)

        payload = {
            'customer': customer,
            'address': address,
            'route': route,
            'items': normalized_items,
            'constraints': constraints,
            'estimated_volume_m3': route.get('estimated_volume_m3'),
            'municipal_limit_m3': route.get('municipal_limit_m3'),
            'special_instructions': args.get('special_instructions') or args.get('notes'),
            'session_id': session_id
        }

        return payload

    def _build_customer_email_payload(self, args: Dict, session_id: Optional[str] = None) -> Dict:
        customer = args.get('customer', {}) or {}
        if not isinstance(customer, dict):
            customer = {}
        customer.setdefault('name', args.get('name', 'Klant'))
        customer.setdefault('email', args.get('email', ''))

        address = args.get('address', {}) or {}
        if not isinstance(address, dict):
            address = {}
        address.setdefault('street', args.get('street', ''))
        address.setdefault('house_number', args.get('house_number', ''))
        address.setdefault('postal_code', args.get('postal_code', ''))
        address.setdefault('city', args.get('city', ''))
        address.setdefault('municipality', args.get('municipality', ''))
        address['full'] = args.get('address_text') or f"{address.get('street', '')} {address.get('house_number', '')}, {address.get('postal_code', '')} {address.get('city', '')}"

        items = args.get('items', []) or []
        if not isinstance(items, list):
            items = [str(items)]
        items = [str(item) for item in items]

        routes = args.get('routes', []) or []
        normalized_routes = []
        for route in routes:
            if isinstance(route, dict):
                normalized_routes.append({
                    'route_name': route.get('route_name') or route.get('name') or 'Onbekende route',
                    'route_code': route.get('route_code') or route.get('code'),
                    'items': route.get('items', []),
                    'notes': route.get('notes')
                })
            else:
                normalized_routes.append({
                    'route_name': str(route),
                    'items': []
                })

        if not normalized_routes:
            normalized_routes.append({
                'route_name': 'Onbekende route',
                'items': items,
                'notes': None
            })

        planning_notes = args.get('planning_notes') or ''

        payload = {
            'customer': customer,
            'address': address,
            'items': items,
            'routes': normalized_routes,
            'planning_notes': planning_notes,
            'additional_notes': args.get('additional_notes') or args.get('notes'),
            'session_id': session_id
        }

        return payload
    
    def get_available_tools(self) -> List[Dict]:
        """Get available tools for the AI agent"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "validate_address",
                    "description": "Validate a Dutch address and check if it's in the service area",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "postcode": {
                                "type": "string",
                                "description": "Dutch postcode (e.g., '1017XN')"
                            },
                            "huisnummer": {
                                "type": "string",
                                "description": "House number (e.g., '42')"
                            }
                        },
                        "required": ["postcode", "huisnummer"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_address_from_text",
                    "description": "Extract and validate address from text input",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "address_text": {
                                "type": "string",
                                "description": "Text containing address information"
                            }
                        },
                        "required": ["address_text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email_to_team",
                    "description": "Send internal XML email to Irado team with grofvuil request details for a specific pickup route.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer": {
                                "type": "object",
                                "description": "Customer contact details",
                                "properties": {
                                    "name": {"type": "string"},
                                    "email": {"type": "string"},
                                    "phone": {"type": "string"}
                                },
                                "required": ["name", "email"]
                            },
                            "address": {
                                "type": "object",
                                "properties": {
                                    "street": {"type": "string"},
                                    "house_number": {"type": "string"},
                                    "postal_code": {"type": "string"},
                                    "city": {"type": "string"},
                                    "municipality": {"type": "string"}
                                },
                                "required": ["street", "house_number", "postal_code", "city", "municipality"]
                            },
                            "route": {
                                "type": "object",
                                "description": "Route metadata",
                                "properties": {
                                    "code": {
                                        "type": "string",
                                        "enum": ["HUISRAAD", "IJZER_EA_MATRASSEN", "TUIN_SNOEIAFVAL"]
                                    },
                                    "name": {"type": "string"},
                                    "estimated_volume_m3": {"type": "number"},
                                    "municipal_limit_m3": {"type": "number"},
                                    "notes": {"type": "string"}
                                },
                                "required": ["code", "name"]
                            },
                            "items": {
                                "type": "array",
                                "description": "List of items that belong to this route",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "description": {"type": "string"},
                                        "quantity": {"type": "number"},
                                        "length_m": {"type": "number"},
                                        "width_m": {"type": "number"},
                                        "height_m": {"type": "number"},
                                        "weight_kg": {"type": "number"},
                                        "notes": {"type": "string"},
                                        "category": {"type": "string"}
                                    },
                                    "required": ["description"]
                                },
                                "minItems": 1
                            },
                            "constraints": {
                                "type": "object",
                                "properties": {
                                    "max_piece_length_m": {"type": "number"},
                                    "max_piece_width_m": {"type": "number"},
                                    "max_piece_weight_kg": {"type": "number"}
                                }
                            },
                            "special_instructions": {
                                "type": "string",
                                "description": "Special instructions for planning or collection"
                            }
                        },
                        "required": ["customer", "address", "route", "items"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email_to_customer",
                    "description": "Send HTML confirmation email to customer after their grofvuil request has been processed. Include all routes and items in the summary.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "email": {"type": "string"}
                                },
                                "required": ["name", "email"]
                            },
                            "address": {
                                "type": "object",
                                "properties": {
                                    "street": {"type": "string"},
                                    "house_number": {"type": "string"},
                                    "postal_code": {"type": "string"},
                                    "city": {"type": "string"},
                                    "municipality": {"type": "string"}
                                }
                            },
                            "items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "All items included in the request"
                            },
                            "routes": {
                                "type": "array",
                                "description": "Breakdown of items per pickup route",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "route_name": {"type": "string"},
                                        "route_code": {"type": "string"},
                                        "items": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "notes": {"type": "string"}
                                    },
                                    "required": ["route_name", "items"]
                                }
                            },
                            "planning_notes": {
                                "type": "string",
                                "description": "Planning information to share with the customer"
                            },
                            "additional_notes": {
                                "type": "string",
                                "description": "Any extra instructions for the customer"
                            }
                        },
                        "required": ["customer", "items", "routes"]
                    }
                }
            }
        ]
