"""
Address validation service for the Irado Chatbot
Validates Dutch addresses using Open Postcode API and checks service area coverage
"""
import requests
import re
import csv
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config import Config
from database_service import BedrijfsklantenDatabaseService

@dataclass
class AddressInfo:
    """Data class for address information"""
    postcode: str
    huisnummer: str
    straat: str
    woonplaats: str
    gemeente: str
    provincie: str
    latitude: float
    longitude: float
    is_valid: bool
    is_in_service_area: bool
    service_area_municipality: Optional[str] = None

class AddressValidationService:
    """Service for validating Dutch addresses and checking service area coverage"""
    
    def __init__(self):
        self.config = Config()
        self.open_postcode_base_url = "https://openpostcode.nl/api"
        self.service_areas = self._load_service_areas()
        self.database_service = BedrijfsklantenDatabaseService()
    
    def _load_service_areas(self) -> Dict[str, List[str]]:
        """Load service area configuration from config"""
        return {
            'Capelle aan den IJssel': ['2900', '2901', '2902', '2903', '2904', '2905', '2906', '2907', '2908', '2909'],
            'Schiedam': ['3100', '3101', '3102', '3103', '3104', '3105', '3106', '3107', '3108', '3109', 
                        '3110', '3111', '3112', '3113', '3114', '3115', '3116', '3117', '3118', '3119',
                        '3120', '3121', '3122', '3123', '3124', '3125'],
            'Vlaardingen': ['3130', '3131', '3132', '3133', '3134', '3135', '3136', '3137', '3138']
        }
    
    def _is_bedrijfsklant(self, postcode: str, huisnummer: str) -> bool:
        """Check if address is a bedrijfsklant using database"""
        try:
            return self.database_service.is_bedrijfsklant(postcode, huisnummer)
        except Exception as e:
            print(f"Error checking bedrijfsklant status: {e}")
            return False
    
    def _normalize_postcode(self, postcode: str) -> str:
        """Normalize Dutch postcode format (remove spaces, convert to uppercase)"""
        if not postcode:
            return ""
        # Remove spaces and convert to uppercase
        normalized = re.sub(r'\s+', '', postcode.upper())
        # Ensure format is 4 digits + 2 letters
        if re.match(r'^\d{4}[A-Z]{2}$', normalized):
            return normalized
        return postcode.upper()
    
    def _normalize_huisnummer(self, huisnummer: str) -> str:
        """Normalize house number (remove spaces, convert to string)"""
        if not huisnummer:
            return ""
        return str(huisnummer).strip()
    
    def validate_address(self, postcode: str, huisnummer: str) -> AddressInfo:
        """
        Validate a Dutch address using Open Postcode API
        
        Args:
            postcode: Dutch postcode (e.g., "1017XN")
            huisnummer: House number (e.g., "42")
            
        Returns:
            AddressInfo object with validation results
        """
        # Normalize inputs
        normalized_postcode = self._normalize_postcode(postcode)
        normalized_huisnummer = self._normalize_huisnummer(huisnummer)
        
        # Initialize result with default values
        result = AddressInfo(
            postcode=normalized_postcode,
            huisnummer=normalized_huisnummer,
            straat="",
            woonplaats="",
            gemeente="",
            provincie="",
            latitude=0.0,
            longitude=0.0,
            is_valid=False,
            is_in_service_area=False
        )
        
        # Validate postcode format
        if not re.match(r'^\d{4}[A-Z]{2}$', normalized_postcode):
            return result
        
        # Check if address is a bedrijfsklant first
        if self._is_bedrijfsklant(normalized_postcode, normalized_huisnummer):
            # Address is a bedrijfsklant - return immediately
            result.is_valid = True  # Address exists but is bedrijfsklant
            result.is_in_service_area = False
            result.service_area_municipality = None
            return result
        
        # Call Open Postcode API
        try:
            api_url = f"{self.open_postcode_base_url}/address"
            # API expects postcode WITHOUT space (e.g., "3114GG")
            params = {
                'postcode': normalized_postcode,
                'huisnummer': normalized_huisnummer
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract address information
            result.straat = data.get('straat', '')
            result.woonplaats = data.get('woonplaats', '')
            result.gemeente = data.get('gemeente', '')
            result.provincie = data.get('provincie', '')
            result.latitude = float(data.get('latitude', 0))
            result.longitude = float(data.get('longitude', 0))
            result.is_valid = True
            
            # Check if address is in service area
            service_area_check = self._check_service_area(normalized_postcode, result.gemeente)
            result.is_in_service_area = service_area_check['is_in_service_area']
            result.service_area_municipality = service_area_check['municipality']
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Open Postcode API: {e}")
            # If API fails, check service area based on postcode only
            service_area_check = self._check_service_area(normalized_postcode, "")
            if service_area_check['is_in_service_area']:
                result.is_valid = True
                result.is_in_service_area = True
                result.service_area_municipality = service_area_check['municipality']
        except (ValueError, KeyError) as e:
            print(f"Error parsing API response: {e}")
        except Exception as e:
            print(f"Unexpected error in address validation: {e}")
        
        return result
    
    def _check_service_area(self, postcode: str, gemeente: str) -> Dict[str, any]:
        """
        Check if address is in the service area
        
        Args:
            postcode: Normalized postcode
            gemeente: Municipality name
            
        Returns:
            Dictionary with service area check results
        """
        # Extract first 4 digits of postcode
        postcode_prefix = postcode[:4]
        
        # Check against service areas
        for municipality, allowed_postcodes in self.service_areas.items():
            if postcode_prefix in allowed_postcodes:
                return {
                    'is_in_service_area': True,
                    'municipality': municipality
                }
        
        # Also check by municipality name (fallback)
        if gemeente in self.service_areas:
            return {
                'is_in_service_area': True,
                'municipality': gemeente
            }
        
        return {
            'is_in_service_area': False,
            'municipality': None
        }
    
    def validate_address_from_text(self, address_text: str) -> AddressInfo:
        """
        Extract and validate address from text input
        
        Args:
            address_text: Text containing address information
            
        Returns:
            AddressInfo object with validation results
        """
        # Try to extract postcode and house number from text
        postcode_pattern = r'\b(\d{4}\s*[A-Z]{2})\b'
        huisnummer_pattern = r'\b(\d+[A-Za-z]?)\b'
        
        postcode_match = re.search(postcode_pattern, address_text, re.IGNORECASE)
        huisnummer_match = re.search(huisnummer_pattern, address_text)
        
        if postcode_match and huisnummer_match:
            postcode = postcode_match.group(1)
            huisnummer = huisnummer_match.group(1)
            return self.validate_address(postcode, huisnummer)
        
        # Return invalid result if we can't extract address
        return AddressInfo(
            postcode="",
            huisnummer="",
            straat="",
            woonplaats="",
            gemeente="",
            provincie="",
            latitude=0.0,
            longitude=0.0,
            is_valid=False,
            is_in_service_area=False
        )
    
    def get_service_area_info(self) -> Dict[str, List[str]]:
        """Get information about service areas"""
        return self.service_areas.copy()
    
    def is_address_blocked(self, postcode: str, huisnummer: str) -> bool:
        """
        Check if address is a bedrijfsklant
        
        Args:
            postcode: Dutch postcode
            huisnummer: House number
            
        Returns:
            True if address is a bedrijfsklant, False otherwise
        """
        return self._is_bedrijfsklant(postcode, huisnummer)
