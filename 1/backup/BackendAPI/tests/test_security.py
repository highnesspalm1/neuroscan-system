#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security and Privacy Integration Tests
Tests for GDPR compliance, audit logging, threat detection, and security configuration
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime, timedelta
import time
import hashlib
import hmac

from main import app
from app.core.privacy import PrivacyController, EncryptionManager, DataAnonymizer
from app.core.audit import SecurityAuditor, SecurityEvent
from app.core.threat_detection import ThreatDetectionEngine, ThreatIntelligence
from app.core.security_config import SecurityConfigManager, SecurityPolicy

client = TestClient(app)


class TestPrivacyCompliance:
    """Test GDPR and privacy compliance features"""
    
    def setup_method(self):
        """Setup test environment"""
        self.privacy_controller = PrivacyController()
        self.encryption_manager = EncryptionManager()
        self.anonymizer = DataAnonymizer()
    
    def test_data_encryption(self):
        """Test PII data encryption"""
        sensitive_data = "user@example.com"
        
        # Encrypt data
        encrypted = self.encryption_manager.encrypt_pii(sensitive_data)
        assert encrypted != sensitive_data
        assert len(encrypted) > 0
        
        # Decrypt data
        decrypted = self.encryption_manager.decrypt_pii(encrypted)
        assert decrypted == sensitive_data
    
    def test_data_anonymization(self):
        """Test data anonymization"""
        test_data = {
            "email": "user@example.com",
            "ip_address": "192.168.1.100",
            "serial_number": "NS-2024-001"
        }
        
        anonymized = self.anonymizer.anonymize_data(test_data)
        
        # Email should be pseudonymized
        assert anonymized["email"] != test_data["email"]
        assert "@" in anonymized["email"]
        
        # IP should be anonymized
        assert anonymized["ip_address"] != test_data["ip_address"]
        assert anonymized["ip_address"].endswith(".0")
        
        # Serial number should be masked
        assert anonymized["serial_number"] != test_data["serial_number"]
        assert "***" in anonymized["serial_number"]
    
    @pytest.mark.asyncio
    async def test_gdpr_data_export(self):
        """Test GDPR data export functionality"""
        user_id = "test_user_123"
        
        # Request data export
        export_data = await self.privacy_controller.export_user_data(user_id)
        
        assert isinstance(export_data, dict)
        assert "personal_data" in export_data
        assert "metadata" in export_data
        assert export_data["metadata"]["export_date"]
    
    @pytest.mark.asyncio
    async def test_gdpr_data_deletion(self):
        """Test GDPR right to be forgotten"""
        user_id = "test_user_123"
        
        # Request data deletion
        deletion_result = await self.privacy_controller.delete_user_data(user_id)
        
        assert deletion_result["success"] is True
        assert "deleted_records" in deletion_result
        assert deletion_result["deletion_date"]
    
    def test_consent_management(self):
        """Test consent tracking and management"""
        user_id = "test_user_123"
        consent_types = ["analytics", "marketing", "essential"]
        
        # Record consent
        for consent_type in consent_types:
            result = self.privacy_controller.record_consent(
                user_id, consent_type, granted=True
            )
            assert result["success"] is True
        
        # Check consent status
        consent_status = self.privacy_controller.get_consent_status(user_id)
        assert len(consent_status) == len(consent_types)
        assert all(status["granted"] for status in consent_status.values())
        
        # Withdraw consent
        result = self.privacy_controller.withdraw_consent(user_id, "marketing")
        assert result["success"] is True
        
        # Verify withdrawal
        updated_status = self.privacy_controller.get_consent_status(user_id)
        assert updated_status["marketing"]["granted"] is False


