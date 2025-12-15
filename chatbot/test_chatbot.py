#!/usr/bin/env python3
"""
Test script for the Irado Chatbot
"""
import requests
import json
import base64
import time

def test_chatbot():
    """Test the chatbot functionality"""
    
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
    
    print("Testing Irado Chatbot...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✓ Health check passed")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False
    
    # Test 2: Chat message
    print("\n2. Testing chat message...")
    session_id = f"test_session_{int(time.time())}"
    
    chat_data = {
        "sessionId": session_id,
        "action": "sendMessage",
        "chatInput": "Hallo, ik wil graag grofvuil aanmelden"
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook/chat",
            headers=headers,
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Chat message sent successfully")
            print(f"Response: {result.get('output', 'No output')[:100]}...")
        else:
            print(f"✗ Chat message failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Chat message error: {e}")
        return False
    
    # Test 3: Follow-up message
    print("\n3. Testing follow-up message...")
    
    followup_data = {
        "sessionId": session_id,
        "action": "sendMessage", 
        "chatInput": "Ik heb een oude bank en een matras"
    }
    
    try:
        response = requests.post(
            f"{base_url}/webhook/chat",
            headers=headers,
            json=followup_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Follow-up message sent successfully")
            print(f"Response: {result.get('output', 'No output')[:100]}...")
        else:
            print(f"✗ Follow-up message failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Follow-up message error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    return True

if __name__ == '__main__':
    success = test_chatbot()
    if success:
        print("✓ Chatbot is working correctly!")
    else:
        print("✗ Chatbot has issues!")



