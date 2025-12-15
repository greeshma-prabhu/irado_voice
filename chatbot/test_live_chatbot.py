#!/usr/bin/env python3
"""
Live test script for the chatbot API
Tests the actual chatbot with blocked addresses
"""
import requests
import json
import base64
import time

def test_chatbot_with_blocked_address():
    """Test chatbot with a blocked address"""
    print("🤖 Testing Chatbot with Blocked Address...")
    print("=" * 50)
    
    # API endpoint
    url = "http://localhost:5000/api/chat"
    
    # Authentication
    username = "irado"
    password = "20Irado25!"
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    # Test conversation with blocked address
    conversation = [
        {
            "sessionId": f"test_blocked_{int(time.time())}",
            "action": "sendMessage",
            "chatInput": "ik wil grofvuil ophalen laten"
        },
        {
            "sessionId": f"test_blocked_{int(time.time())}",
            "action": "sendMessage", 
            "chatInput": "ja"
        },
        {
            "sessionId": f"test_blocked_{int(time.time())}",
            "action": "sendMessage",
            "chatInput": "spechtlaan 508, 3136hp vlaardingen een bankstel"
        },
        {
            "sessionId": f"test_blocked_{int(time.time())}",
            "action": "sendMessage",
            "chatInput": "naam armin jonker. armin@fam-jonker.de"
        },
        {
            "sessionId": f"test_blocked_{int(time.time())}",
            "action": "sendMessage",
            "chatInput": "ja"
        }
    ]
    
    print("Starting conversation test...")
    
    for i, message in enumerate(conversation, 1):
        print(f"\n--- Message {i} ---")
        print(f"Input: {message['chatInput']}")
        
        try:
            response = requests.post(url, headers=headers, json=message, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                output = data.get('output', 'No response')
                print(f"Response: {output}")
                
                # Check if address validation worked
                if "niet in het verzorgingsgebied" in output.lower() or "niet toegestaan" in output.lower():
                    print("✅ Address correctly blocked!")
                    break
                elif "email" in output.lower() and "verzonden" in output.lower():
                    print("❌ Address was not blocked - this is a problem!")
                    break
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            break
        
        # Small delay between messages
        time.sleep(1)
    
    print("\n" + "=" * 50)

def test_chatbot_with_valid_address():
    """Test chatbot with a valid address"""
    print("🤖 Testing Chatbot with Valid Address...")
    print("=" * 50)
    
    # API endpoint
    url = "http://localhost:5000/api/chat"
    
    # Authentication
    username = "irado"
    password = "20Irado25!"
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    # Test conversation with valid address
    conversation = [
        {
            "sessionId": f"test_valid_{int(time.time())}",
            "action": "sendMessage",
            "chatInput": "ik wil grofvuil ophalen laten"
        },
        {
            "sessionId": f"test_valid_{int(time.time())}",
            "action": "sendMessage", 
            "chatInput": "ja"
        },
        {
            "sessionId": f"test_valid_{int(time.time())}",
            "action": "sendMessage",
            "chatInput": "1017xn 42 amsterdam een tafel"
        },
        {
            "sessionId": f"test_valid_{int(time.time())}",
            "action": "sendMessage",
            "chatInput": "naam test user. test@example.com"
        },
        {
            "sessionId": f"test_valid_{int(time.time())}",
            "action": "sendMessage",
            "chatInput": "ja"
        }
    ]
    
    print("Starting conversation test with valid address...")
    
    for i, message in enumerate(conversation, 1):
        print(f"\n--- Message {i} ---")
        print(f"Input: {message['chatInput']}")
        
        try:
            response = requests.post(url, headers=headers, json=message, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                output = data.get('output', 'No response')
                print(f"Response: {output}")
                
                # Check if address validation worked
                if "niet in het verzorgingsgebied" in output.lower():
                    print("✅ Address correctly identified as outside service area!")
                    break
                elif "email" in output.lower() and "verzonden" in output.lower():
                    print("❌ Address was processed - this might be expected for outside service area")
                    break
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            break
        
        # Small delay between messages
        time.sleep(1)
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    print("🚀 IRADO CHATBOT LIVE TEST")
    print("=" * 60)
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Test with blocked address
        test_chatbot_with_blocked_address()
        
        print("\n" + "=" * 60)
        
        # Test with valid address outside service area
        test_chatbot_with_valid_address()
        
        print("\n🎉 LIVE TESTS COMPLETED!")
        print("=" * 60)
        print("Check the responses above to verify:")
        print("✅ Blocked addresses are rejected")
        print("✅ Valid addresses are processed correctly")
        print("✅ Email system works")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ LIVE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

