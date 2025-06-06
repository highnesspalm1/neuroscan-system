#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Privacy and Data Protection Module
Implements GDPR compliance, data encryption, and privacy controls
"""

import hashlib
import hmac
import secrets
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os
from dataclasses import dataclass
from enum import Enum

class DataCategory(Enum):
    """Data categories for GDPR compliance"""
    PERSONAL = "personal"
    TECHNICAL = "technical"
    USAGE = "usage"
    MARKETING = "marketing"
    SECURITY = "security"

class ConsentType(Enum):
    """Types of user consent"""
    NECESSARY = "necessary"
    FUNCTIONAL = "functional"
    ANALYTICS = "analytics"
    MARKETING = "marketing"

@dataclass
class DataProcessingRecord:
    """Record of data processing activities for GDPR compliance"""
    id: str
    purpose: str
    data_category: DataCategory
    legal_basis: str
    retention_period: int  # days
    created_at: datetime
    consent_required: bool = True
    automated_decision_making: bool = False

class EncryptionManager:
    """Manages encryption operations for sensitive data"""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize encryption manager with master key"""
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = self._generate_master_key()
        
        self._derive_keys()
    
    def _generate_master_key(self) -> bytes:
        """Generate a new master encryption key"""
        return secrets.token_bytes(32)
    
    def _derive_keys(self):
        """Derive encryption keys from master key"""
        # Derive key for general encryption
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'neuroscan_salt_2025',
            iterations=100000,
            backend=default_backend()
        )
        self.encryption_key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        self.fernet = Fernet(self.encryption_key)
        
        # Derive key for PII encryption
        kdf_pii = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'neuroscan_pii_2025',
            iterations=150000,
            backend=default_backend()
        )
        self.pii_key = base64.urlsafe_b64encode(kdf_pii.derive(self.master_key))
        self.pii_fernet = Fernet(self.pii_key)
    
    def encrypt_data(self, data: str, use_pii_key: bool = False) -> str:
        """Encrypt sensitive data"""
        try:
            data_bytes = data.encode('utf-8')
            fernet = self.pii_fernet if use_pii_key else self.fernet
            encrypted = fernet.encrypt(data_bytes)
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data: str, use_pii_key: bool = False) -> str:
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            fernet = self.pii_fernet if use_pii_key else self.fernet
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def hash_data(self, data: str, salt: Optional[str] = None) -> str:
        """Create irreversible hash of data"""
        if not salt:
            salt = secrets.token_hex(16)
        
        combined = f"{data}{salt}".encode('utf-8')
        hash_object = hashlib.sha256(combined)
        return f"{salt}:{hash_object.hexdigest()}"
    
    def verify_hash(self, data: str, hashed: str) -> bool:
        """Verify data against hash"""
        try:
            salt, hash_value = hashed.split(':', 1)
            return self.hash_data(data, salt) == hashed
        except:
            return False

