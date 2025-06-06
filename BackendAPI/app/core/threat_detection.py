#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Threat Detection and Prevention System
Advanced security monitoring and automated threat response
"""

import asyncio
import ipaddress
import re
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict, deque
import json
import sqlite3
from pathlib import Path
import aioredis
import dns.resolver
import requests
from user_agents import parse as parse_user_agent

class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    DIRECTORY_TRAVERSAL = "directory_traversal"
    RATE_LIMIT_ABUSE = "rate_limit_abuse"
    BOT_TRAFFIC = "bot_traffic"
    SUSPICIOUS_USER_AGENT = "suspicious_user_agent"
    GEOLOCATION_ANOMALY = "geolocation_anomaly"
    API_ABUSE = "api_abuse"
    DATA_SCRAPING = "data_scraping"
    MALFORMED_REQUEST = "malformed_request"
    KNOWN_MALICIOUS_IP = "known_malicious_ip"

class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ActionType(Enum):
    """Automated response actions"""
    LOG_ONLY = "log_only"
    RATE_LIMIT = "rate_limit"
    TEMPORARY_BLOCK = "temporary_block"
    PERMANENT_BLOCK = "permanent_block"
    CAPTCHA_CHALLENGE = "captcha_challenge"
    ENHANCED_MONITORING = "enhanced_monitoring"
    ALERT_ADMIN = "alert_admin"

@dataclass
class ThreatDetection:
    """Threat detection result"""
    threat_id: str
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: float  # 0.0 to 1.0
    source_ip: str
    endpoint: str
    timestamp: datetime
    details: Dict[str, Any]
    suggested_action: ActionType
    evidence: List[str]

@dataclass
class SecurityRule:
    """Security rule definition"""
    rule_id: str
    name: str
    threat_type: ThreatType
    pattern: str
    severity: ThreatSeverity
    action: ActionType
    enabled: bool = True
    false_positive_rate: float = 0.0

class ThreatIntelligence:
    """Threat intelligence feeds and databases"""
    
    def __init__(self):
        self.malicious_ips: Set[str] = set()
        self.known_bots: Set[str] = set()
        self.suspicious_patterns: List[str] = []
        self.reputation_cache: Dict[str, Dict[str, Any]] = {}
        self.last_update = datetime.utcnow()
        
        # Load default threat intelligence
        self._load_default_intelligence()
    
    def _load_default_intelligence(self):
        """Load default threat intelligence data"""
        # Known malicious user agents
        self.malicious_user_agents = {
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zgrab',
            'shodan', 'censys', 'scanner', 'crawler',
            'bot', 'spider', 'scraper', 'harvester'
        }
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            r"(\s*(union|select|insert|delete|update|drop|create|alter)\s+)",
            r"(\s*(or|and)\s+\d+\s*=\s*\d+)",
            r"('|\"|`|;|--|/\*|\*/|\bxp_)",
            r"(\bexec\s*\(|\bexecute\s*\()",
            r"(\bsp_\w+|\bxp_\w+)"
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript\s*:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>"
        ]
        
        # Directory traversal patterns
        self.traversal_patterns = [
            r"\.\.[\\/]",
            r"\.\.%2f",
            r"\.\.%5c",
            r"%2e%2e%2f",
            r"%2e%2e%5c"
        ]
    
    def is_malicious_ip(self, ip: str) -> bool:
        """Check if IP is known to be malicious"""
        return ip in self.malicious_ips
    
    def is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""
        ua_lower = user_agent.lower()
        return any(pattern in ua_lower for pattern in self.malicious_user_agents)
    
    def check_sql_injection(self, text: str) -> bool:
        """Check for SQL injection patterns"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) 
                  for pattern in self.sql_injection_patterns)
    
    def check_xss(self, text: str) -> bool:
        """Check for XSS patterns"""
        return any(re.search(pattern, text, re.IGNORECASE) 
                  for pattern in self.xss_patterns)
    
    def check_directory_traversal(self, text: str) -> bool:
        """Check for directory traversal patterns"""
        return any(re.search(pattern, text, re.IGNORECASE) 
                  for pattern in self.traversal_patterns)

