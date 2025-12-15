#!/usr/bin/env python3
"""
Test script to verify email functionality
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service import EmailService
from config import Config

def test_email_configuration():
    """Test email configuration"""
    print("Testing Email Configuration...")
    print("=" * 50)
    
    config = Config()
    
    print(f"Internal Email: {config.INTERNAL_EMAIL}")
    print(f"From Email: {config.FROM_EMAIL}")
    print(f"NoReply Email: {config.NOREPLY_EMAIL}")
    
    # Check if j.moolenaar is removed
    if hasattr(config, 'INTERNAL_EMAIL_2'):
        print(f"INTERNAL_EMAIL_2 still exists: {config.INTERNAL_EMAIL_2}")
    else:
        print("✓ INTERNAL_EMAIL_2 removed")
    
    print("\n" + "=" * 50)

def test_email_service():
    """Test email service functionality"""
    print("Testing Email Service...")
    print("=" * 50)
    
    try:
        email_service = EmailService()
        
        # Test internal notification (this will actually send an email)
        print("Testing internal notification...")
        subject = "Test Email - Chatbot Upgrade"
        html_content = """
        <html>
        <body>
            <h2>Test Email from Chatbot</h2>
            <p>This is a test email to verify the email functionality works correctly.</p>
            <p>If you receive this email, the chatbot email system is working properly.</p>
        </body>
        </html>
        """
        
        success = email_service.send_internal_notification(subject, html_content)
        
        if success:
            print("✓ Internal notification sent successfully")
        else:
            print("✗ Failed to send internal notification")
            
    except Exception as e:
        print(f"✗ Error testing email service: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    print("Irado Chatbot Email Functionality Test")
    print("=" * 50)
    
    try:
        test_email_configuration()
        test_email_service()
        print("\nAll email tests completed!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)

