#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Security Configuration and Management
Centralized security settings and policy management
"""

import os
import json
import yaml
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import hmac
from cryptography.fernet import Fernet
import re

class SecurityLevel(Enum):
    """Security levels for different environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class PasswordPolicy(Enum):
    """Password policy levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    # Authentication settings
    jwt_expiry_minutes: int = 60
    refresh_token_expiry_days: int = 30
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    require_2fa: bool = False
    
    # Password requirements
    password_policy: PasswordPolicy = PasswordPolicy.STANDARD
    min_password_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    password_history_count: int = 5
    password_max_age_days: int = 90
    
    # Session management
    session_timeout_minutes: int = 30
    max_concurrent_sessions: int = 3
    secure_cookies: bool = True
    httponly_cookies: bool = True
    
    # Rate limiting
    global_rate_limit: int = 1000  # requests per hour
    api_rate_limit: int = 100      # API requests per hour
    auth_rate_limit: int = 10      # auth attempts per hour
    burst_allowance: int = 10      # burst requests allowed
    
    # IP Security
    enable_ip_whitelist: bool = False
    enable_ip_blacklist: bool = True
    auto_block_suspicious_ips: bool = True
    geo_blocking_enabled: bool = False
    allowed_countries: List[str] = None
    
    # Content Security
    enable_csrf_protection: bool = True
    enable_xss_protection: bool = True
    enable_content_type_validation: bool = True
    max_request_size_mb: int = 10
    allowed_file_types: List[str] = None
    
    # Audit and Monitoring
    log_all_requests: bool = True
    log_sensitive_data: bool = False
    audit_retention_days: int = 2555  # 7 years
    enable_real_time_alerts: bool = True
    
    # Encryption
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 30
    encrypt_database_connections: bool = True
    encrypt_backup_files: bool = True
    
    # API Security
    require_api_key: bool = True
    api_key_length: int = 32
    api_key_expiry_days: int = 365
    enable_api_versioning: bool = True
    
    # CORS Policy
    cors_allowed_origins: List[str] = None
    cors_allow_credentials: bool = True
    cors_allowed_methods: List[str] = None
    cors_allowed_headers: List[str] = None
    
    def __post_init__(self):
        """Initialize default values"""
        if self.allowed_file_types is None:
            self.allowed_file_types = ['pdf', 'png', 'jpg', 'jpeg', 'svg']
        
        if self.cors_allowed_origins is None:
            self.cors_allowed_origins = ['http://localhost:3000']
        
        if self.cors_allowed_methods is None:
            self.cors_allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        
        if self.cors_allowed_headers is None:
            self.cors_allowed_headers = ['*']
        
        if self.allowed_countries is None:
            self.allowed_countries = []

class SecurityConfigManager:
    """Manages security configuration and policies"""
    
    def __init__(self, config_file: str = "security_config.yaml"):
        self.config_file = Path(config_file)
        self.security_policy = SecurityPolicy()
        self.security_level = SecurityLevel.DEVELOPMENT
        self.secrets_manager = SecretsManager()
        
        # Load configuration
        self.load_configuration()
        
        # Environment-specific adjustments
        self._adjust_for_environment()
    
    def load_configuration(self):
        """Load security configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Update security policy
                if 'security_policy' in config_data:
                    policy_dict = config_data['security_policy']
                    for key, value in policy_dict.items():
                        if hasattr(self.security_policy, key):
                            setattr(self.security_policy, key, value)
                
                # Set security level
                if 'security_level' in config_data:
                    self.security_level = SecurityLevel(config_data['security_level'])
                
            except Exception as e:
                print(f"Warning: Failed to load security config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def save_configuration(self):
        """Save current configuration to file"""
        config_data = {
            'security_level': self.security_level.value,
            'security_policy': asdict(self.security_policy),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
    
    def _create_default_config(self):
        """Create default security configuration"""
        self.save_configuration()
    
    def _adjust_for_environment(self):
        """Adjust security settings based on environment"""
        env = os.getenv('ENVIRONMENT', 'development').lower()
        
        if env == 'production':
            self.security_level = SecurityLevel.PRODUCTION
            self.security_policy.require_2fa = True
            self.security_policy.password_policy = PasswordPolicy.ENTERPRISE
            self.security_policy.session_timeout_minutes = 15
            self.security_policy.auto_block_suspicious_ips = True
            self.security_policy.log_sensitive_data = False
            self.security_policy.secure_cookies = True
            
        elif env == 'staging':
            self.security_level = SecurityLevel.STAGING
            self.security_policy.password_policy = PasswordPolicy.STRICT
            self.security_policy.session_timeout_minutes = 30
            
        elif env == 'testing':
            self.security_level = SecurityLevel.TESTING
            self.security_policy.max_login_attempts = 10
            self.security_policy.lockout_duration_minutes = 5
            
        else:  # development
            self.security_level = SecurityLevel.DEVELOPMENT
            self.security_policy.max_login_attempts = 20
            self.security_policy.lockout_duration_minutes = 1
            self.security_policy.require_2fa = False
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password against current policy"""
        policy = self.security_policy
        errors = []
        
        # Length check
        if len(password) < policy.min_password_length:
            errors.append(f"Password must be at least {policy.min_password_length} characters")
        
        # Character requirements
        if policy.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if policy.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if policy.require_numbers and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if policy.require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Policy-specific checks
        if policy.password_policy == PasswordPolicy.ENTERPRISE:
            # Additional enterprise requirements
            if len(password) < 16:
                errors.append("Enterprise policy requires at least 16 characters")
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>].*[!@#$%^&*(),.?":{}|<>]', password):
                errors.append("Enterprise policy requires at least two special characters")
        
        # Common password check
        if self._is_common_password(password):
            errors.append("Password is too common, please choose a different one")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength_score': self._calculate_password_strength(password)
        }
    
    def _is_common_password(self, password: str) -> bool:
        """Check if password is in common passwords list"""
        common_passwords = {
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', '1234567890', 'password1'
        }
        return password.lower() in common_passwords
    
    def _calculate_password_strength(self, password: str) -> int:
        """Calculate password strength score (0-100)"""
        score = 0
        
        # Length bonus
        score += min(len(password) * 2, 25)
        
        # Character variety
        if re.search(r'[a-z]', password):
            score += 5
        if re.search(r'[A-Z]', password):
            score += 5
        if re.search(r'\d', password):
            score += 5
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10
        
        # Pattern checks
        if not re.search(r'(.)\1{2,}', password):  # No 3+ repeated chars
            score += 10
        
        if not re.search(r'(012|123|234|345|456|567|678|789|890)', password):  # No sequences
            score += 10
        
        # Bonus for mixed case and special chars
        if re.search(r'[a-z]', password) and re.search(r'[A-Z]', password):
            score += 5
        
        if len(set(password)) > len(password) * 0.6:  # Character diversity
            score += 15
        
        return min(score, 100)
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get HTTP security headers based on current policy"""
        headers = {}
        
        if self.security_policy.enable_xss_protection:
            headers['X-XSS-Protection'] = '1; mode=block'
            headers['X-Content-Type-Options'] = 'nosniff'
            headers['X-Frame-Options'] = 'DENY'
        
        if self.security_level in [SecurityLevel.PRODUCTION, SecurityLevel.STAGING]:
            headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self'"
            )
        
        headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        headers['Permissions-Policy'] = 'camera=(), microphone=(), location=()'
        
        return headers
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed based on policy"""
        # Check whitelist first
        if self.security_policy.enable_ip_whitelist:
            # Implementation would check against whitelist
            pass
        
        # Check blacklist
        if self.security_policy.enable_ip_blacklist:
            # Implementation would check against blacklist
            pass
        
        return True  # Default allow
    
    def get_rate_limit_config(self, endpoint_type: str = 'global') -> Dict[str, int]:
        """Get rate limit configuration for endpoint type"""
        if endpoint_type == 'api':
            return {
                'requests': self.security_policy.api_rate_limit,
                'window': 3600,  # 1 hour
                'burst': self.security_policy.burst_allowance
            }
        elif endpoint_type == 'auth':
            return {
                'requests': self.security_policy.auth_rate_limit,
                'window': 3600,  # 1 hour
                'burst': 2
            }
        else:
            return {
                'requests': self.security_policy.global_rate_limit,
                'window': 3600,  # 1 hour
                'burst': self.security_policy.burst_allowance
            }

class SecretsManager:
    """Manages encryption keys and secrets"""
    
    def __init__(self, secrets_file: str = ".secrets"):
        self.secrets_file = Path(secrets_file)
        self.secrets: Dict[str, str] = {}
        self.encryption_key = None
        
        self._load_or_create_secrets()
    
    def _load_or_create_secrets(self):
        """Load secrets from file or create new ones"""
        if self.secrets_file.exists():
            try:
                with open(self.secrets_file, 'r') as f:
                    self.secrets = json.load(f)
            except:
                self._create_default_secrets()
        else:
            self._create_default_secrets()
        
        # Set up encryption key
        if 'master_key' in self.secrets:
            self.encryption_key = Fernet(self.secrets['master_key'].encode())
        else:
            master_key = Fernet.generate_key()
            self.secrets['master_key'] = master_key.decode()
            self.encryption_key = Fernet(master_key)
            self._save_secrets()
    
    def _create_default_secrets(self):
        """Create default secrets"""
        self.secrets = {
            'jwt_secret': secrets.token_urlsafe(32),
            'session_secret': secrets.token_urlsafe(32),
            'webhook_secret': secrets.token_urlsafe(32),
            'api_key_salt': secrets.token_urlsafe(16),
            'master_key': Fernet.generate_key().decode(),
            'created_at': datetime.utcnow().isoformat()
        }
        self._save_secrets()
    
    def _save_secrets(self):
        """Save secrets to file"""
        with open(self.secrets_file, 'w') as f:
            json.dump(self.secrets, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(self.secrets_file, 0o600)
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get a secret by key"""
        return self.secrets.get(key)
    
    def set_secret(self, key: str, value: str):
        """Set a secret value"""
        self.secrets[key] = value
        self._save_secrets()
    
    def rotate_secret(self, key: str) -> str:
        """Rotate a secret (generate new value)"""
        new_value = secrets.token_urlsafe(32)
        self.set_secret(key, new_value)
        return new_value
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if self.encryption_key:
            encrypted = self.encryption_key.encrypt(data.encode())
            return encrypted.decode()
        return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if self.encryption_key:
            try:
                decrypted = self.encryption_key.decrypt(encrypted_data.encode())
                return decrypted.decode()
            except:
                return encrypted_data
        return encrypted_data
    
    def generate_api_key(self) -> str:
        """Generate a new API key"""
        return secrets.token_urlsafe(32)
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage"""
        salt = self.get_secret('api_key_salt')
        if salt:
            return hashlib.pbkdf2_hex(api_key.encode(), salt.encode(), 100000)
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def verify_api_key(self, api_key: str, hashed: str) -> bool:
        """Verify an API key against its hash"""
        return self.hash_api_key(api_key) == hashed

class ComplianceManager:
    """Manages compliance requirements and reporting"""
    
    def __init__(self, security_config: SecurityConfigManager):
        self.security_config = security_config
        self.compliance_frameworks = {
            'GDPR': self._check_gdpr_compliance,
            'SOC2': self._check_soc2_compliance,
            'ISO27001': self._check_iso27001_compliance,
            'HIPAA': self._check_hipaa_compliance
        }
    
    def get_compliance_status(self) -> Dict[str, Dict[str, Any]]:
        """Get compliance status for all frameworks"""
        status = {}
        
        for framework, check_func in self.compliance_frameworks.items():
            status[framework] = check_func()
        
        return status
    
    def _check_gdpr_compliance(self) -> Dict[str, Any]:
        """Check GDPR compliance"""
        policy = self.security_config.security_policy
        
        checks = {
            'data_encryption': True,  # We implement encryption
            'audit_logging': policy.log_all_requests,
            'data_retention_policy': policy.audit_retention_days > 0,
            'user_consent_management': True,  # Implemented in privacy module
            'data_subject_rights': True,  # Implemented in privacy module
            'privacy_by_design': True,
            'data_breach_notification': policy.enable_real_time_alerts
        }
        
        compliance_score = sum(checks.values()) / len(checks) * 100
        
        return {
            'compliant': compliance_score >= 90,
            'score': compliance_score,
            'checks': checks,
            'recommendations': self._get_gdpr_recommendations(checks)
        }
    
    def _check_soc2_compliance(self) -> Dict[str, Any]:
        """Check SOC 2 compliance"""
        policy = self.security_config.security_policy
        
        checks = {
            'access_controls': policy.require_2fa or policy.max_login_attempts <= 5,
            'encryption_in_transit': True,
            'encryption_at_rest': policy.encrypt_database_connections,
            'monitoring_and_logging': policy.log_all_requests,
            'incident_response': policy.enable_real_time_alerts,
            'security_awareness': True,  # Assumed
            'vendor_management': True,   # Assumed
            'backup_and_recovery': policy.encrypt_backup_files
        }
        
        compliance_score = sum(checks.values()) / len(checks) * 100
        
        return {
            'compliant': compliance_score >= 85,
            'score': compliance_score,
            'checks': checks,
            'recommendations': self._get_soc2_recommendations(checks)
        }
    
    def _check_iso27001_compliance(self) -> Dict[str, Any]:
        """Check ISO 27001 compliance"""
        policy = self.security_config.security_policy
        
        checks = {
            'information_security_policy': True,
            'risk_management': True,
            'asset_management': True,
            'access_control': policy.require_2fa,
            'cryptography': policy.encrypt_database_connections,
            'physical_security': True,  # Assumed for cloud deployment
            'operations_security': policy.log_all_requests,
            'communications_security': True,
            'system_acquisition': True,
            'supplier_relationships': True,
            'incident_management': policy.enable_real_time_alerts,
            'business_continuity': policy.encrypt_backup_files
        }
        
        compliance_score = sum(checks.values()) / len(checks) * 100
        
        return {
            'compliant': compliance_score >= 80,
            'score': compliance_score,
            'checks': checks,
            'recommendations': self._get_iso27001_recommendations(checks)
        }
    
    def _check_hipaa_compliance(self) -> Dict[str, Any]:
        """Check HIPAA compliance (if applicable)"""
        policy = self.security_config.security_policy
        
        checks = {
            'access_control': policy.require_2fa,
            'audit_controls': policy.log_all_requests,
            'integrity': True,
            'person_authentication': policy.max_login_attempts <= 3,
            'transmission_security': True,
            'encryption': policy.encrypt_database_connections,
            'automatic_logoff': policy.session_timeout_minutes <= 30,
            'unique_user_identification': True
        }
        
        compliance_score = sum(checks.values()) / len(checks) * 100
        
        return {
            'compliant': compliance_score >= 95,
            'score': compliance_score,
            'checks': checks,
            'recommendations': self._get_hipaa_recommendations(checks)
        }
    
    def _get_gdpr_recommendations(self, checks: Dict[str, bool]) -> List[str]:
        """Get GDPR compliance recommendations"""
        recommendations = []
        
        if not checks.get('audit_logging'):
            recommendations.append("Enable comprehensive audit logging")
        
        if not checks.get('data_retention_policy'):
            recommendations.append("Implement data retention policies")
        
        return recommendations
    
    def _get_soc2_recommendations(self, checks: Dict[str, bool]) -> List[str]:
        """Get SOC 2 compliance recommendations"""
        recommendations = []
        
        if not checks.get('access_controls'):
            recommendations.append("Implement multi-factor authentication")
        
        if not checks.get('encryption_at_rest'):
            recommendations.append("Enable database encryption")
        
        return recommendations
    
    def _get_iso27001_recommendations(self, checks: Dict[str, bool]) -> List[str]:
        """Get ISO 27001 compliance recommendations"""
        recommendations = []
        
        if not checks.get('access_control'):
            recommendations.append("Implement strong access controls with 2FA")
        
        return recommendations
    
    def _get_hipaa_recommendations(self, checks: Dict[str, bool]) -> List[str]:
        """Get HIPAA compliance recommendations"""
        recommendations = []
        
        if not checks.get('access_control'):
            recommendations.append("Implement multi-factor authentication")
        
        if not checks.get('person_authentication'):
            recommendations.append("Reduce maximum login attempts to 3")
        
        return recommendations

# Global security configuration manager
security_config = SecurityConfigManager()
compliance_manager = ComplianceManager(security_config)
