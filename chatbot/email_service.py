"""
Email service for sending notifications and confirmations
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from config import Config

class EmailService:
    """Handles email sending for the chatbot"""
    
    def __init__(self):
        self.config = Config()
        self.smtp_server = None
    
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
    
    def send_email(self, to_email: str, subject: str, content: str, content_type: str = 'html', from_email: str = None):
        """Send email to customer with XML or HTML content"""
        if not from_email:
            from_email = self.config.FROM_EMAIL
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Create content part based on type
            if content_type == 'xml':
                content_part = MIMEText(content, 'xml', 'utf-8')
            else:  # html
                content_part = MIMEText(content, 'html', 'utf-8')
            
            msg.attach(content_part)
            
            # Send email
            smtp = self.get_smtp_connection()
            smtp.sendmail(from_email, to_email, msg.as_string())
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False
    
    def send_internal_notification(self, subject: str, content: str, content_type: str = 'html'):
        """Send internal notification to team with XML or HTML content"""
        # Send only to a.jonker@mainfact.ai
        success = self.send_email(
            to_email=self.config.INTERNAL_EMAIL,
            subject=subject,
            content=content,
            content_type=content_type,
            from_email=self.config.NOREPLY_EMAIL
        )
        
        return success
    
    def send_customer_confirmation(self, customer_email: str, subject: str, html_content: str):
        """Send confirmation email to customer"""
        return self.send_email(
            to_email=customer_email,
            subject=subject,
            html_content=html_content,
            from_email=self.config.FROM_EMAIL
        )
    
    def create_grofvuil_request_email(self, request_data: Dict) -> str:
        """Create HTML email for grofvuil request with Irado branding"""
        items_list = request_data.get('items', [])
        items_html = ''.join([f'<li style="margin-bottom: 8px;">{item}</li>' for item in items_list])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Grofvuil Aanvraag - Irado</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            </style>
        </head>
        <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);">
                
                <!-- Header -->
                <div style="background: #0f7ac0; padding: 30px 40px; text-align: center;">
                    <img src="https://www.irado.nl/files/cropped-irado_jubileumlogo25jaar_wit-RGB-middel-2048x696.png" alt="Irado 25 jaar" style="height: 60px; width: auto; max-width: 200px;">
                    <h1 style="color: white; margin: 20px 0 0 0; font-size: 24px; font-weight: 600;">Nieuwe Grofvuil Aanvraag</h1>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px;">
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h2 style="color: #0f7ac0; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">Klantgegevens</h2>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151; width: 120px;">Naam:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{request_data.get('name', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151;">Adres:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{request_data.get('address', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151;">E-mail:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{request_data.get('email', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151;">Gemeente:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{request_data.get('municipality', 'N/A')}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h2 style="color: #0f7ac0; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">Afvalsoorten</h2>
                        <ul style="margin: 0; padding-left: 20px; color: #1f2937;">
                            {items_html}
                        </ul>
                    </div>
                    
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h2 style="color: #0f7ac0; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">Bijzonderheden</h2>
                        <p style="margin: 0; color: #1f2937;">{request_data.get('notes', 'Geen bijzonderheden')}</p>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">
                            <em>Deze aanvraag is automatisch gegenereerd door de Irado Chatbot</em>
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 20px 40px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; color: #6b7280; font-size: 14px;">
                        Irado - 25 jaar ervaring in afvalinzameling en recycling
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def create_customer_confirmation_email(self, request_data: Dict) -> str:
        """Create HTML confirmation email for customer with Irado branding"""
        items_list = request_data.get('items', [])
        items_html = ''.join([f'<li style="margin-bottom: 8px;">{item}</li>' for item in items_list])
        
        # Special handling for mattresses in Schiedam/Vlaardingen
        municipality = request_data.get('municipality', '')
        has_mattresses = any('matras' in item.lower() for item in items_list)
        
        if has_mattresses and municipality in ['Schiedam', 'Vlaardingen']:
            planning_note = """
            <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="color: #92400e; margin: 0 0 10px 0; font-size: 16px;">⚠️ Belangrijk voor matrassen</h3>
                <p style="margin: 0; color: #92400e;">Voor uw aanvraag worden 2 aparte afspraken ingepland: één voor huisraad, één voor matrassen. 
                U ontvangt hiervoor later 2 datums van onze planning.</p>
            </div>
            """
        else:
            planning_note = """
            <div style="background: #dbeafe; border: 1px solid #3b82f6; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <p style="margin: 0; color: #1e40af; font-weight: 500;">📅 U ontvangt later de definitieve datum van onze planning per e-mail.</p>
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
                        <p style="margin: 0; color: #065f46;">Beste {request_data.get('name', 'klant')}, uw grofvuil aanvraag is succesvol ontvangen en wordt verwerkt.</p>
                    </div>
                    
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h2 style="color: #0f7ac0; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">Uw Gegevens</h2>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151; width: 120px;">Naam:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{request_data.get('name', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151;">Adres:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{request_data.get('address', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151;">E-mail:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{request_data.get('email', 'N/A')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: 500; color: #374151;">Gemeente:</td>
                                <td style="padding: 8px 0; color: #1f2937;">{request_data.get('municipality', 'N/A')}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h2 style="color: #0f7ac0; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">Afvalsoorten</h2>
                        <ul style="margin: 0; padding-left: 20px; color: #1f2937;">
                            {items_html}
                        </ul>
                    </div>
                    
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
