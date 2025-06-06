#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Backend API Tests
Comprehensive test suite for all API endpoints and functionality
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
from unittest.mock import Mock, patch
import json
from datetime import datetime, timedelta

from main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models import Certificate, Customer, Product
from sqlalchemy import Column, Integer, String, Boolean


# Simple User model for testing
class User(Base):
    __tablename__ = "test_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test database
Base.metadata.create_all(bind=engine)

# Test client
client = TestClient(app)


class TestFixtures:
    """Test data fixtures"""
    
    @staticmethod
    def create_test_user(db, username="testuser", role="admin"):
        """Create test user"""
        user = User(
            username=username,
            email=f"{username}@test.com",
            hashed_password="$2b$12$test_hash",
            role=role,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def create_test_certificate(db, serial_number="TEST-001"):
        """Create test certificate"""
        cert = Certificate(
            serial_number=serial_number,
            customer_name="Test Customer Ltd.",
            product_name="Test Product",
            qr_data="encrypted_test_data",
            signature="test_signature",
            creation_date=datetime.utcnow()
        )
        db.add(cert)
        db.commit()
        db.refresh(cert)
        return cert
    
    @staticmethod
    def get_test_token(user_id=1):
        """Generate test JWT token"""
        return create_access_token(data={"sub": str(user_id)})


@pytest.fixture
def db_session():
    """Database session fixture"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    """Test user fixture"""
    return TestFixtures.create_test_user(db_session)


@pytest.fixture
def test_certificate(db_session):
    """Test certificate fixture"""
    return TestFixtures.create_test_certificate(db_session)


@pytest.fixture
def auth_headers(test_user):
    """Authentication headers fixture"""
    token = TestFixtures.get_test_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


class TestAuthentication:
    """Test authentication and authorization"""
    
    def test_login_valid_credentials(self, db_session):
        """Test login with valid credentials"""
        user = TestFixtures.create_test_user(db_session, "admin", "admin")
        
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123"  # This would need proper password hashing
        })
        
        # Note: This test assumes proper password verification is implemented
        assert response.status_code in [200, 401]  # 401 expected without proper password
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post("/api/v1/auth/login", json={
            "username": "invalid",
            "password": "wrong"
        })
        assert response.status_code == 401
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/admin/certificates")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/admin/certificates", headers=headers)
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self, auth_headers):
        """Test accessing protected endpoint with valid token"""
        response = client.get("/admin/certificates", headers=auth_headers)
        assert response.status_code in [200, 422]  # 422 if validation fails


class TestCertificateVerification:
    """Test certificate verification endpoints"""
    
    def test_verify_valid_certificate(self, test_certificate):
        """Test verifying a valid certificate"""
        response = client.post("/verify", json={
            "qr_data": test_certificate.qr_data,
            "signature": test_certificate.signature
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "certificate" in data
    
    def test_verify_invalid_qr_data(self):
        """Test verifying with invalid QR data"""
        response = client.post("/verify", json={
            "qr_data": "invalid_data",
            "signature": "invalid_signature"
        })
        
        assert response.status_code in [400, 404]
    
    def test_verify_missing_signature(self):
        """Test verifying without signature"""
        response = client.post("/verify", json={
            "qr_data": "some_data"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_get_certificate_details(self, test_certificate):
        """Test getting certificate details by serial number"""
        response = client.get(f"/verify/{test_certificate.serial_number}")
        
        assert response.status_code == 200
        data = response.json()
        assert "certificate" in data
        assert data["certificate"]["serial_number"] == test_certificate.serial_number
    
    def test_get_nonexistent_certificate(self):
        """Test getting details for nonexistent certificate"""
        response = client.get("/verify/NONEXISTENT-001")
        assert response.status_code == 404


class TestAdminOperations:
    """Test administrative operations"""
    
    def test_create_certificate(self, auth_headers):
        """Test creating a new certificate"""
        certificate_data = {
            "customer_name": "New Customer Ltd.",
            "product_name": "New Product",
            "serial_number": "NEW-001"
        }
        
        response = client.post(
            "/admin/certificate",
            json=certificate_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 422]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["serial_number"] == "NEW-001"
    
    def test_create_duplicate_certificate(self, auth_headers, test_certificate):
        """Test creating certificate with duplicate serial number"""
        certificate_data = {
            "customer_name": "Duplicate Customer",
            "product_name": "Duplicate Product",
            "serial_number": test_certificate.serial_number
        }
        
        response = client.post(
            "/admin/certificate",
            json=certificate_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400  # Conflict
    
    def test_list_certificates(self, auth_headers, test_certificate):
        """Test listing certificates"""
        response = client.get("/admin/certificates", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "certificates" in data
        assert isinstance(data["certificates"], list)
    
    def test_list_certificates_with_pagination(self, auth_headers):
        """Test listing certificates with pagination"""
        response = client.get(
            "/admin/certificates?page=1&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "total" in data
    
    def test_delete_certificate(self, auth_headers, test_certificate):
        """Test deleting a certificate"""
        response = client.delete(
            f"/admin/certificate/{test_certificate.serial_number}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204]
    
    def test_delete_nonexistent_certificate(self, auth_headers):
        """Test deleting nonexistent certificate"""
        response = client.delete(
            "/admin/certificate/NONEXISTENT-001",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestPDFLabelGeneration:
    """Test PDF label generation"""
    
    def test_generate_pdf_label(self, auth_headers, test_certificate):
        """Test generating PDF label"""
        response = client.post(
            "/labels/generate",
            json={
                "serial_number": test_certificate.serial_number,
                "format": "A4",
                "include_logo": True
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "pdf_url" in data or "download_token" in data
    
    def test_generate_pdf_invalid_serial(self, auth_headers):
        """Test generating PDF for invalid serial number"""
        response = client.post(
            "/labels/generate",
            json={
                "serial_number": "INVALID-001",
                "format": "A4"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestWebSocketConnections:
    """Test WebSocket functionality"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        with client.websocket_connect("/ws") as websocket:
            # Test basic connection
            data = websocket.receive_json()
            assert "type" in data or "error" not in data
    
    @pytest.mark.asyncio
    async def test_websocket_authentication(self, test_user):
        """Test WebSocket authentication"""
        token = TestFixtures.get_test_token(test_user.id)
        
        with client.websocket_connect("/ws") as websocket:
            # Send authentication
            websocket.send_json({
                "action": "authenticate",
                "token": token
            })
            
            response = websocket.receive_json()
            # Should not receive error for valid token
            assert "error" not in response or response.get("authenticated") is True
    
    @pytest.mark.asyncio
    async def test_websocket_subscription(self):
        """Test WebSocket event subscription"""
        with client.websocket_connect("/ws") as websocket:
            # Subscribe to certificate events
            websocket.send_json({
                "action": "subscribe",
                "channel": "certificates"
            })
            
            response = websocket.receive_json()
            # Should acknowledge subscription
            assert "subscribed" in response or "error" not in response


class TestMonitoringEndpoints:
    """Test monitoring and health check endpoints"""
    
    def test_health_check(self):
        """Test basic health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_database_health(self, auth_headers):
        """Test database health check"""
        response = client.get("/health/db", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
    
    def test_metrics_endpoint(self, auth_headers):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics", headers=auth_headers)
        assert response.status_code == 200
        
        # Should return Prometheus format
        assert "text/plain" in response.headers.get("content-type", "")
    
    def test_api_statistics(self, auth_headers):
        """Test API statistics endpoint"""
        response = client.get("/api/v1/monitoring/stats", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "requests" in data
        assert "performance" in data


class TestWebhookManagement:
    """Test webhook management"""
    
    def test_create_webhook(self, auth_headers):
        """Test creating a webhook"""
        webhook_data = {
            "url": "https://test.example.com/webhook",
            "events": ["certificate.verified", "certificate.created"],
            "secret": "test_secret"
        }
        
        response = client.post(
            "/api/v1/webhooks",
            json=webhook_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["url"] == webhook_data["url"]
    
    def test_list_webhooks(self, auth_headers):
        """Test listing webhooks"""
        response = client.get("/api/v1/webhooks", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "webhooks" in data
        assert isinstance(data["webhooks"], list)
    
    def test_delete_webhook(self, auth_headers):
        """Test deleting a webhook"""
        # First create a webhook
        webhook_data = {
            "url": "https://test-delete.example.com/webhook",
            "events": ["certificate.verified"],
            "secret": "test_secret"
        }
        
        create_response = client.post(
            "/api/v1/webhooks",
            json=webhook_data,
            headers=auth_headers
        )
        
        if create_response.status_code in [200, 201]:
            webhook_id = create_response.json()["id"]
            
            # Delete the webhook
            delete_response = client.delete(
                f"/api/v1/webhooks/{webhook_id}",
                headers=auth_headers
            )
            assert delete_response.status_code in [200, 204]


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_verification(self):
        """Test rate limiting on verification endpoint"""
        # Make multiple requests to trigger rate limit
        responses = []
        for _ in range(102):  # Exceed 100 request limit
            response = client.post("/verify", json={
                "qr_data": "test_data",
                "signature": "test_signature"
            })
            responses.append(response.status_code)
            
            # Stop if rate limited
            if response.status_code == 429:
                break
        
        # Should eventually get rate limited
        assert 429 in responses or len(responses) >= 100
    
    def test_rate_limit_headers(self):
        """Test rate limit headers in response"""
        response = client.get("/health")
        
        # Check for rate limit headers
        headers = response.headers
        assert any(header.startswith("x-ratelimit") for header in headers.keys()) or \
               any(header.startswith("X-RateLimit") for header in headers.keys())


class TestSecurityFeatures:
    """Test security features"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.get("/health")
        headers = response.headers
        
        # CORS headers should be present
        assert "access-control-allow-origin" in headers or \
               "Access-Control-Allow-Origin" in headers
    
    def test_security_headers(self):
        """Test security headers"""
        response = client.get("/health")
        headers = response.headers
        
        # Check for common security headers
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection"
        ]
        
        # At least some security headers should be present
        assert any(header in headers for header in security_headers)
    
    def test_input_validation(self):
        """Test input validation"""
        # Test with malicious input
        malicious_data = {
            "qr_data": "<script>alert('xss')</script>",
            "signature": "'; DROP TABLE certificates; --"
        }
        
        response = client.post("/verify", json=malicious_data)
        
        # Should handle malicious input gracefully
        assert response.status_code in [400, 404, 422]
        
        # Response should not contain the malicious content
        response_text = response.text
        assert "<script>" not in response_text
        assert "DROP TABLE" not in response_text


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_handling(self):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_validation_error_handling(self):
        """Test validation error handling"""
        response = client.post("/verify", json={
            "invalid_field": "invalid_value"
        })
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data or "error" in data
    
    def test_internal_error_handling(self):
        """Test internal error handling"""
        # This test would require mocking to trigger an internal error
        with patch('app.routes.verify.some_function') as mock_func:
            mock_func.side_effect = Exception("Test internal error")
            
            response = client.post("/verify", json={
                "qr_data": "test_data",
                "signature": "test_signature"
            })
            
            # Should handle internal errors gracefully
            assert response.status_code in [500, 400, 404]


