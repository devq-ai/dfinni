#!/usr/bin/env python3
"""Test field-level encryption service."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.encryption_service import encryption_service

def test_encryption():
    """Test encryption and decryption of PII fields."""
    
    print("Testing Field-Level Encryption...")
    print("-" * 80)
    
    # Test data with PII
    test_patient = {
        "first_name": "John",
        "last_name": "Doe",
        "ssn": "123-45-6789",
        "date_of_birth": "1990-01-01",
        "phone_number": "+1-555-0123",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "TX",
            "zip_code": "12345"
        },
        "medical_record_number": "MRN-12345",
        "insurance_policy_number": "INS-98765"
    }
    
    print("Original Data:")
    print(f"  SSN: {test_patient['ssn']}")
    print(f"  DOB: {test_patient['date_of_birth']}")
    print(f"  Phone: {test_patient['phone_number']}")
    print(f"  Address: {test_patient['address']}")
    print(f"  MRN: {test_patient['medical_record_number']}")
    
    # Encrypt
    encrypted = encryption_service.encrypt_patient_pii(test_patient)
    
    print("\nEncrypted Data:")
    print(f"  SSN: {encrypted.get('ssn', 'N/A')[:50]}...")
    print(f"  SSN Encrypted Flag: {encrypted.get('ssn_encrypted', False)}")
    print(f"  DOB: {encrypted.get('date_of_birth', 'N/A')[:50]}...")
    print(f"  DOB Encrypted Flag: {encrypted.get('date_of_birth_encrypted', False)}")
    print(f"  Phone: {encrypted.get('phone_number', 'N/A')[:50]}...")
    print(f"  Address: {encrypted.get('address', 'N/A')[:50] if isinstance(encrypted.get('address'), str) else 'Complex object'}...")
    
    # Decrypt
    decrypted = encryption_service.decrypt_patient_pii(encrypted)
    
    print("\nDecrypted Data:")
    print(f"  SSN: {decrypted['ssn']}")
    print(f"  DOB: {decrypted['date_of_birth']}")
    print(f"  Phone: {decrypted['phone_number']}")
    print(f"  Address: {decrypted['address']}")
    print(f"  MRN: {decrypted['medical_record_number']}")
    
    # Verify
    print("\nVerification:")
    print(f"  SSN Match: {'✅' if decrypted['ssn'] == test_patient['ssn'] else '❌'}")
    print(f"  DOB Match: {'✅' if decrypted['date_of_birth'] == test_patient['date_of_birth'] else '❌'}")
    print(f"  Phone Match: {'✅' if decrypted['phone_number'] == test_patient['phone_number'] else '❌'}")
    print(f"  Address Match: {'✅' if decrypted['address'] == test_patient['address'] else '❌'}")
    print(f"  MRN Match: {'✅' if decrypted['medical_record_number'] == test_patient['medical_record_number'] else '❌'}")

if __name__ == "__main__":
    test_encryption()