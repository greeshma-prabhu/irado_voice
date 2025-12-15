"""
Email service for sending notifications and confirmations with XML support
"""
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from datetime import datetime
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape

from config import Config
from logging_utils import (
    log_email_attempt, log_email_result, log_smtp_details,
    log_error, log_event
)

logger = logging.getLogger(__name__)

class EmailService:
    """Handles email sending for the chatbot with XML support"""
    
    def __init__(self):
        self.config = Config()
        self.smtp_server = None
        self.timezone = ZoneInfo(self.config.APP_TIMEZONE)
    
    def get_smtp_connection(self):
        """Get SMTP connection"""
        if not self.smtp_server:
            context = ssl.create_default_context()
            self.smtp_server = smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT)
            self.smtp_server.starttls(context=context)
            self.smtp_server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
        return self.smtp_server
    
    def close_connection(self):
        """Close SMTP connection"""
        if self.smtp_server:
            self.smtp_server.quit()
            self.smtp_server = None
    
    def send_email(self, to_email: str, subject: str, content: str, content_type: str = 'html', from_email: str = None, as_attachment: bool = False, session_id: str = 'current_session'):
        """Send email to customer with XML or HTML content"""
        if not from_email:
            from_email = self.config.FROM_EMAIL
        
        # Log email attempt
        log_email_attempt(session_id or 'current_session', content_type, to_email, bool(content))
        log_event('EMAIL_DETAILS', f'Preparing {content_type} email', {
            'to': to_email,
            'from': from_email,
            'subject': subject,
            'content_length': len(content),
            'content_type': content_type,
            'as_attachment': as_attachment,
            'content_preview': content[:500] + '...' if len(content) > 500 else content
        })
        
        # Log full content for debugging (truncated for readability)
        print(f"📧 EMAIL CONTENT ({content_type}):")
        print(f"   To: {to_email}")
        print(f"   Subject: {subject}")
        print(f"   As attachment: {as_attachment}")
        print(f"   Content ({len(content)} chars):")
        print("   " + "-" * 70)
        # Show first 800 chars of content
        preview = content[:800] if len(content) > 800 else content
        for line in preview.split('\n')[:20]:  # Max 20 lines
            print(f"   {line}")
        if len(content) > 800:
            print(f"   ... ({len(content) - 800} more chars)")
        print("   " + "-" * 70)
        
        # Check if SMTP is configured
        if not self.config.SMTP_HOST or not self.config.SMTP_USER:
            log_event('EMAIL_SIMULATION', 'SMTP niet geconfigureerd - simulatie', {
                'session_id': session_id,
                'to': to_email,
                'subject': subject,
                'content_type': content_type
            }, 'warning')
            print(f"⚠️  SMTP not configured. Would send {content_type} email to {to_email}:")
            print(f"   Subject: {subject}")
            print(f"   Content preview: {content[:200]}...")
            print(f"✅ Email simulation successful (SMTP not configured)")
            log_email_result(session_id or 'current_session', content_type, True)
            return True
        
        # Log SMTP config
        log_smtp_details(
            self.config.SMTP_HOST,
            self.config.SMTP_PORT,
            self.config.SMTP_USER,
            bool(self.config.SMTP_PASSWORD)
        )
        
        try:
            msg = MIMEMultipart('mixed')  # Changed to 'mixed' for attachments
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Create content part based on type
            if as_attachment and content_type == 'xml':
                # XML as attachment
                from email.mime.base import MIMEBase
                from email import encoders
                
                # Add simple text body
                body = MIMEText("Zie bijlage voor de grofvuil aanvraag (XML format).", 'plain', 'utf-8')
                msg.attach(body)
                
                # Add XML as attachment
                attachment = MIMEBase('application', 'xml')
                attachment.set_payload(content.encode('utf-8'))
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment', filename='grofvuil_aanvraag.xml')
                msg.attach(attachment)
                
                print("   📎 XML attached as file")
            else:
                # Content as body (HTML or inline XML)
                if content_type == 'xml':
                    content_part = MIMEText(content, 'xml', 'utf-8')
                else:  # html
                    content_part = MIMEText(content, 'html', 'utf-8')
                msg.attach(content_part)
            
            log_event('SMTP_CONNECT', 'Connecting to SMTP server', {
                'host': self.config.SMTP_HOST,
                'port': self.config.SMTP_PORT
            })
            
            # Send email
            smtp = self.get_smtp_connection()
            smtp.sendmail(from_email, to_email, msg.as_string())
            
            log_email_result(session_id or 'current_session', content_type, True)
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            log_email_result(session_id or 'current_session', content_type, False, str(e))
            log_error('send_email', e, session_id)
            print(f"❌ Error sending email to {to_email}: {e}")
            return False
    
    def send_internal_notification(self, subject: str, content: str, content_type: str = 'html', session_id: str = 'current_session'):
        """Send internal notification to team with XML or HTML content"""
        # Send only to a.jonker@mainfact.ai
        # XML should be sent as attachment for better compatibility
        as_attachment = (content_type == 'xml')
        
        success = self.send_email(
            to_email=self.config.INTERNAL_EMAIL,
            subject=subject,
            content=content,
            content_type=content_type,
            from_email=self.config.NOREPLY_EMAIL,
            as_attachment=as_attachment,
            session_id=session_id
        )
        
        return success
    
    def send_customer_confirmation(self, customer_email: str, subject: str, html_content: str, session_id: str = 'current_session'):
        """Send confirmation email to customer"""
        return self.send_email(
            to_email=customer_email,
            subject=subject,
            content=html_content,
            content_type='html',
            from_email=self.config.FROM_EMAIL,
            session_id=session_id
        )
    
    def create_grofvuil_request_xml(self, request_data: Dict) -> str:
        """Create XML email for grofvuil request - structured data for system integration"""
        from datetime import datetime
        
        customer = request_data.get('customer', {}) or {}
        name = customer.get('name', 'Onbekend')
        email = customer.get('email', '')

        address_obj = request_data.get('address', {}) or {}
        municipality = address_obj.get('municipality', 'Onbekend')

        items = request_data.get('items', []) or []
        route = request_data.get('route', {}) or {}
        constraints = request_data.get('constraints', {}) or {}

        timestamp = datetime.now(self.timezone).isoformat()

        def esc(value):
            return escape(str(value)) if value is not None else ''

        xml_lines = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<QMLRequest version=\"1.0\">",
            "  <RequestType>GROFVUIL_AFHAAL</RequestType>",
            f"  <Municipality>{esc(municipality)}</Municipality>",
            f"  <Route code=\"{esc(route.get('code', 'HUISRAAD'))}\">{esc(route.get('name', route.get('code', 'Huisraad')))}</Route>",
            "  <Customer>",
            f"    <Name>{esc(name)}</Name>",
            f"    <Email>{esc(email)}</Email>",
            f"    <Phone>{esc(request_data.get('customer', {}).get('phone', ''))}</Phone>",
            "  </Customer>",
            "  <Address>",
            f"    <Street>{esc(address_obj.get('street', ''))}</Street>",
            f"    <HouseNumber>{esc(address_obj.get('house_number', ''))}</HouseNumber>",
            f"    <PostalCode>{esc(address_obj.get('postal_code', ''))}</PostalCode>",
            f"    <City>{esc(address_obj.get('city', ''))}</City>",
            f"    <Municipality>{esc(municipality)}</Municipality>",
            "  </Address>",
            "  <Items>"
        ]

        for item in request_data.get('items', []):
            xml_lines.append("    <Item>")
            xml_lines.append(f"      <Name>{esc(item.get('description', 'Onbekend item'))}</Name>")
            xml_lines.append(f"      <Quantity>{esc(item.get('quantity', 1))}</Quantity>")
            xml_lines.append(
                f"      <Size length_m=\"{esc(item.get('length_m', ''))}\" "
                f"width_m=\"{esc(item.get('width_m', ''))}\" "
                f"height_m=\"{esc(item.get('height_m', ''))}\" "
                f"weight_kg=\"{esc(item.get('weight_kg', ''))}\" />"
            )
            xml_lines.append(f"      <Notes>{esc(item.get('notes', ''))}</Notes>")
            if item.get('category'):
                xml_lines.append(f"      <Category>{esc(item['category'])}</Category>")
            xml_lines.append("    </Item>")

        xml_lines.extend([
            "  </Items>",
            "  <Constraints>",
            f"    <MaxPieceLengthM>{esc(constraints.get('max_piece_length_m'))}</MaxPieceLengthM>",
            f"    <MaxPieceWidthM>{esc(constraints.get('max_piece_width_m'))}</MaxPieceWidthM>",
            f"    <MaxPieceWeightKg>{esc(constraints.get('max_piece_weight_kg'))}</MaxPieceWeightKg>",
            "  </Constraints>",
            "  <RouteData>",
            f"    <EstimatedVolumeM3>{esc(request_data.get('estimated_volume_m3'))}</EstimatedVolumeM3>",
            f"    <MunicipalLimitM3>{esc(request_data.get('municipal_limit_m3'))}</MunicipalLimitM3>",
            f"    <Notes>{esc(request_data.get('special_instructions') or route.get('notes', ''))}</Notes>",
            "  </RouteData>",
            "  <Source>Chatbot-Irado</Source>",
            f"  <Timestamp>{esc(timestamp)}</Timestamp>",
            "</QMLRequest>"
        ])

        return "\n".join(xml_lines)
    
    def create_customer_confirmation_html(self, request_data: Dict) -> str:
        """Create HTML confirmation email for customer with Irado branding"""
        customer = request_data.get('customer', {}) or {}
        address_obj = request_data.get('address', {}) or {}
        municipality = address_obj.get('municipality', '')
        customer_name = customer.get('name', 'klant')
        customer_email = customer.get('email', '')

        address_summary = address_obj.get('full') or f"{address_obj.get('street', '')} {address_obj.get('house_number', '')}, {address_obj.get('postal_code', '')} {address_obj.get('city', '')}"

        items_list = request_data.get('items', []) or []
        items_html = ''.join([
            f'<li style="margin-bottom: 8px;">{escape(str(item))}</li>'
            for item in items_list
        ]) or '<li style="margin-bottom: 8px;">Geen items geregistreerd</li>'

        routes = request_data.get('routes', []) or []
        has_mattresses = any(
            any('matras' in str(it).lower() for it in route.get('items', []))
            for route in routes
        )

        planning_notes_override = request_data.get('planning_notes')

        if planning_notes_override:
            planning_note = f"""
            <div style=\"background: #e0f2fe; border: 1px solid #38bdf8; border-radius: 8px; padding: 20px; margin: 20px 0;\">
                <p style=\"margin: 0; color: #075985; font-weight: 500;\">{escape(str(planning_notes_override))}</p>
            </div>
            """
        elif has_mattresses and municipality in ['Schiedam', 'Vlaardingen']:
            planning_note = """
            <div style=\"background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 20px 0;\">
                <h3 style=\"color: #92400e; margin: 0 0 10px 0; font-size: 16px;\">⚠️ Belangrijk voor matrassen</h3>
                <p style=\"margin: 0; color: #92400e;\">Voor uw aanvraag worden 2 aparte afspraken ingepland: één voor huisraad, één voor matrassen. U ontvangt hiervoor later twee datums van onze planning.</p>
            </div>
            """
        else:
            planning_note = """
            <div style=\"background: #dbeafe; border: 1px solid #3b82f6; border-radius: 8px; padding: 20px; margin: 20px 0;\">
                <p style=\"margin: 0; color: #1e40af; font-weight: 500;\">📅 U ontvangt later de definitieve datum (of datums) van onze planning per e-mail.</p>
            </div>
            """

        route_sections = []
        for route in routes:
            route_items = route.get('items', []) or []
            route_html = ''.join([
                f'<li style="margin-bottom: 6px;">{escape(str(it))}</li>'
                for it in route_items
            ]) or '<li style="margin-bottom: 6px;">Geen items geregistreerd</li>'
            notes = route.get('notes')
            notes_html = f"<p style=\"margin: 0; color: #6b7280; font-size: 14px;\">{escape(str(notes))}</p>" if notes else ''
            route_sections.append(
                f"""
                <div style=\"background: #eef2ff; padding: 20px; border-radius: 8px; margin-bottom: 20px;\">
                    <h3 style=\"color: #312e81; margin: 0 0 12px 0; font-size: 18px; font-weight: 600;\">Route: {escape(route.get('route_name', 'Onbekend'))}</h3>
                    <ul style=\"margin: 0; padding-left: 20px; color: #1f2937;\">{route_html}</ul>
                    {notes_html}
                </div>
                """
            )
        routes_html = '\n'.join(route_sections)

        extra_note_html = ""
        if request_data.get('additional_notes'):
            extra_note_html = f"""
            <div style=\"background: #fff7ed; border: 1px solid #fb923c; border-radius: 8px; padding: 20px; margin-bottom: 25px;\">
                <h3 style=\"color: #c2410c; margin: 0 0 10px 0; font-size: 18px; font-weight: 600;\">Extra informatie</h3>
                <p style=\"margin: 0; color: #7c2d12; font-size: 15px;\">{escape(str(request_data.get('additional_notes')))}</p>
            </div>
            """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Grofvuil Aanvraag Bevestigd - Irado</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            </style>
        </head>
        <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);">
                
                <!-- Header -->
                <div style="background: #0f7ac0; padding: 30px 40px; text-align: center;">
                    <img src="https://www.irado.nl/files/cropped-irado_jubileumlogo25jaar_wit-RGB-middel-2048x696.png" alt="Irado 25 jaar" style="height: 60px; width: auto; max-width: 200px;">
                    <h1 style="color: white; margin: 20px 0 0 0; font-size: 24px; font-weight: 600;">Grofvuil Aanvraag Bevestigd</h1>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px;">
                    <div style="background: #d1fae5; border: 1px solid #10b981; border-radius: 8px; padding: 20px; margin-bottom: 30px; text-align: center;">
                        <h2 style="color: #065f46; margin: 0 0 10px 0; font-size: 20px; font-weight: 600;">✅ Aanvraag Succesvol Ontvangen</h2>
                        <p style="margin: 0; color: #065f46;">Beste {escape(customer_name)}, uw grofvuil aanvraag is succesvol ontvangen en wordt verwerkt.</p>
                    </div>
                    
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h2 style="color: #0f7ac0; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">Uw Gegevens</h2>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151; width: 120px;">Naam:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{escape(customer_name)}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151;">Adres:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{escape(address_summary)}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151;">E-mail:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{escape(customer_email)}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151;">Gemeente:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{escape(municipality)}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h2 style="color: #0f7ac0; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">Overzicht van uw melding</h2>
                        <ul style="margin: 0; padding-left: 20px; color: #1f2937;">
                            {items_html}
                        </ul>
                    </div>

                    {routes_html}
                    
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h2 style="color: #0f7ac0; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">Belangrijke Informatie</h2>
                        <ul style="margin: 0; padding-left: 20px; color: #1f2937;">
                            <li style="margin-bottom: 8px;"><strong>Buiten zetten:</strong> tussen 05:00 – 07:30 uur</li>
                            <li style="margin-bottom: 8px;"><strong>Ophalen:</strong> tussen 07:30 – 16:00 uur</li>
                            <li style="margin-bottom: 8px;"><strong>Locatie:</strong> voor de woning aan doorgaande weg (niet stoep/erf, goed bereikbaar)</li>
                            <li style="margin-bottom: 8px;"><strong>Afmetingen:</strong> Max. lengte: 1,80 m, max. breedte: 0,90 m, max. gewicht: 30 kg per stuk</li>
                        </ul>
                    </div>
                    
                    {planning_note}
                    {extra_note_html}

                    <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; margin-top: 30px;">
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">
                            <em>Deze bevestiging is automatisch gegenereerd door de Irado Chatbot</em>
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 20px 40px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; color: #6b7280; font-size: 14px;">
                        Met vriendelijke groet,<br>
                        <strong>Het Irado team</strong><br>
                        <em>25 jaar ervaring in afvalinzameling en recycling</em>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