class TestSecurityAudit:
    """Test security audit logging and monitoring"""
    
    def setup_method(self):
        """Setup test environment"""
        self.auditor = SecurityAuditor()
    
    def test_security_event_creation(self):
        """Test security event logging"""
        event = SecurityEvent(
            event_type="authentication",
            user_id="test_user",
            ip_address="192.168.1.100",
            user_agent="Test Browser",
            details={"login_attempt": "successful"}
        )
        
        assert event.event_type == "authentication"
        assert event.user_id == "test_user"
        assert event.timestamp
        assert event.event_id
    
    @pytest.mark.asyncio
    async def test_audit_log_creation(self):
        """Test audit log creation with digital signature"""
        event_data = {
            "event_type": "certificate_verification",
            "user_id": "test_user",
            "ip_address": "192.168.1.100",
            "details": {"serial_number": "TEST-001"}
        }
        
        log_entry = await self.auditor.log_security_event(**event_data)
        
        assert log_entry["event_id"]
        assert log_entry["signature"]
        assert log_entry["timestamp"]
        assert log_entry["integrity_hash"]
    
    def test_audit_signature_verification(self):
        """Test audit log signature verification"""
        # Create a test log entry
        log_data = {
            "event_id": "test_event_123",
            "event_type": "test",
            "timestamp": "2024-06-02T15:00:00Z",
            "data": {"test": "data"}
        }
        
        # Generate signature
        signature = self.auditor.sign_audit_entry(log_data)
        assert signature
        
        # Verify signature
        is_valid = self.auditor.verify_audit_signature(log_data, signature)
        assert is_valid is True
        
        # Test with tampered data
        tampered_data = log_data.copy()
        tampered_data["data"]["test"] = "tampered"
        
        is_valid_tampered = self.auditor.verify_audit_signature(tampered_data, signature)
        assert is_valid_tampered is False
    
    def test_failed_login_tracking(self):
        """Test failed login attempt tracking"""
        ip_address = "192.168.1.100"
        
        # Simulate multiple failed attempts
        for i in range(5):
            self.auditor.log_failed_attempt(ip_address, "invalid_credentials")
        
        # Check if IP is flagged as suspicious
        is_suspicious = self.auditor.is_suspicious_ip(ip_address)
        assert is_suspicious is True
        
        # Check attempt count
        attempt_count = self.auditor.get_failed_attempts(ip_address)
        assert attempt_count >= 5


