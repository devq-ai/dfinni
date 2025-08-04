"""
Field-level encryption service for protecting PII/PHI data.
"""
import os
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import logfire
from app.config.settings import get_settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive patient data."""
    
    def __init__(self):
        self.settings = get_settings()
        self._cipher = self._initialize_cipher()
        
    def _initialize_cipher(self) -> Fernet:
        """Initialize the encryption cipher with a derived key."""
        # Get encryption key from environment
        master_key = os.getenv('PFINNI_ENCRYPTION_KEY')
        if not master_key:
            # Generate a new key if not set (for development only)
            logfire.warning("No PFINNI_ENCRYPTION_KEY found, generating new key")
            master_key = Fernet.generate_key().decode()
            logfire.error("CRITICAL: Set PFINNI_ENCRYPTION_KEY in production!")
            
        # Derive a key from the master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'pfinni-patient-dashboard',  # Static salt for deterministic derivation
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        
        return Fernet(key)
    
    def encrypt_field(self, value: Union[str, dict, list]) -> str:
        """Encrypt a single field value."""
        if value is None:
            return None
            
        try:
            # Convert to JSON string if not already a string
            if not isinstance(value, str):
                value = json.dumps(value)
                
            # Encrypt the value
            encrypted = self._cipher.encrypt(value.encode())
            
            # Log encryption (without the actual value)
            with logfire.span("field_encrypted"):
                logfire.info(
                    "Field encrypted",
                    field_type=type(value).__name__,
                    encrypted_length=len(encrypted)
                )
                
            return base64.urlsafe_b64encode(encrypted).decode()
            
        except Exception as e:
            logfire.error("Encryption failed", error=str(e))
            raise
    
    def decrypt_field(self, encrypted_value: str) -> Union[str, dict, list]:
        """Decrypt a single field value."""
        if encrypted_value is None:
            return None
            
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            
            # Decrypt the value
            decrypted = self._cipher.decrypt(encrypted_bytes).decode()
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return decrypted
                
        except Exception as e:
            logfire.error("Decryption failed", error=str(e))
            raise
    
    def encrypt_patient_pii(self, patient_data: dict) -> dict:
        """Encrypt PII fields in patient data."""
        # Define fields that contain PII/PHI
        pii_fields = {
            'ssn', 'social_security_number',
            'date_of_birth', 'dob',
            'medical_record_number', 'mrn',
            'phone_number', 'phone',
            'address', 'home_address',
            'emergency_contact',
            'insurance_policy_number',
            'driver_license'
        }
        
        encrypted_data = patient_data.copy()
        
        # Encrypt PII fields
        for field, value in patient_data.items():
            if field.lower() in pii_fields and value is not None:
                encrypted_data[field] = self.encrypt_field(value)
                encrypted_data[f"{field}_encrypted"] = True
                
        with logfire.span("patient_pii_encrypted"):
            logfire.info(
                "Patient PII encrypted",
                fields_encrypted=len([f for f in patient_data if f.lower() in pii_fields])
            )
                
        return encrypted_data
    
    def decrypt_patient_pii(self, encrypted_data: dict) -> dict:
        """Decrypt PII fields in patient data."""
        decrypted_data = encrypted_data.copy()
        
        # Decrypt fields marked as encrypted
        for field, value in encrypted_data.items():
            if field.endswith('_encrypted') and value is True:
                actual_field = field.replace('_encrypted', '')
                if actual_field in encrypted_data:
                    decrypted_data[actual_field] = self.decrypt_field(
                        encrypted_data[actual_field]
                    )
                    # Remove the encryption marker
                    del decrypted_data[field]
                    
        return decrypted_data


# Global encryption service instance
encryption_service = EncryptionService()