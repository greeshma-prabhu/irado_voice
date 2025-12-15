#!/usr/bin/env python3
"""
Test script for address validation functionality
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from address_validation import AddressValidationService

def test_address_validation():
    """Test the address validation service"""
    print("Testing Address Validation Service...")
    print("=" * 50)
    
    # Initialize the service
    validator = AddressValidationService()
    
    # Test cases with real addresses
    test_cases = [
        {
            "name": "Valid address in Amsterdam (outside service area)",
            "postcode": "1017XN",
            "huisnummer": "42",
            "expected_valid": True,
            "expected_service_area": False
        },
        {
            "name": "Invalid postcode format",
            "postcode": "12345",
            "huisnummer": "42",
            "expected_valid": False,
            "expected_service_area": False
        },
        {
            "name": "Test with KOAD address from CSV",
            "postcode": "3136HN",
            "huisnummer": "464",
            "expected_valid": True,
            "expected_service_area": True,
            "expected_blocked": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
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
            
            # Check if results match expectations
            if result.is_valid == test_case['expected_valid']:
                print("  ✓ Validity check passed")
            else:
                print(f"  ✗ Validity check failed (expected {test_case['expected_valid']}, got {result.is_valid})")
            
            if result.is_in_service_area == test_case['expected_service_area']:
                print("  ✓ Service area check passed")
            else:
                print(f"  ✗ Service area check failed (expected {test_case['expected_service_area']}, got {result.is_in_service_area})")
                
        except Exception as e:
            print(f"  ✗ Error during validation: {e}")
    
    # Test KOAD data loading
    print(f"\nKOAD Data Test:")
    print(f"  - KOAD entries loaded: {len(validator.koad_data)}")
    
    # Test service area info
    print(f"\nService Area Info:")
    service_areas = validator.get_service_area_info()
    for municipality, postcodes in service_areas.items():
        print(f"  - {municipality}: {len(postcodes)} postcode ranges")
    
    print("\n" + "=" * 50)
    print("Address validation testing completed!")

def test_address_from_text():
    """Test address extraction from text"""
    print("\nTesting Address Extraction from Text...")
    print("=" * 50)
    
    validator = AddressValidationService()
    
    test_texts = [
        "Mijn adres is Spechtlaan 464, 3136HN Vlaardingen",
        "Ik woon op 1017XN 42 in Amsterdam",
        "Adres: 2900AB 5, Capelle aan den IJssel",
        "Geen geldig adres hier"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {text}")
        
        try:
            result = validator.validate_address_from_text(text)
            
            print(f"Result:")
            print(f"  - Valid: {result.is_valid}")
            print(f"  - Service Area: {result.is_in_service_area}")
            print(f"  - Postcode: {result.postcode}")
            print(f"  - Huisnummer: {result.huisnummer}")
            print(f"  - Street: {result.straat}")
            print(f"  - City: {result.woonplaats}")
            
        except Exception as e:
            print(f"  ✗ Error during text extraction: {e}")
    
    print("\n" + "=" * 50)
    print("Address text extraction testing completed!")

if __name__ == "__main__":
    print("Irado Chatbot Address Validation Test")
    print("=" * 50)
    
    try:
        test_address_validation()
        test_address_from_text()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)