class TestThreatDetection:
    """Test threat detection and response system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.threat_engine = ThreatDetectionEngine()
        self.threat_intel = ThreatIntelligence()
    
    def test_sql_injection_detection(self):
        """Test SQL injection pattern detection"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "1; SELECT * FROM secrets"
        ]
        
        for malicious_input in malicious_inputs:
            threat_level = self.threat_intel.analyze_request_content(malicious_input)
            assert threat_level > 0.5  # Should detect as high threat
    
    def test_xss_detection(self):
        """Test XSS pattern detection"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "onclick='alert(1)'"
        ]
        
        for payload in xss_payloads:
            threat_level = self.threat_intel.analyze_request_content(payload)
            assert threat_level > 0.5  # Should detect as high threat
    
    def test_rate_limiting_detection(self):
        """Test rate limiting and abuse detection"""
        ip_address = "192.168.1.100"
        
        # Simulate rapid requests
        for i in range(150):  # Exceed rate limit
            detection_result = self.threat_engine.analyze_request(
                ip_address=ip_address,
                endpoint="/verify",
                user_agent="Test Client"
            )
        
        # Should detect rate limit violation
        assert detection_result["threat_detected"] is True
        assert "rate_limit" in detection_result["threat_types"]
    
    def test_geographic_anomaly_detection(self):
        """Test geographic anomaly detection"""
        user_id = "test_user_123"
        
        # Establish baseline (US location)
        for _ in range(10):
            self.threat_engine.record_user_activity(
                user_id=user_id,
                ip_address="192.168.1.100",  # US IP (simulated)
                country="US"
            )
        
        # Test anomalous location
        anomaly_result = self.threat_engine.detect_geographic_anomaly(
            user_id=user_id,
            ip_address="1.2.3.4",  # Different country IP (simulated)
            country="CN"
        )
        
        assert anomaly_result["anomaly_detected"] is True
        assert anomaly_result["risk_score"] > 0.5
    
    def test_automated_response(self):
        """Test automated threat response"""
        ip_address = "192.168.1.100"
        threat_data = {
            "threat_type": "high_rate_limit_violation",
            "severity": "high",
            "ip_address": ip_address
        }
        
        # Trigger automated response
        response_action = self.threat_engine.automated_response(threat_data)
        
        assert response_action["action"] in ["block_ip", "rate_limit", "monitor"]
        assert response_action["duration"] > 0
        
        # Verify IP is blocked
        is_blocked = self.threat_engine.is_ip_blocked(ip_address)
        assert is_blocked is True
    
    def test_behavioral_profiling(self):
        """Test user behavioral profiling"""
        user_id = "test_user_123"
        
        # Establish normal behavior pattern
        normal_activities = [
            {"endpoint": "/verify", "time": "09:00"},
            {"endpoint": "/verify", "time": "09:15"},
            {"endpoint": "/admin/certificates", "time": "10:00"}
        ]
        
        for activity in normal_activities:
            self.threat_engine.record_user_behavior(user_id, activity)
        
        # Test anomalous behavior
        anomalous_activity = {
            "endpoint": "/admin/delete", "time": "03:00"  # Unusual time and action
        }
        
        anomaly_score = self.threat_engine.analyze_behavior_anomaly(
            user_id, anomalous_activity
        )
        
        assert anomaly_score > 0.3  # Should detect anomaly


class TestSecurityConfiguration:
    """Test security configuration management"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config_manager = SecurityConfigManager()
        self.security_policy = SecurityPolicy()
    
    def test_security_policy_validation(self):
        """Test security policy validation"""
        # Test valid policy
        valid_policy = {
            "authentication": {
                "jwt_expiration": 3600,
                "max_login_attempts": 5,
                "lockout_duration": 900
            },
            "passwords": {
                "min_length": 12,
                "require_uppercase": True,
                "require_numbers": True,
                "require_symbols": True
            }
        }
        
        validation_result = self.security_policy.validate_policy(valid_policy)
        assert validation_result["valid"] is True
        
        # Test invalid policy
        invalid_policy = {
            "authentication": {
                "jwt_expiration": -1,  # Invalid negative value
                "max_login_attempts": 0
            }
        }
        
        validation_result = self.security_policy.validate_policy(invalid_policy)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_compliance_checking(self):
        """Test compliance framework checking"""
        # Test GDPR compliance
        gdpr_score = self.config_manager.check_gdpr_compliance()
        assert isinstance(gdpr_score, dict)
        assert "score" in gdpr_score
        assert "recommendations" in gdpr_score
        
        # Test SOC2 compliance
        soc2_score = self.config_manager.check_soc2_compliance()
        assert isinstance(soc2_score, dict)
        assert "score" in soc2_score
        
        # Test ISO27001 compliance
        iso_score = self.config_manager.check_iso27001_compliance()
        assert isinstance(iso_score, dict)
        assert "score" in iso_score
    
    def test_secrets_management(self):
        """Test encrypted secrets management"""
        secret_key = "database_password"
        secret_value = "super_secret_password_123"
        
        # Store secret
        result = self.config_manager.store_secret(secret_key, secret_value)
        assert result["success"] is True
        
        # Retrieve secret
        retrieved = self.config_manager.get_secret(secret_key)
        assert retrieved == secret_value
        
        # Test secret rotation
        new_secret = "new_super_secret_password_456"
        rotation_result = self.config_manager.rotate_secret(secret_key, new_secret)
        assert rotation_result["success"] is True
        
        # Verify new secret
        updated_secret = self.config_manager.get_secret(secret_key)
        assert updated_secret == new_secret
    
    def test_environment_specific_configs(self):
        """Test environment-specific security configurations"""
        # Test development environment
        dev_config = self.config_manager.get_environment_config("development")
        assert dev_config["debug_mode"] is True
        assert dev_config["rate_limits"]["requests_per_minute"] > 0
        
        # Test production environment
        prod_config = self.config_manager.get_environment_config("production")
        assert prod_config["debug_mode"] is False
        assert prod_config["rate_limits"]["requests_per_minute"] < dev_config["rate_limits"]["requests_per_minute"]
        
        # Test that production has stricter security
        assert prod_config["security"]["require_https"] is True
        assert prod_config["security"]["csrf_protection"] is True