class RateLimitTracker:
    """Advanced rate limiting with sliding windows"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.violations: Dict[str, int] = defaultdict(int)
        
        # Rate limit configurations
        self.limits = {
            'global': {'requests': 100, 'window': 60},      # 100 req/min global
            'api': {'requests': 50, 'window': 60},          # 50 req/min for API
            'auth': {'requests': 5, 'window': 300},         # 5 auth/5min
            'verify': {'requests': 20, 'window': 60}        # 20 verify/min
        }
    
    def check_rate_limit(self, identifier: str, endpoint_type: str = 'global') -> Tuple[bool, int]:
        """Check if request exceeds rate limit"""
        current_time = time.time()
        limit_config = self.limits.get(endpoint_type, self.limits['global'])
        
        # Clean old requests
        requests_queue = self.requests[identifier]
        while requests_queue and current_time - requests_queue[0] > limit_config['window']:
            requests_queue.popleft()
        
        # Check if limit exceeded
        if len(requests_queue) >= limit_config['requests']:
            self.violations[identifier] += 1
            return False, len(requests_queue)
        
        # Add current request
        requests_queue.append(current_time)
        return True, len(requests_queue)
    
    def get_violation_count(self, identifier: str) -> int:
        """Get number of rate limit violations"""
        return self.violations.get(identifier, 0)

class AnomalyDetector:
    """Behavioral anomaly detection"""
    
    def __init__(self):
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.endpoint_baselines: Dict[str, Dict[str, float]] = {}
        self.geographic_baselines: Dict[str, Set[str]] = {}
    
    def update_user_profile(self, user_id: str, request_data: Dict[str, Any]):
        """Update user behavioral profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'request_count': 0,
                'endpoints': set(),
                'user_agents': set(),
                'ip_addresses': set(),
                'countries': set(),
                'request_times': [],
                'last_seen': datetime.utcnow()
            }
        
        profile = self.user_profiles[user_id]
        profile['request_count'] += 1
        profile['endpoints'].add(request_data.get('endpoint', ''))
        profile['user_agents'].add(request_data.get('user_agent', ''))
        profile['ip_addresses'].add(request_data.get('ip_address', ''))
        
        if 'country' in request_data:
            profile['countries'].add(request_data['country'])
        
        profile['request_times'].append(datetime.utcnow())
        profile['last_seen'] = datetime.utcnow()
        
        # Keep only recent request times (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        profile['request_times'] = [
            t for t in profile['request_times'] if t > cutoff
        ]
    
    def detect_anomalies(self, user_id: str, request_data: Dict[str, Any]) -> List[str]:
        """Detect behavioral anomalies"""
        anomalies = []
        
        if user_id not in self.user_profiles:
            return anomalies
        
        profile = self.user_profiles[user_id]
        
        # Check for geographic anomaly
        if 'country' in request_data:
            country = request_data['country']
            if country not in profile['countries'] and len(profile['countries']) > 0:
                # First time from this country
                if len(profile['countries']) == 1:
                    anomalies.append("New geographic location detected")
        
        # Check for new user agent
        user_agent = request_data.get('user_agent', '')
        if user_agent not in profile['user_agents'] and len(profile['user_agents']) > 0:
            # Completely different user agent family
            parsed_ua = parse_user_agent(user_agent)
            existing_families = {parse_user_agent(ua).browser.family 
                               for ua in profile['user_agents']}
            
            if parsed_ua.browser.family not in existing_families:
                anomalies.append("New browser/client detected")
        
        # Check for velocity anomaly
        if len(profile['request_times']) > 10:
            recent_requests = [
                t for t in profile['request_times'] 
                if datetime.utcnow() - t < timedelta(minutes=5)
            ]
            
            if len(recent_requests) > 20:
                anomalies.append("High request velocity detected")
        
        return anomalies

