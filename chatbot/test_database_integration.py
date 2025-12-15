#!/usr/bin/env python3
"""
Test script voor database integratie
Test of de migratie van CSV naar database succesvol is
"""

import sys
import os
sys.path.append('/opt/irado/chatbot')

from database_service import BedrijfsklantenDatabaseService
from address_validation import AddressValidationService
import requests
import json

def test_database_connection():
    """Test database verbinding"""
    print("🧪 Testing database connection...")
    try:
        db = BedrijfsklantenDatabaseService()
        stats = db.get_bedrijfsklanten_stats()
        print(f"✅ Database connection successful")
        print(f"   Total records: {stats.get('totaal_klanten', 0)}")
        print(f"   Active records: {stats.get('actieve_klanten', 0)}")
        print(f"   Unique postcodes: {stats.get('unieke_postcodes', 0)}")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_bedrijfsklant_check():
    """Test bedrijfsklant check functionaliteit"""
    print("\n🧪 Testing bedrijfsklant check...")
    try:
        db = BedrijfsklantenDatabaseService()
        
        # Test met een bekend adres uit de data
        is_blocked = db.is_bedrijfsklant('3136HN', '464')
        print(f"✅ Bedrijfsklant check successful: {is_blocked}")
        
        # Test met een onbekend adres
        is_not_blocked = db.is_bedrijfsklant('1017XN', '999')
        print(f"✅ Non-bedrijfsklant check successful: {is_not_blocked}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Bedrijfsklant check failed: {e}")
        return False

def test_address_validation():
    """Test address validation service"""
    print("\n🧪 Testing address validation...")
    try:
        validator = AddressValidationService()
        
        # Test met bedrijfsklant adres
        result = validator.validate_address('3136HN', '464')
        print(f"✅ Address validation successful")
        print(f"   Is valid: {result.is_valid}")
        print(f"   Is in service area: {result.is_in_service_area}")
        print(f"   Is bedrijfsklant: {validator.is_address_blocked('3136HN', '464')}")
        
        return True
    except Exception as e:
        print(f"❌ Address validation failed: {e}")
        return False

def test_dashboard_api():
    """Test dashboard API endpoints"""
    print("\n🧪 Testing dashboard API...")
    try:
        # Test health endpoint
        response = requests.get('http://localhost:3256/health', timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard health check successful")
        else:
            print(f"❌ Dashboard health check failed: {response.status_code}")
            return False
        
        # Test KOAD API endpoint
        response = requests.get('http://localhost:3256/api/koad', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ KOAD API successful: {data.get('total', 0)} records")
            else:
                print(f"❌ KOAD API failed: {data.get('error')}")
                return False
        else:
            print(f"❌ KOAD API failed: {response.status_code}")
            return False
        
        # Test search endpoint
        response = requests.get('http://localhost:3256/api/koad/search?q=Spechtlaan', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Search API successful: {data.get('total', 0)} results")
            else:
                print(f"❌ Search API failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Search API failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Dashboard API test failed: {e}")
        return False

def test_csv_upload():
    """Test CSV upload functionaliteit"""
    print("\n🧪 Testing CSV upload...")
    try:
        # Maak een test CSV
        test_csv = """KOAD-nummer,KOAD-str,KOAD-pc,KOAD-huisaand,KOAD-huisnr,KOAD-etage,KOAD-naam,KOAD-actief,KOAD-inwoner
999999,Teststraat,1017XN,,123,,Test Bedrijf,1,1
999998,Testlaan,1017XN,,456,,Test Bedrijf 2,1,1"""
        
        # Test upload via API
        files = {'file': ('test.csv', test_csv, 'text/csv')}
        response = requests.post('http://localhost:3256/api/koad/upload', files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ CSV upload successful: {data.get('message')}")
                return True
            else:
                print(f"❌ CSV upload failed: {data.get('error')}")
                return False
        else:
            print(f"❌ CSV upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CSV upload test failed: {e}")
        return False

def main():
    """Hoofdfunctie voor alle tests"""
    print("🧪 Testing Database Integration")
    print("==============================")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Bedrijfsklant Check", test_bedrijfsklant_check),
        ("Address Validation", test_address_validation),
        ("Dashboard API", test_dashboard_api),
        ("CSV Upload", test_csv_upload)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database migration successful!")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)