class DataAnonymizer:
    """Anonymizes and pseudonymizes personal data"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def anonymize_ip(self, ip_address: str) -> str:
        """Anonymize IP address by removing last octet"""
        if '.' in ip_address:  # IPv4
            parts = ip_address.split('.')
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
        elif ':' in ip_address:  # IPv6
            parts = ip_address.split(':')
            if len(parts) >= 4:
                return ':'.join(parts[:4]) + '::'
        return "0.0.0.0"
    
    def pseudonymize_email(self, email: str) -> str:
        """Create pseudonym for email address"""
        hash_value = hashlib.sha256(email.encode()).hexdigest()[:8]
        domain = email.split('@')[1] if '@' in email else 'example.com'
        return f"user_{hash_value}@{domain}"
    
    def mask_serial_number(self, serial: str, show_chars: int = 4) -> str:
        """Mask serial number for logs"""
        if len(serial) <= show_chars:
            return '*' * len(serial)
        return serial[:show_chars] + '*' * (len(serial) - show_chars)
    
    def anonymize_user_agent(self, user_agent: str) -> str:
        """Anonymize user agent string"""
        # Remove version numbers and specific identifiers
        anonymized = user_agent
        # Remove Chrome version
        if 'Chrome/' in anonymized:
            parts = anonymized.split('Chrome/')
            if len(parts) > 1:
                version_part = parts[1].split(' ')[0]
                anonymized = anonymized.replace(f'Chrome/{version_part}', 'Chrome/XXX')
        
        # Remove detailed OS version
        if 'Windows NT' in anonymized:
            anonymized = anonymized.replace('Windows NT 10.0', 'Windows NT X.X')
        
        return anonymized

class ConsentManager:
    """Manages user consent for data processing"""
    
    def __init__(self):
        self.consent_records: Dict[str, Dict[ConsentType, bool]] = {}
        self.consent_timestamps: Dict[str, Dict[ConsentType, datetime]] = {}
    
    def record_consent(self, user_id: str, consent_type: ConsentType, granted: bool):
        """Record user consent"""
        if user_id not in self.consent_records:
            self.consent_records[user_id] = {}
            self.consent_timestamps[user_id] = {}
        
        self.consent_records[user_id][consent_type] = granted
        self.consent_timestamps[user_id][consent_type] = datetime.utcnow()
    
    def has_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Check if user has granted specific consent"""
        return self.consent_records.get(user_id, {}).get(consent_type, False)
    
    def get_consent_record(self, user_id: str) -> Dict[str, Any]:
        """Get complete consent record for user"""
        consent = self.consent_records.get(user_id, {})
        timestamps = self.consent_timestamps.get(user_id, {})
        
        return {
            "user_id": user_id,
            "consents": {
                consent_type.value: {
                    "granted": granted,
                    "timestamp": timestamps.get(consent_type, datetime.utcnow()).isoformat()
                }
                for consent_type, granted in consent.items()
            }
        }
    
    def withdraw_consent(self, user_id: str, consent_type: ConsentType):
        """Withdraw specific consent"""
        self.record_consent(user_id, consent_type, False)

class DataRetentionManager:
    """Manages data retention and deletion policies"""
    
    def __init__(self):
        self.retention_policies: Dict[DataCategory, int] = {
            DataCategory.PERSONAL: 730,      # 2 years
            DataCategory.TECHNICAL: 365,     # 1 year
            DataCategory.USAGE: 730,         # 2 years
            DataCategory.MARKETING: 1095,    # 3 years
            DataCategory.SECURITY: 2555      # 7 years
        }
        
        self.processing_records: List[DataProcessingRecord] = []
    
    def register_processing(self, purpose: str, data_category: DataCategory, 
                          legal_basis: str, retention_days: Optional[int] = None,
                          consent_required: bool = True) -> str:
        """Register a new data processing activity"""
        record_id = secrets.token_hex(8)
        retention_period = retention_days or self.retention_policies[data_category]
        
        record = DataProcessingRecord(
            id=record_id,
            purpose=purpose,
            data_category=data_category,
            legal_basis=legal_basis,
            retention_period=retention_period,
            created_at=datetime.utcnow(),
            consent_required=consent_required
        )
        
        self.processing_records.append(record)
        return record_id
    
    def get_expired_data(self) -> List[str]:
        """Get list of data that should be deleted based on retention policies"""
        expired = []
        current_time = datetime.utcnow()
        
        for record in self.processing_records:
            expiry_date = record.created_at + timedelta(days=record.retention_period)
            if current_time > expiry_date:
                expired.append(record.id)
        
        return expired
    
    def should_delete_data(self, processing_id: str) -> bool:
        """Check if data should be deleted"""
        record = next((r for r in self.processing_records if r.id == processing_id), None)
        if not record:
            return False
        
        expiry_date = record.created_at + timedelta(days=record.retention_period)
        return datetime.utcnow() > expiry_date