class ThreatDetectionEngine:
    """Main threat detection and prevention engine"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.threat_intel = ThreatIntelligence()
        self.rate_limiter = RateLimitTracker()
        self.anomaly_detector = AnomalyDetector()
        
        # Blocked IPs and temporary blocks
        self.blocked_ips: Set[str] = set()
        self.temp_blocks: Dict[str, datetime] = {}
        
        # Detection statistics
        self.detection_stats = {
            'total_requests': 0,
            'threats_detected': 0,
            'threats_blocked': 0,
            'false_positives': 0
        }
        
        # Security rules
        self.security_rules: List[SecurityRule] = []
        self._load_default_rules()
        
        # Redis for distributed blocking (optional)
        self.redis = None
        if redis_url:
            asyncio.create_task(self._initialize_redis(redis_url))
    
    async def _initialize_redis(self, redis_url: str):
        """Initialize Redis connection for distributed blocking"""
        try:
            self.redis = await aioredis.from_url(redis_url)
        except Exception:
            self.redis = None
    
    def _load_default_rules(self):
        """Load default security rules"""
        rules = [
            SecurityRule(
                "sql_injection_1",
                "SQL Injection Detection",
                ThreatType.SQL_INJECTION,
                "union|select|insert|delete|update|drop",
                ThreatSeverity.HIGH,
                ActionType.TEMPORARY_BLOCK
            ),
            SecurityRule(
                "xss_attempt_1",
                "XSS Attempt Detection", 
                ThreatType.XSS_ATTEMPT,
                "<script|javascript:|on\\w+=",
                ThreatSeverity.MEDIUM,
                ActionType.RATE_LIMIT
            ),
            SecurityRule(
                "directory_traversal_1",
                "Directory Traversal Detection",
                ThreatType.DIRECTORY_TRAVERSAL,
                "\\.\\.[/\\\\]|%2e%2e%2f",
                ThreatSeverity.HIGH,
                ActionType.TEMPORARY_BLOCK
            ),
            SecurityRule(
                "brute_force_1",
                "Brute Force Detection",
                ThreatType.BRUTE_FORCE,
                "",  # Behavioral detection
                ThreatSeverity.HIGH,
                ActionType.TEMPORARY_BLOCK
            )
        ]
        
        self.security_rules.extend(rules)
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked"""
        # Check permanent blocks
        if ip in self.blocked_ips:
            return True
        
        # Check temporary blocks
        if ip in self.temp_blocks:
            if datetime.utcnow() < self.temp_blocks[ip]:
                return True
            else:
                # Block expired
                del self.temp_blocks[ip]
        
        return False
    
    def block_ip(self, ip: str, duration_minutes: Optional[int] = None):
        """Block an IP address"""
        if duration_minutes:
            # Temporary block
            expiry = datetime.utcnow() + timedelta(minutes=duration_minutes)
            self.temp_blocks[ip] = expiry
            
            # Store in Redis if available
            if self.redis:
                asyncio.create_task(
                    self.redis.setex(f"blocked_ip:{ip}", duration_minutes * 60, "1")
                )
        else:
            # Permanent block
            self.blocked_ips.add(ip)
            
            # Store in Redis if available
            if self.redis:
                asyncio.create_task(
                    self.redis.sadd("permanently_blocked_ips", ip)
                )
    
    async def analyze_request(self, request_data: Dict[str, Any]) -> Optional[ThreatDetection]:
        """Analyze request for threats"""
        self.detection_stats['total_requests'] += 1
        
        ip_address = request_data.get('ip_address', '')
        endpoint = request_data.get('endpoint', '')
        method = request_data.get('method', '')
        user_agent = request_data.get('user_agent', '')
        query_params = request_data.get('query_params', {})
        headers = request_data.get('headers', {})
        
        # Check if IP is already blocked
        if self.is_ip_blocked(ip_address):
            return ThreatDetection(
                threat_id=self._generate_threat_id(),
                threat_type=ThreatType.KNOWN_MALICIOUS_IP,
                severity=ThreatSeverity.HIGH,
                confidence=1.0,
                source_ip=ip_address,
                endpoint=endpoint,
                timestamp=datetime.utcnow(),
                details={'blocked_ip': True},
                suggested_action=ActionType.PERMANENT_BLOCK,
                evidence=['IP is in blocked list']
            )
        
        # Rate limiting check
        endpoint_type = self._get_endpoint_type(endpoint)
        allowed, request_count = self.rate_limiter.check_rate_limit(ip_address, endpoint_type)
        
        if not allowed:
            violations = self.rate_limiter.get_violation_count(ip_address)
            severity = ThreatSeverity.MEDIUM if violations < 5 else ThreatSeverity.HIGH
            
            threat = ThreatDetection(
                threat_id=self._generate_threat_id(),
                threat_type=ThreatType.RATE_LIMIT_ABUSE,
                severity=severity,
                confidence=0.9,
                source_ip=ip_address,
                endpoint=endpoint,
                timestamp=datetime.utcnow(),
                details={
                    'request_count': request_count,
                    'violations': violations,
                    'endpoint_type': endpoint_type
                },
                suggested_action=ActionType.TEMPORARY_BLOCK if violations >= 3 else ActionType.RATE_LIMIT,
                evidence=[f'Rate limit exceeded: {request_count} requests']
            )
            
            self.detection_stats['threats_detected'] += 1
            return threat
        
        # Check threat intelligence
        if self.threat_intel.is_malicious_ip(ip_address):
            return ThreatDetection(
                threat_id=self._generate_threat_id(),
                threat_type=ThreatType.KNOWN_MALICIOUS_IP,
                severity=ThreatSeverity.CRITICAL,
                confidence=0.95,
                source_ip=ip_address,
                endpoint=endpoint,
                timestamp=datetime.utcnow(),
                details={'threat_intel_match': True},
                suggested_action=ActionType.PERMANENT_BLOCK,
                evidence=['IP matches threat intelligence']
            )
        
        # Check suspicious user agent
        if self.threat_intel.is_suspicious_user_agent(user_agent):
            return ThreatDetection(
                threat_id=self._generate_threat_id(),
                threat_type=ThreatType.SUSPICIOUS_USER_AGENT,
                severity=ThreatSeverity.MEDIUM,
                confidence=0.7,
                source_ip=ip_address,
                endpoint=endpoint,
                timestamp=datetime.utcnow(),
                details={'user_agent': user_agent},
                suggested_action=ActionType.ENHANCED_MONITORING,
                evidence=['Suspicious user agent detected']
            )
        
        # Check for injection attacks
        all_inputs = []
        all_inputs.extend(str(v) for v in query_params.values())
        all_inputs.extend(str(v) for v in headers.values())
        if 'body' in request_data:
            all_inputs.append(str(request_data['body']))
        
        combined_input = ' '.join(all_inputs).lower()
        
        # SQL Injection check
        if self.threat_intel.check_sql_injection(combined_input):
            return ThreatDetection(
                threat_id=self._generate_threat_id(),
                threat_type=ThreatType.SQL_INJECTION,
                severity=ThreatSeverity.HIGH,
                confidence=0.85,
                source_ip=ip_address,
                endpoint=endpoint,
                timestamp=datetime.utcnow(),
                details={'injection_detected': True, 'payload': combined_input[:200]},
                suggested_action=ActionType.TEMPORARY_BLOCK,
                evidence=['SQL injection patterns detected']
            )
        
        # XSS check
        if self.threat_intel.check_xss(combined_input):
            return ThreatDetection(
                threat_id=self._generate_threat_id(),
                threat_type=ThreatType.XSS_ATTEMPT,
                severity=ThreatSeverity.MEDIUM,
                confidence=0.8,
                source_ip=ip_address,
                endpoint=endpoint,
                timestamp=datetime.utcnow(),
                details={'xss_detected': True, 'payload': combined_input[:200]},
                suggested_action=ActionType.RATE_LIMIT,
                evidence=['XSS patterns detected']
            )
        
        # Directory traversal check
        if self.threat_intel.check_directory_traversal(combined_input):
            return ThreatDetection(
                threat_id=self._generate_threat_id(),
                threat_type=ThreatType.DIRECTORY_TRAVERSAL,
                severity=ThreatSeverity.HIGH,
                confidence=0.9,
                source_ip=ip_address,
                endpoint=endpoint,
                timestamp=datetime.utcnow(),
                details={'traversal_detected': True, 'payload': combined_input[:200]},
                suggested_action=ActionType.TEMPORARY_BLOCK,
                evidence=['Directory traversal patterns detected']
            )
        
        # Behavioral anomaly detection
        user_id = request_data.get('user_id')
        if user_id:
            self.anomaly_detector.update_user_profile(user_id, request_data)
            anomalies = self.anomaly_detector.detect_anomalies(user_id, request_data)
            
            if anomalies:
                return ThreatDetection(
                    threat_id=self._generate_threat_id(),
                    threat_type=ThreatType.GEOLOCATION_ANOMALY,
                    severity=ThreatSeverity.LOW,
                    confidence=0.6,
                    source_ip=ip_address,
                    endpoint=endpoint,
                    timestamp=datetime.utcnow(),
                    details={'anomalies': anomalies},
                    suggested_action=ActionType.ENHANCED_MONITORING,
                    evidence=anomalies
                )
        
        return None
    
    def _get_endpoint_type(self, endpoint: str) -> str:
        """Determine endpoint type for rate limiting"""
        if '/api/' in endpoint:
            return 'api'
        elif '/auth/' in endpoint or '/login' in endpoint:
            return 'auth'
        elif '/verify/' in endpoint:
            return 'verify'
        else:
            return 'global'
    
    def _generate_threat_id(self) -> str:
        """Generate unique threat ID"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"threat_{timestamp}_{random_part}"
    
    async def execute_threat_response(self, threat: ThreatDetection) -> Dict[str, Any]:
        """Execute automated threat response"""
        response = {
            'threat_id': threat.threat_id,
            'action_taken': threat.suggested_action.value,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if threat.suggested_action == ActionType.TEMPORARY_BLOCK:
            # Block IP for 30 minutes for medium severity, 2 hours for high
            duration = 30 if threat.severity == ThreatSeverity.MEDIUM else 120
            self.block_ip(threat.source_ip, duration)
            response['block_duration_minutes'] = duration
            self.detection_stats['threats_blocked'] += 1
        
        elif threat.suggested_action == ActionType.PERMANENT_BLOCK:
            self.block_ip(threat.source_ip)
            response['block_type'] = 'permanent'
            self.detection_stats['threats_blocked'] += 1
        
        elif threat.suggested_action == ActionType.RATE_LIMIT:
            # Additional rate limiting is handled by the rate limiter
            response['rate_limit_applied'] = True
        
        elif threat.suggested_action == ActionType.ENHANCED_MONITORING:
            # Mark for enhanced monitoring
            response['monitoring_enhanced'] = True
        
        elif threat.suggested_action == ActionType.ALERT_ADMIN:
            # Send admin alert (implementation depends on notification system)
            response['admin_alerted'] = True
        
        return response
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat detection statistics"""
        return {
            'total_requests': self.detection_stats['total_requests'],
            'threats_detected': self.detection_stats['threats_detected'],
            'threats_blocked': self.detection_stats['threats_blocked'],
            'false_positives': self.detection_stats['false_positives'],
            'detection_rate': (
                self.detection_stats['threats_detected'] / 
                max(self.detection_stats['total_requests'], 1)
            ),
            'blocked_ips_count': len(self.blocked_ips),
            'temp_blocks_count': len(self.temp_blocks),
            'active_rules': len([r for r in self.security_rules if r.enabled]),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def whitelist_ip(self, ip: str):
        """Add IP to whitelist (remove from blocked lists)"""
        self.blocked_ips.discard(ip)
        if ip in self.temp_blocks:
            del self.temp_blocks[ip]
        
        if self.redis:
            asyncio.create_task(self.redis.srem("permanently_blocked_ips", ip))
            asyncio.create_task(self.redis.delete(f"blocked_ip:{ip}"))

# Global threat detection engine
threat_detector = ThreatDetectionEngine()

# Middleware for threat detection
async def threat_detection_middleware(request, call_next):
    """Middleware to detect and respond to threats"""
    # Extract request data
    request_data = {
        'ip_address': request.client.host if request.client else 'unknown',
        'endpoint': str(request.url.path),
        'method': request.method,
        'user_agent': request.headers.get('user-agent', ''),
        'query_params': dict(request.query_params),
        'headers': dict(request.headers)
    }
    
    # Check for threats
    threat = await threat_detector.analyze_request(request_data)
    
    if threat:
        # Execute threat response
        response_info = await threat_detector.execute_threat_response(threat)
        
        # If IP should be blocked, return 403
        if threat.suggested_action in [ActionType.TEMPORARY_BLOCK, ActionType.PERMANENT_BLOCK]:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Access denied",
                    "threat_id": threat.threat_id,
                    "reason": "Security policy violation"
                }
            )
    
    # Continue with request
    response = await call_next(request)
    return response
