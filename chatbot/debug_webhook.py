#!/usr/bin/env python3
"""
Debug script to test the webhook endpoint
"""
import requests
import json
import base64

def test_webhook():
    """Test the webhook endpoint with detailed debugging"""
    
    # Configuration
    base_url = "http://localhost:5000"
    username = "irado"
    password = "20Irado25!"
    
    # Create basic auth header
    credentials = f"{username}:{password}"
    auth_header = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Basic {auth_header}'
    }
    
    print("Testing Irado Chatbot Webhook...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✓ Health check passed")
        else:
            print("✗ Health check failed")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False
    
    # Test 2: Chat message with detailed debugging
    print("\n2. Testing chat message...")
    session_id = f"debug_session_{int(__import__('time').time())}"
    
    chat_data = {
        "sessionId": session_id,
        "action": "sendMessage",
        "chatInput": "ik wil een grofvuil afspraak"
    }
    
    print(f"Request URL: {base_url}/webhook/chat")
    print(f"Request headers: {headers}")
    print(f"Request data: {json.dumps(chat_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/webhook/chat",
            headers=headers,
            json=chat_data,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Chat message sent successfully")
            print(f"Output: {result.get('output', 'No output')}")
        else:
            print(f"✗ Chat message failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Chat message error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Debug test completed!")
    return True

if __name__ == '__main__':
    test_webhook()



