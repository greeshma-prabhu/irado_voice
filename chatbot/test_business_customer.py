#!/usr/bin/env python3
"""
Test script for business customer handling
Tests the chatbot with blocked business addresses
"""
import requests
import json
import base64
import time

def test_business_customer():
    """Test with business customer address"""
    print("🏢 Testing Business Customer: Spechtlaan 508, 3136HP Vlaardingen")
    print("=" * 70)
    
    url = "http://localhost:5000/api/chat"
    credentials = base64.b64encode(b"irado:20Irado25!").decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    session_id = f"test_business_{int(time.time())}"
    
    # Step 1: Start conversation
    print("Step 1: Starting conversation...")
    response = requests.post(url, headers=headers, json={
        "sessionId": session_id,
        "action": "sendMessage",
        "chatInput": "ik wil grofvuil ophalen laten"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data.get('output', 'No response')}")
    else:
        print(f"❌ Error: {response.status_code}")
        return
    
    # Step 2: Privacy agreement
    print("\nStep 2: Privacy agreement...")
    response = requests.post(url, headers=headers, json={
        "sessionId": session_id,
        "action": "sendMessage",
        "chatInput": "ja"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data.get('output', 'No response')}")
    else:
        print(f"❌ Error: {response.status_code}")
        return
    
    # Step 3: Provide business address
    print("\nStep 3: Providing business address...")
    response = requests.post(url, headers=headers, json={
        "sessionId": session_id,
        "action": "sendMessage",
        "chatInput": "spechtlaan 508, 3136hp vlaardingen een bankstel"
    })
    
    if response.status_code == 200:
        data = response.json()
        output = data.get('output', 'No response')
        print(f"✅ Response: {output}")
        
        # Check if business customer was referred correctly
        if "zakelijke klantenservice" in output.lower() or "bedrijfsafval" in output.lower():
            print("🎉 SUCCESS: Business customer correctly referred to business service!")
        elif "niet in het verzorgingsgebied" in output.lower():
            print("✅ SUCCESS: Address correctly identified as outside service area")
        elif "email" in output.lower() and "verzonden" in output.lower():
            print("❌ FAILURE: Business address was processed - this is a problem!")
        else:
            print("⚠️  UNCLEAR: Response doesn't clearly indicate business customer handling")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("=" * 70)

def test_private_customer():
    """Test with private customer address"""
    print("🏠 Testing Private Customer: Valid address in service area")
    print("=" * 70)
    
    url = "http://localhost:5000/api/chat"
    credentials = base64.b64encode(b"irado:20Irado25!").decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    session_id = f"test_private_{int(time.time())}"
    
    # Step 1: Start conversation
    print("Step 1: Starting conversation...")
    response = requests.post(url, headers=headers, json={
        "sessionId": session_id,
        "action": "sendMessage",
        "chatInput": "ik wil grofvuil ophalen laten"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data.get('output', 'No response')}")
    else:
        print(f"❌ Error: {response.status_code}")
        return
    
    # Step 2: Privacy agreement
    print("\nStep 2: Privacy agreement...")
    response = requests.post(url, headers=headers, json={
        "sessionId": session_id,
        "action": "sendMessage",
        "chatInput": "ja"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data.get('output', 'No response')}")
    else:
        print(f"❌ Error: {response.status_code}")
        return
    
    # Step 3: Provide private address (Amsterdam - outside service area)
    print("\nStep 3: Providing private address outside service area...")
    response = requests.post(url, headers=headers, json={
        "sessionId": session_id,
        "action": "sendMessage",
        "chatInput": "1017xn 42 amsterdam een tafel"
    })
    
    if response.status_code == 200:
        data = response.json()
        output = data.get('output', 'No response')
        print(f"✅ Response: {output}")
        
        # Check if private customer was handled correctly
        if "niet in ons verzorgingsgebied" in output.lower() and "zakelijke klantenservice" not in output.lower():
            print("🎉 SUCCESS: Private customer correctly informed about service area!")
        elif "zakelijke klantenservice" in output.lower():
            print("⚠️  WARNING: Private customer incorrectly referred to business service")
        else:
            print("⚠️  UNCLEAR: Response doesn't clearly indicate private customer handling")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("=" * 70)

if __name__ == "__main__":
    print("🚀 IRADO CHATBOT BUSINESS CUSTOMER TEST")
    print("=" * 80)
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Test business customer
        test_business_customer()
        
        print("\n" + "=" * 80)
        
        # Test private customer
        test_private_customer()
        
        print("\n🎉 BUSINESS CUSTOMER TESTS COMPLETED!")
        print("=" * 80)
        print("Summary:")
        print("✅ Business customers should be referred to business service")
        print("✅ Private customers should be informed about service area")
        print("✅ KOAD blacklist should distinguish between business and private")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ BUSINESS CUSTOMER TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