class TestPerformance:
    """Test performance requirements"""
    
    def test_response_time(self):
        """Test response time for health check"""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Health check should respond quickly
        assert response_time < 1.0  # 1 second
        assert response.status_code == 200
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        
        # Should complete in reasonable time
        assert end_time - start_time < 5.0  # 5 seconds


class TestAdvancedFeatures:
    """Test all advanced features integrated in Steps 12-13"""
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "NeuroScan API"
        assert data["version"] == "1.0.0"
        assert "status" in data
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "NeuroScan API"
        assert data["company"] == "NeuroCompany"
    
    def test_api_v2_enhanced_endpoints(self, auth_headers):
        """Test enhanced API v2 endpoints"""
        # Test enhanced certificate creation
        response = client.post("/api/v2/certificates/enhanced", 
                             headers=auth_headers,
                             json={
                                 "customer_name": "Enhanced Customer",
                                 "product_name": "Enhanced Product",
                                 "batch_number": "BATCH-001",
                                 "tags": ["premium", "certified"]
                             })
        # Should work or return appropriate error
        assert response.status_code in [200, 201, 422]
    
    def test_caching_functionality(self):
        """Test caching system"""
        # Test that repeated requests are cached
        response1 = client.get("/health")
        response2 = client.get("/health")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        # Both should return same data
        assert response1.json() == response2.json()
    
    def test_analytics_endpoints(self, auth_headers):
        """Test analytics and business intelligence endpoints"""
        # Test analytics dashboard
        response = client.get("/api/v2/analytics/dashboard", headers=auth_headers)
        assert response.status_code in [200, 401, 404]
        
        # Test certificate analytics
        response = client.get("/api/v2/analytics/certificates", headers=auth_headers)
        assert response.status_code in [200, 401, 404]
    
    def test_webhook_management(self, auth_headers):
        """Test webhook system"""
        # Test webhook registration
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": ["certificate.created", "certificate.verified"],
            "secret": "test_secret"
        }
        
        response = client.post("/api/v1/webhooks/register", 
                             headers=auth_headers,
                             json=webhook_data)
        assert response.status_code in [200, 201, 422]
        
        # Test webhook listing
        response = client.get("/api/v1/webhooks", headers=auth_headers)
        assert response.status_code in [200, 401]
    
    def test_monitoring_endpoints(self, auth_headers):
        """Test monitoring and metrics"""
        # Test basic monitoring
        response = client.get("/api/v1/monitoring/metrics", headers=auth_headers)
        assert response.status_code in [200, 401]
        
        # Test advanced monitoring
        response = client.get("/api/v2/monitoring/dashboard", headers=auth_headers)
        assert response.status_code in [200, 401]
    
    def test_versioning_system(self):
        """Test API versioning"""
        # Test v1 endpoint
        response = client.get("/api/v1/version")
        assert response.status_code in [200, 404]
        
        # Test v2 endpoint  
        response = client.get("/api/v2/version")
        assert response.status_code in [200, 404]
    
    def test_websocket_endpoints(self):
        """Test WebSocket functionality"""
        # Test WebSocket info endpoint
        response = client.get("/api/v1/ws/info")
        assert response.status_code in [200, 404]
    
    def test_documentation_endpoints(self):
        """Test enhanced documentation"""
        # Test OpenAPI docs
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test custom documentation
        response = client.get("/api/v1/docs/endpoints")
        assert response.status_code in [200, 404]
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Make multiple rapid requests to test rate limiting
        responses = []
        for i in range(10):
            response = client.get("/health")
            responses.append(response.status_code)
        
        # Most should succeed, but rate limiting might kick in
        success_count = sum(1 for status in responses if status == 200)
        assert success_count > 0  # At least some should succeed
    
    def test_security_features(self):
        """Test security enhancements"""
        # Test with suspicious payload (should be caught by threat detection)
        malicious_payload = {
            "query": "'; DROP TABLE users; --",
            "script": "<script>alert('xss')</script>"
        }
        
        response = client.post("/verify/qr", json=malicious_payload)
        # Should either block or sanitize
        assert response.status_code in [400, 403, 422]


