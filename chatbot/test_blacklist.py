#!/usr/bin/env python3
"""
Test script to verify KOAD blacklist functionality
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from address_validation import AddressValidationService

def test_blacklist():
    """Test the KOAD blacklist functionality"""
    print("Testing KOAD Blacklist Functionality...")
    print("=" * 50)
    
    # Initialize the service
    validator = AddressValidationService()
    
    # Test with the exact address from your example
    test_addresses = [
        {
            "name": "Blocked address from KOAD (Spechtlaan 508, 3136HP)",
            "postcode": "3136HP",
            "huisnummer": "508",
            "expected_blocked": True
        },
        {
            "name": "Blocked address from KOAD (Spechtlaan 464, 3136HN)",
            "postcode": "3136HN", 
            "huisnummer": "464",
            "expected_blocked": True
        },
        {
            "name": "Valid address in Amsterdam (not blocked)",
            "postcode": "1017XN",
            "huisnummer": "42",
            "expected_blocked": False
        }
    ]
    
    for i, test_case in enumerate(test_addresses, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Postcode: {test_case['postcode']}, Huisnummer: {test_case['huisnummer']}")
        
        try:
            result = validator.validate_address(test_case['postcode'], test_case['huisnummer'])
            
            print(f"Result:")
            print(f"  - Valid: {result.is_valid}")
            print(f"  - Service Area: {result.is_in_service_area}")
            print(f"  - Municipality: {result.service_area_municipality}")
            print(f"  - Street: {result.straat}")
            print(f"  - City: {result.woonplaats}")
            
            # Check if address is blocked
            is_blocked = not result.is_in_service_area and result.is_valid
            print(f"  - Blocked: {is_blocked}")
            
            if is_blocked == test_case['expected_blocked']:
                print("  ✓ Blacklist check passed")
            else:
                print(f"  ✗ Blacklist check failed (expected {test_case['expected_blocked']}, got {is_blocked})")
                
        except Exception as e:
            print(f"  ✗ Error during validation: {e}")
    
    # Test direct KOAD lookup
    print(f"\nDirect KOAD Lookup Test:")
    koad_key = "3136HP_508"
    is_in_koad = koad_key in validator.koad_data
    print(f"  - Key '{koad_key}' in KOAD: {is_in_koad}")
    
    koad_key2 = "3136HN_464"
    is_in_koad2 = koad_key2 in validator.koad_data
    print(f"  - Key '{koad_key2}' in KOAD: {is_in_koad2}")
    
    print("\n" + "=" * 50)
    print("KOAD blacklist testing completed!")

if __name__ == "__main__":
    print("Irado Chatbot KOAD Blacklist Test")
    print("=" * 50)
    
    try:
        test_blacklist()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)

