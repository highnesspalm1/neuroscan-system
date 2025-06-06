#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Security Audit and Logging System
Implements comprehensive audit trails and security monitoring
"""

import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import logging.handlers
from fastapi import Request, Response
import structlog
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import ipaddress
import geoip2.database
import geoip2.errors

class SecurityEventType(Enum):
    """Types of security events to log"""
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_DENIED = "auth_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    API_KEY_USAGE = "api_key_usage"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_ERROR = "system_error"
    CONFIGURATION_CHANGE = "config_change"
    BACKUP_OPERATION = "backup_operation"
    DATA_EXPORT = "data_export"
    PRIVACY_REQUEST = "privacy_request"
    WEBHOOK_DELIVERY = "webhook_delivery"
    CERTIFICATE_VERIFICATION = "cert_verification"

class RiskLevel(Enum):
    """Risk levels for security events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    endpoint: str
    method: str
    status_code: int
    risk_level: RiskLevel
    details: Dict[str, Any]
    success: bool
    response_time_ms: float
    data_accessed: Optional[List[str]] = None
    geographical_info: Optional[Dict[str, str]] = None
    signature: Optional[str] = None

class SecurityAuditor:
    """Main security auditing system"""
    
    def __init__(self, log_dir: str = "logs", enable_geoip: bool = True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize structured logging
        self._setup_logging()
        
        # Security monitoring
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.suspicious_ips: set = set()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # GeoIP support
        self.geoip_enabled = enable_geoip
        self.geoip_db = None
        if enable_geoip:
            self._initialize_geoip()
        
        # Digital signatures for audit logs
        self._initialize_signing()
    
    def _setup_logging(self):
        """Setup structured logging with rotation"""
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Setup rotating file handlers
        self.security_logger = logging.getLogger("security")
        self.security_logger.setLevel(logging.INFO)
        
        # Security audit log (high retention)
        security_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "security_audit.log",
            maxBytes=50*1024*1024,  # 50MB
            backupCount=100
        )
        security_handler.setFormatter(logging.Formatter('%(message)s'))
        self.security_logger.addHandler(security_handler)
        
        # System events log
        self.system_logger = logging.getLogger("system")
        system_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "system_events.log",
            maxBytes=20*1024*1024,  # 20MB
            backupCount=50
        )
        self.system_logger.addHandler(system_handler)
        
        # Access log
        self.access_logger = logging.getLogger("access")
        access_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "access.log",
            maxBytes=100*1024*1024,  # 100MB
            backupCount=30
        )
        self.access_logger.addHandler(access_handler)
    
    def _initialize_geoip(self):
        """Initialize GeoIP database"""
        try:
            # Try to load GeoLite2 database (free)
            geoip_path = Path("data/GeoLite2-City.mmdb")
            if geoip_path.exists():
                self.geoip_db = geoip2.database.Reader(str(geoip_path))
        except Exception:
            self.geoip_enabled = False
    
    def _initialize_signing(self):
        """Initialize digital signing for audit log integrity"""
        try:
            # Load or generate RSA key pair for signing
            key_path = self.log_dir / "audit_signing_key.pem"
            if key_path.exists():
                with open(key_path, "rb") as key_file:
                    self.private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None
                    )
            else:
                # Generate new key pair
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                
                # Save private key
                pem = self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                with open(key_path, "wb") as key_file:
                    key_file.write(pem)
                
                # Save public key for verification
                public_key = self.private_key.public_key()
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                with open(self.log_dir / "audit_public_key.pem", "wb") as pub_file:
                    pub_file.write(public_pem)
        
        except Exception as e:
            self.private_key = None
            self.security_logger.error(f"Failed to initialize audit signing: {e}")
    
    def _sign_event(self, event_data: str) -> Optional[str]:
        """Create digital signature for audit event"""
        if not self.private_key:
            return None
        
        try:
            signature = self.private_key.sign(
                event_data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature.hex()
        except Exception:
            return None
    
    def _get_geographical_info(self, ip_address: str) -> Optional[Dict[str, str]]:
        """Get geographical information for IP address"""
        if not self.geoip_enabled or not self.geoip_db:
            return None
        
        try:
            # Skip private IP addresses
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private:
                return {"country": "Private", "city": "Private"}
            
            response = self.geoip_db.city(ip_address)
            return {
                "country": response.country.name or "Unknown",
                "city": response.city.name or "Unknown",
                "country_code": response.country.iso_code or "XX"
            }
        except (geoip2.errors.AddressNotFoundError, ValueError):
            return {"country": "Unknown", "city": "Unknown"}
    
    def _assess_risk_level(self, event_type: SecurityEventType, details: Dict[str, Any]) -> RiskLevel:
        """Assess risk level for security event"""
        # High risk events
        if event_type in [
            SecurityEventType.AUTHENTICATION_FAILURE,
            SecurityEventType.AUTHORIZATION_DENIED,
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            SecurityEventType.RATE_LIMIT_EXCEEDED
        ]:
            # Check for repeated failures
            ip_address = details.get('ip_address', '')
            if ip_address in self.suspicious_ips:
                return RiskLevel.CRITICAL
            
            # Check failed attempt patterns
            if event_type == SecurityEventType.AUTHENTICATION_FAILURE:
                recent_failures = len([
                    dt for dt in self.failed_attempts.get(ip_address, [])
                    if datetime.utcnow() - dt < timedelta(minutes=15)
                ])
                if recent_failures >= 10:
                    return RiskLevel.CRITICAL
                elif recent_failures >= 5:
                    return RiskLevel.HIGH
            
            return RiskLevel.MEDIUM
        
        # Medium risk events
        elif event_type in [
            SecurityEventType.DATA_MODIFICATION,
            SecurityEventType.CONFIGURATION_CHANGE,
            SecurityEventType.DATA_EXPORT
        ]:
            return RiskLevel.MEDIUM
        
        # Low risk events
        else:
            return RiskLevel.LOW
    
    def _update_threat_intelligence(self, event: SecurityEvent):
        """Update threat intelligence based on security events"""
        ip_address = event.ip_address
        
        # Track failed authentication attempts
        if event.event_type == SecurityEventType.AUTHENTICATION_FAILURE:
            if ip_address not in self.failed_attempts:
                self.failed_attempts[ip_address] = []
            self.failed_attempts[ip_address].append(event.timestamp)
            
            # Mark as suspicious after multiple failures
            recent_failures = [
                dt for dt in self.failed_attempts[ip_address]
                if event.timestamp - dt < timedelta(hours=1)
            ]
            
            if len(recent_failures) >= 5:
                self.suspicious_ips.add(ip_address)
        
        # Clean old failed attempts
        cutoff_time = event.timestamp - timedelta(hours=24)
        for ip in list(self.failed_attempts.keys()):
            self.failed_attempts[ip] = [
                dt for dt in self.failed_attempts[ip] if dt > cutoff_time
            ]
            if not self.failed_attempts[ip]:
                del self.failed_attempts[ip]
    
    async def log_security_event(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: str = "unknown",
        user_agent: str = "unknown",
        endpoint: str = "unknown",
        method: str = "unknown",
        status_code: int = 200,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        response_time_ms: float = 0.0,
        data_accessed: Optional[List[str]] = None
    ) -> str:
        """Log a security event with full audit trail"""
        
        event_id = hashlib.sha256(
            f"{datetime.utcnow().isoformat()}{ip_address}{endpoint}".encode()
        ).hexdigest()[:16]
        
        if details is None:
            details = {}
        
        # Get geographical information
        geo_info = self._get_geographical_info(ip_address)
        
        # Assess risk level
        risk_level = self._assess_risk_level(event_type, details)
        
        # Create security event
        event = SecurityEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            risk_level=risk_level,
            details=details,
            success=success,
            response_time_ms=response_time_ms,
            data_accessed=data_accessed,
            geographical_info=geo_info
        )
        
        # Create audit log entry
        audit_data = asdict(event)
        audit_json = json.dumps(audit_data, default=str, sort_keys=True)
        
        # Sign the audit entry
        event.signature = self._sign_event(audit_json)
        
        # Log to appropriate channels
        if event_type in [
            SecurityEventType.AUTHENTICATION_FAILURE,
            SecurityEventType.AUTHORIZATION_DENIED,
            SecurityEventType.SUSPICIOUS_ACTIVITY
        ]:
            self.security_logger.critical(json.dumps(asdict(event), default=str))
        elif risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.security_logger.error(json.dumps(asdict(event), default=str))
        else:
            self.security_logger.info(json.dumps(asdict(event), default=str))
        
        # Access logging
        self.access_logger.info(
            f"{ip_address} - - [{event.timestamp.isoformat()}] "
            f'"{method} {endpoint}" {status_code} {response_time_ms}ms'
        )
        
        # Update threat intelligence
        self._update_threat_intelligence(event)
        
        # Real-time alerting for critical events
        if risk_level == RiskLevel.CRITICAL:
            await self._send_security_alert(event)
        
        return event_id
    
    async def _send_security_alert(self, event: SecurityEvent):
        """Send real-time security alerts for critical events"""
        alert = {
            "alert_type": "SECURITY_INCIDENT",
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "ip_address": event.ip_address,
            "risk_level": event.risk_level.value,
            "details": event.details,
            "geographical_info": event.geographical_info
        }
        
        # Log the alert
        self.security_logger.critical(f"SECURITY_ALERT: {json.dumps(alert)}")
        
        # Here you could integrate with:
        # - Email alerts
        # - Slack notifications
        # - SIEM systems
        # - Incident response tools
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security summary for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Count events by type and risk level
        event_counts = {}
        risk_counts = {level.value: 0 for level in RiskLevel}
        
        # This would typically query from a database
        # For now, return basic threat intelligence
        
        suspicious_ips_count = len(self.suspicious_ips)
        active_threats = sum(
            1 for ip, attempts in self.failed_attempts.items()
            if any(attempt > cutoff_time for attempt in attempts)
        )
        
        return {
            "time_period_hours": hours,
            "suspicious_ips": suspicious_ips_count,
            "active_threats": active_threats,
            "failed_attempts_by_ip": {
                ip: len([a for a in attempts if a > cutoff_time])
                for ip, attempts in self.failed_attempts.items()
                if any(a > cutoff_time for a in attempts)
            },
            "risk_summary": risk_counts,
            "monitoring_status": "active",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def is_ip_suspicious(self, ip_address: str) -> bool:
        """Check if IP address is marked as suspicious"""
        return ip_address in self.suspicious_ips
    
    def get_audit_trail(self, user_id: Optional[str] = None, 
                       event_type: Optional[SecurityEventType] = None,
                       hours: int = 24) -> List[Dict[str, Any]]:
        """Get audit trail for specified criteria"""
        # In a real implementation, this would query the database
        # For now, return empty list with structure example
        return [
            {
                "event_id": "example123",
                "event_type": "data_access",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id or "system",
                "ip_address": "192.168.1.1",
                "success": True,
                "risk_level": "low"
            }
        ]

# Global security auditor instance
security_auditor = SecurityAuditor()

# Security logging middleware
async def security_logging_middleware(request: Request, call_next):
    """Middleware to log all security-relevant requests"""
    start_time = datetime.utcnow()
    
    # Extract request information
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    endpoint = str(request.url.path)
    method = request.method
    
    # Check if IP is suspicious
    is_suspicious = security_auditor.is_ip_suspicious(ip_address)
    
    try:
        response = await call_next(request)
        
        # Calculate response time
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Determine event type
        event_type = SecurityEventType.DATA_ACCESS
        if method in ["POST", "PUT", "PATCH", "DELETE"]:
            event_type = SecurityEventType.DATA_MODIFICATION
        
        # Log the request
        await security_auditor.log_security_event(
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=response.status_code,
            success=response.status_code < 400,
            response_time_ms=response_time,
            details={
                "suspicious_ip": is_suspicious,
                "query_params": dict(request.query_params),
                "content_type": request.headers.get("content-type", "unknown")
            }
        )
        
        return response
        
    except Exception as e:
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Log the error
        await security_auditor.log_security_event(
            event_type=SecurityEventType.SYSTEM_ERROR,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=500,
            success=False,
            response_time_ms=response_time,
            details={
                "error": str(e),
                "suspicious_ip": is_suspicious
            }
        )
        
        raise e

# Decorator for audit logging
def audit_logged(event_type: SecurityEventType):
    """Decorator to automatically log function calls"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = await func(*args, **kwargs)
                
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                await security_auditor.log_security_event(
                    event_type=event_type,
                    endpoint=func.__name__,
                    success=True,
                    response_time_ms=response_time,
                    details={"function": func.__name__}
                )
                return result
            except Exception as e:
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                await security_auditor.log_security_event(
                    event_type=SecurityEventType.SYSTEM_ERROR,
                    endpoint=func.__name__,
                    success=False,
                    response_time_ms=response_time,
                    details={"function": func.__name__, "error": str(e)}
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                # For sync functions, we'll need to handle logging differently
                # This is a simplified version
                return result
            except Exception as e:
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