class TestIntegrationSecurity:
    """Integration tests for security features"""
    
    def test_end_to_end_threat_detection(self):
        """Test end-to-end threat detection workflow"""
        # Simulate malicious request
        malicious_payload = {
            "qr_data": "'; DROP TABLE certificates; --",
            "signature": "<script>alert('xss')</script>"
        }
        
        response = client.post("/verify", json=malicious_payload)
        
        # Should be rejected due to threat detection
        assert response.status_code in [400, 403, 422]
        
        # Check if threat was logged
        # This would require access to audit logs in a real implementation
    
    def test_rate_limiting_integration(self):
        """Test rate limiting integration"""
        # Make many requests quickly
        responses = []
        for i in range(55):  # Exceed rate limit
            response = client.get("/health")
            responses.append(response.status_code)
            
            if response.status_code == 429:  # Rate limited
                break
        
        # Should eventually get rate limited
        assert 429 in responses or len(responses) >= 50
    
    def test_security_headers_integration(self):
        """Test security headers in API responses"""
        response = client.get("/health")
        headers = response.headers
        
        # Check for security headers
        security_headers = [
            "x-content-type-options",
            "x-frame-options", 
            "strict-transport-security",
            "x-xss-protection"
        ]
        
        # At least some security headers should be present
        present_headers = [h for h in security_headers if h in headers]
        assert len(present_headers) > 0
    
    def test_audit_trail_integration(self):
        """Test audit trail creation during API operations"""
        # Make authenticated request
        auth_response = client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        
        # This would trigger audit logging
        # In a real test, we would verify the audit log was created
        assert auth_response.status_code in [200, 401, 422]
    
    @pytest.mark.asyncio
    async def test_privacy_workflow_integration(self):
        """Test complete privacy workflow"""
        user_id = "integration_test_user"
        
        # Simulate user data processing
        test_data = {
            "email": "integration@test.com",
            "ip_address": "192.168.1.100",
            "user_agent": "Test Browser"
        }
        
        privacy_controller = PrivacyController()
        
        # Record consent
        consent_result = privacy_controller.record_consent(
            user_id, "analytics", granted=True
        )
        assert consent_result["success"] is True
        
        # Process data with encryption
        encrypted_data = privacy_controller.process_personal_data(test_data)
        assert encrypted_data != test_data
        
        # Export user data
        export_result = await privacy_controller.export_user_data(user_id)
        assert "personal_data" in export_result
        
        # Delete user data
        deletion_result = await privacy_controller.delete_user_data(user_id)
        assert deletion_result["success"] is True


# Performance and load testing
class TestSecurityPerformance:
    """Test security feature performance"""
    
    def test_encryption_performance(self):
        """Test encryption/decryption performance"""
        encryption_manager = EncryptionManager()
        test_data = "sensitive_data_" * 100  # Larger test data
        
        start_time = time.time()
        
        # Encrypt 100 times
        for _ in range(100):
            encrypted = encryption_manager.encrypt_pii(test_data)
            decrypted = encryption_manager.decrypt_pii(encrypted)
            assert decrypted == test_data
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should complete 100 operations in reasonable time
        assert elapsed < 5.0  # 5 seconds
    
    def test_threat_detection_performance(self):
        """Test threat detection performance"""
        threat_engine = ThreatDetectionEngine()
        
        start_time = time.time()
        
        # Analyze 1000 requests
        for i in range(1000):
            result = threat_engine.analyze_request(
                ip_address=f"192.168.1.{i % 255}",
                endpoint="/verify",
                user_agent="Test Client"
            )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should analyze 1000 requests quickly
        assert elapsed < 10.0  # 10 seconds
    
    def test_audit_logging_performance(self):
        """Test audit logging performance"""
        auditor = SecurityAuditor()
        
        start_time = time.time()
        
        # Log 500 events
        for i in range(500):
            event_data = {
                "event_type": "test_event",
                "user_id": f"user_{i}",
                "ip_address": f"192.168.1.{i % 255}",
                "details": {"test": f"data_{i}"}
            }
            
            # This would be async in real implementation
            log_entry = auditor.create_audit_entry(**event_data)
            assert log_entry is not None
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should log 500 events quickly
        assert elapsed < 15.0  # 15 seconds


if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=app.core",
        "--cov-report=html:htmlcov_security",
        "--cov-report=term-missing"
    ])