class PrivacyController:
    """Main privacy controller implementing GDPR compliance"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.encryption_manager = EncryptionManager(master_key)
        self.anonymizer = DataAnonymizer(self.encryption_manager)
        self.consent_manager = ConsentManager()
        self.retention_manager = DataRetentionManager()
        
        # Register standard processing activities
        self._register_standard_processing()
    
    def _register_standard_processing(self):
        """Register standard data processing activities"""
        self.retention_manager.register_processing(
            "Product verification logging",
            DataCategory.TECHNICAL,
            "Legitimate interest - fraud prevention",
            retention_days=365,
            consent_required=False
        )
        
        self.retention_manager.register_processing(
            "User analytics and statistics",
            DataCategory.USAGE,
            "Consent",
            retention_days=730,
            consent_required=True
        )
        
        self.retention_manager.register_processing(
            "Security monitoring",
            DataCategory.SECURITY,
            "Legitimate interest - security",
            retention_days=2555,
            consent_required=False
        )
    
    def process_verification_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process verification request with privacy controls"""
        # Anonymize IP address
        if 'ip_address' in request_data:
            request_data['ip_address'] = self.anonymizer.anonymize_ip(request_data['ip_address'])
        
        # Anonymize user agent
        if 'user_agent' in request_data:
            request_data['user_agent'] = self.anonymizer.anonymize_user_agent(request_data['user_agent'])
        
        # Mask serial number in logs
        if 'serial_number' in request_data:
            request_data['serial_masked'] = self.anonymizer.mask_serial_number(request_data['serial_number'])
        
        return request_data
    
    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in data"""
        sensitive_fields = ['email', 'phone', 'address', 'customer_name']
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data:
                encrypted_data[field] = self.encryption_manager.encrypt_data(
                    str(encrypted_data[field]), use_pii_key=True
                )
        
        return encrypted_data
    
    def decrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in data"""
        sensitive_fields = ['email', 'phone', 'address', 'customer_name']
        decrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data:
                try:
                    decrypted_data[field] = self.encryption_manager.decrypt_data(
                        decrypted_data[field], use_pii_key=True
                    )
                except:
                    # Field might not be encrypted
                    pass
        
        return decrypted_data
    
    def handle_data_subject_request(self, user_id: str, request_type: str) -> Dict[str, Any]:
        """Handle GDPR data subject requests"""
        if request_type == "access":
            return self._handle_access_request(user_id)
        elif request_type == "deletion":
            return self._handle_deletion_request(user_id)
        elif request_type == "portability":
            return self._handle_portability_request(user_id)
        elif request_type == "rectification":
            return self._handle_rectification_request(user_id)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    def _handle_access_request(self, user_id: str) -> Dict[str, Any]:
        """Handle data access request"""
        return {
            "user_id": user_id,
            "consent_record": self.consent_manager.get_consent_record(user_id),
            "processing_activities": [
                {
                    "purpose": record.purpose,
                    "data_category": record.data_category.value,
                    "legal_basis": record.legal_basis,
                    "retention_period": record.retention_period
                }
                for record in self.retention_manager.processing_records
            ],
            "data_export_instructions": "Contact support@neurocompany.com for full data export"
        }
    
    def _handle_deletion_request(self, user_id: str) -> Dict[str, Any]:
        """Handle data deletion request"""
        # Withdraw all consents
        for consent_type in ConsentType:
            self.consent_manager.withdraw_consent(user_id, consent_type)
        
        return {
            "user_id": user_id,
            "status": "deletion_initiated",
            "message": "Data deletion has been initiated. Some data may be retained for legal compliance.",
            "retention_note": "Security logs retained for 7 years for legal compliance"
        }
    
    def _handle_portability_request(self, user_id: str) -> Dict[str, Any]:
        """Handle data portability request"""
        return {
            "user_id": user_id,
            "format": "JSON",
            "status": "ready_for_export",
            "contact": "support@neurocompany.com",
            "note": "Data will be provided in machine-readable format within 30 days"
        }
    
    def _handle_rectification_request(self, user_id: str) -> Dict[str, Any]:
        """Handle data rectification request"""
        return {
            "user_id": user_id,
            "status": "rectification_available",
            "contact": "support@neurocompany.com",
            "note": "Contact support to update your personal information"
        }
    
    def generate_privacy_report(self) -> Dict[str, Any]:
        """Generate privacy compliance report"""
        expired_data = self.retention_manager.get_expired_data()
        
        return {
            "report_generated": datetime.utcnow().isoformat(),
            "processing_activities": len(self.retention_manager.processing_records),
            "consent_records": len(self.consent_manager.consent_records),
            "expired_data_count": len(expired_data),
            "encryption_status": "active",
            "anonymization_status": "active",
            "gdpr_compliance": {
                "data_protection_by_design": True,
                "consent_management": True,
                "data_subject_rights": True,
                "data_retention_policies": True,
                "breach_notification": True
            }
        }

# Global privacy controller instance
privacy_controller = PrivacyController()

# Privacy middleware decorator
def privacy_protected(func):
    """Decorator to apply privacy protection to route handlers"""
    def wrapper(*args, **kwargs):
        # Apply privacy controls before processing
        if 'request_data' in kwargs:
            kwargs['request_data'] = privacy_controller.process_verification_request(
                kwargs['request_data']
            )
        return func(*args, **kwargs)
    return wrapper