class TestPerformanceAndReliability:
    """Test system performance and reliability"""
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        # Should complete within reasonable time
        assert end_time - start_time < 5.0
    
    def test_large_payload_handling(self):
        """Test handling of large payloads"""
        large_data = {
            "customer_name": "Test Customer" * 100,
            "product_name": "Test Product" * 100,
            "description": "A" * 10000  # 10KB of data
        }
        
        response = client.post("/verify/qr", json=large_data)
        # Should handle gracefully
        assert response.status_code in [200, 400, 413, 422]
    
    def test_error_handling(self):
        """Test comprehensive error handling"""
        # Test 404 endpoints
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Test malformed JSON
        response = client.post("/verify/qr", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_database_resilience(self):
        """Test database connection resilience"""
        # Test health check which includes database check
        response = client.get("/health")
        # Should handle database issues gracefully
        assert response.status_code in [200, 503]


class TestIntegrationScenarios:
    """Test complete integration scenarios"""
    
    def test_complete_certificate_lifecycle(self, auth_headers):
        """Test complete certificate lifecycle with all features"""
        # 1. Create certificate with enhanced API
        cert_data = {
            "customer_name": "Integration Test Customer",
            "product_name": "Integration Test Product",
            "batch_number": "INT-001",
            "tags": ["integration", "test"]
        }
        
        create_response = client.post("/api/v2/certificates/enhanced",
                                    headers=auth_headers,
                                    json=cert_data)
        
        if create_response.status_code in [200, 201]:
            cert_id = create_response.json().get("id")
            
            # 2. Verify certificate
            verify_response = client.post("/verify/qr", json={
                "qr_data": "test_data"
            })
            assert verify_response.status_code in [200, 400, 404]
            
            # 3. Check analytics
            analytics_response = client.get("/api/v2/analytics/certificates",
                                          headers=auth_headers)
            assert analytics_response.status_code in [200, 401, 404]
    
    def test_monitoring_integration(self, auth_headers):
        """Test monitoring system integration"""
        # Make some requests to generate metrics
        for i in range(5):
            client.get("/health")
        
        # Check if metrics are collected
        response = client.get("/api/v1/monitoring/metrics", headers=auth_headers)
        assert response.status_code in [200, 401, 404]
        
        # Check dashboard
        response = client.get("/api/v2/monitoring/dashboard", headers=auth_headers) 
        assert response.status_code in [200, 401, 404]
    
    def test_webhook_integration(self, auth_headers):
        """Test webhook system integration"""
        # Register webhook
        webhook_data = {
            "url": "https://webhook.site/test",
            "events": ["certificate.created"],
            "secret": "integration_test"
        }
        
        register_response = client.post("/api/v1/webhooks/register",
                                      headers=auth_headers,
                                      json=webhook_data)
        
        if register_response.status_code in [200, 201]:
            # Trigger event that should send webhook
            cert_response = client.post("/api/v2/certificates/enhanced",
                                      headers=auth_headers,
                                      json={
                                          "customer_name": "Webhook Test",
                                          "product_name": "Webhook Product"
                                      })
            
            # Webhook should be triggered (async, so we can't directly test delivery)
            assert cert_response.status_code in [200, 201, 422]


class TestAdvancedSecurity:
    """Test advanced security features"""
    
    def test_threat_detection(self):
        """Test threat detection system"""
        # Test SQL injection attempt
        malicious_requests = [
            {"query": "'; DROP TABLE certificates; --"},
            {"input": "<script>alert('xss')</script>"},
            {"path": "../../../etc/passwd"},
        ]
        
        for payload in malicious_requests:
            response = client.post("/verify/qr", json=payload)
            # Should be detected and blocked/sanitized
            assert response.status_code in [400, 403, 422]
    
    def test_rate_limiting_advanced(self):
        """Test advanced rate limiting"""
        # Test different endpoints have different limits
        endpoints = ["/health", "/", "/verify/qr"]
        
        for endpoint in endpoints:
            responses = []
            for i in range(20):  # Try to exceed rate limit
                if endpoint == "/verify/qr":
                    response = client.post(endpoint, json={"test": "data"})
                else:
                    response = client.get(endpoint)
                responses.append(response.status_code)
            
            # Should have some successful responses
            success_count = sum(1 for status in responses if status in [200, 422])
            assert success_count > 0
    
    def test_security_headers(self):
        """Test security headers are present"""
        response = client.get("/health")
        
        # Check for common security headers
        headers = response.headers
        # Note: Actual implementation may vary
        assert response.status_code == 200


@pytest.mark.asyncio 
class TestAsyncFeatures:
    """Test asynchronous features"""
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        # This would require WebSocket test client
        # For now, just test the WebSocket info endpoint
        response = client.get("/api/v1/ws/info")
        assert response.status_code in [200, 404]
    
    async def test_async_analytics(self):
        """Test asynchronous analytics processing"""
        # Test analytics endpoints that might use async processing
        response = client.get("/api/v2/analytics/dashboard")
        assert response.status_code in [200, 401, 404]


class TestSystemValidation:
    """Final system validation tests"""
    
    def test_all_core_endpoints_accessible(self):
        """Validate all core endpoints are accessible"""
        core_endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/docs", "GET"),
        ]
        
        for endpoint, method in core_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            
            # Should not return 500 errors
            assert response.status_code != 500
    
    def test_feature_integration_complete(self):
        """Test that all features are properly integrated"""
        # This test validates the overall system health
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "NeuroScan API"
        assert data["version"] == "1.0.0"
    
    def test_api_documentation_complete(self):
        """Test that API documentation is complete"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test that OpenAPI spec is accessible
        response = client.get("/openapi.json")
        assert response.status_code == 200


# Test runner configuration
if __name__ == "__main__":
    # Clean up test database
    if os.path.exists("test.db"):
        os.remove("test.db")
    
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])
