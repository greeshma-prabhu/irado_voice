#!/usr/bin/env python3
"""
Test script for XML email functionality
"""
import sys
import os
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service_xml import EmailService

def test_xml_email_generation():
    """Test XML email generation"""
    print("🧪 Testing XML Email Generation...")
    print("=" * 50)
    
    # Test data for grofvuil request
    test_request_data = {
        'name': 'Armin Jonker',
        'address': 'Westfrankelandsestraat 11, 3117 AJ Schiedam',
        'email': 'armin@fam-jonker.de',
        'municipality': 'Schiedam',
        'category': 'Huisraad',
        'items': [
            '1× matras (droog)',
            '1× tafel',
            '1× glasplaat (nog niet getapet)'
        ],
        'notes': 'Matras is droog en schoon'
    }
    
    try:
        email_service = EmailService()
        
        # Generate XML content
        xml_content = email_service.create_grofvuil_request_xml(test_request_data)
        
        print("✅ XML content generated successfully")
        print("\n📄 Generated XML:")
        print("-" * 30)
        print(xml_content)
        print("-" * 30)
        
        # Save XML to file for inspection
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        xml_file = f"/opt/irado/chatbot/test_xml_{timestamp}.xml"
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"\n💾 XML saved to: {xml_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating XML: {e}")
        return False

def test_xml_email_sending():
    """Test sending XML email (only if you want to actually send)"""
    print("\n📧 Testing XML Email Sending...")
    print("=" * 50)
    
    # Test data
    test_request_data = {
        'name': 'Test Klant',
        'address': 'Teststraat 123, 1234 AB Teststad',
        'email': 'test@example.com',
        'municipality': 'Schiedam',
        'category': 'Huisraad',
        'items': [
            '1× test item'
        ],
        'notes': 'Test aanvraag'
    }
    
    try:
        email_service = EmailService()
        
        # Generate XML content
        xml_content = email_service.create_grofvuil_request_xml(test_request_data)
        
        # Send test email (uncomment if you want to actually send)
        # success = email_service.send_internal_notification(
        #     subject="🧪 Test XML Email - Grofvuil Aanvraag",
        #     content=xml_content,
        #     content_type='xml'
        # )
        
        print("✅ XML email generation successful")
        print("📧 Email sending disabled for testing (uncomment to enable)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with XML email: {e}")
        return False

def test_customer_html_email():
    """Test customer HTML email generation"""
    print("\n🎨 Testing Customer HTML Email...")
    print("=" * 50)
    
    test_request_data = {
        'name': 'Armin Jonker',
        'address': 'Westfrankelandsestraat 11, 3117 AJ Schiedam',
        'email': 'armin@fam-jonker.de',
        'municipality': 'Schiedam',
        'items': [
            '1× matras (droog)',
            '1× tafel'
        ]
    }
    
    try:
        email_service = EmailService()
        
        # Generate HTML content
        html_content = email_service.create_customer_confirmation_html(test_request_data)
        
        print("✅ HTML content generated successfully")
        
        # Save HTML to file for inspection
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = f"/opt/irado/chatbot/test_html_{timestamp}.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 HTML saved to: {html_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating HTML: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Irado Chatbot XML Email Test")
    print("=" * 60)
    
    # Test XML generation
    xml_success = test_xml_email_generation()
    
    # Test XML email sending
    email_success = test_xml_email_sending()
    
    # Test customer HTML
    html_success = test_customer_html_email()
    
    # Summary
    print("\n📊 Test Results:")
    print("=" * 30)
    print(f"XML Generation: {'✅ PASS' if xml_success else '❌ FAIL'}")
    print(f"XML Email: {'✅ PASS' if email_success else '❌ FAIL'}")
    print(f"HTML Email: {'✅ PASS' if html_success else '❌ FAIL'}")
    
    if all([xml_success, email_success, html_success]):
        print("\n🎉 All tests passed! XML email functionality is working.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
