"""
Database schema for advanced features
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class Metrics(Base):
    """Metrics storage for analytics"""
    __tablename__ = "metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    value = Column(Float, nullable=False)
    labels = Column(JSON)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    metric_type = Column(String(50), nullable=False)
    unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_metrics_name_timestamp', 'name', 'timestamp'),
        Index('idx_metrics_labels_gin', 'labels', postgresql_using='gin'),
    )

class WebhookEndpoints(Base):
    """Webhook endpoint configurations"""
    __tablename__ = "webhook_endpoints"
    
    id = Column(String(255), primary_key=True)
    url = Column(String(2048), nullable=False)
    secret = Column(String(255), nullable=False)
    events = Column(JSON, nullable=False)  # List of subscribed events
    active = Column(Boolean, default=True, index=True)
    headers = Column(JSON)  # Custom headers
    timeout = Column(Integer, default=30)
    max_retries = Column(Integer, default=3)
    retry_delay = Column(Integer, default=60)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)
    
    # Relationship to webhook events
    events_sent = relationship("WebhookEvents", back_populates="endpoint")

class WebhookEvents(Base):
    """Webhook event delivery tracking"""
    __tablename__ = "webhook_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(255), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    endpoint_id = Column(String(255), ForeignKey('webhook_endpoints.id'), nullable=False, index=True)
    status = Column(String(50), nullable=False, default='pending', index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    scheduled_at = Column(DateTime, index=True)
    delivered_at = Column(DateTime)
    attempts = Column(Integer, default=0)
    last_error = Column(Text)
    signature = Column(String(255))
    response_status = Column(Integer)
    response_body = Column(Text)
    delivery_time = Column(Float)  # Response time in seconds
    
    # Relationship to endpoint
    endpoint = relationship("WebhookEndpoints", back_populates="events_sent")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_webhook_events_endpoint_status', 'endpoint_id', 'status'),
        Index('idx_webhook_events_created_at', 'created_at'),
    )

class CacheEntries(Base):
    """Cache entries tracking (optional, for analytics)"""
    __tablename__ = "cache_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(500), nullable=False, unique=True, index=True)
    namespace = Column(String(255), index=True)
    size_bytes = Column(Integer)
    ttl = Column(Integer)
    hits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, index=True)

class ApiVersions(Base):
    """API version management"""
    __tablename__ = "api_versions"
    
    version = Column(String(50), primary_key=True)
    status = Column(String(50), nullable=False)  # current, deprecated, sunset, removed
    release_date = Column(DateTime, nullable=False)
    deprecation_date = Column(DateTime)
    sunset_date = Column(DateTime)
    changelog = Column(Text)
    breaking_changes = Column(JSON)  # List of breaking changes
    migration_guide_url = Column(String(2048))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSessions(Base):
    """Enhanced user session tracking"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    session_token = Column(String(500), nullable=False, unique=True, index=True)
    client_ip = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    device_fingerprint = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    metadata = Column(JSON)  # Additional session data
    
    # Security fields
    login_method = Column(String(50))  # password, oauth, sso
    mfa_verified = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_user_sessions_user_active', 'user_id', 'is_active'),
        Index('idx_user_sessions_expires', 'expires_at'),
    )

class ProductScans(Base):
    """Enhanced product scan tracking"""
    __tablename__ = "product_scans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    scan_result = Column(String(50), nullable=False)  # success, failed, suspicious
    authenticity_score = Column(Float)
    scan_engine_version = Column(String(50))
    scan_duration_ms = Column(Integer)
    client_ip = Column(String(45))
    user_agent = Column(Text)
    device_info = Column(JSON)
    location_data = Column(JSON)  # Geolocation if available
    qr_code_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Security and fraud detection
    risk_indicators = Column(JSON)  # List of risk factors
    fraud_score = Column(Float, default=0.0)
    verified_by_human = Column(Boolean)
    
    # Performance metrics
    cache_hit = Column(Boolean, default=False)
    processing_nodes = Column(JSON)  # Which servers processed the scan
    
    # Indexes for analytics
    __table_args__ = (
        Index('idx_product_scans_product_date', 'product_id', 'created_at'),
        Index('idx_product_scans_user_date', 'user_id', 'created_at'),
        Index('idx_product_scans_result_date', 'scan_result', 'created_at'),
    )

class SecurityEvents(Base):
    """Security event tracking"""
    __tablename__ = "security_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(255), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)  # low, medium, high, critical
    user_id = Column(String(255), index=True)
    client_ip = Column(String(45), index=True)
    user_agent = Column(Text)
    details = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Response tracking
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(255))
    acknowledged_at = Column(DateTime)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(String(255))
    resolved_at = Column(DateTime)
    
    # Automation
    auto_resolved = Column(Boolean, default=False)
    suppressed = Column(Boolean, default=False)
    false_positive = Column(Boolean, default=False)
    
    # Indexes for security monitoring
    __table_args__ = (
        Index('idx_security_events_type_severity', 'event_type', 'severity'),
        Index('idx_security_events_ip_date', 'client_ip', 'created_at'),
        Index('idx_security_events_unresolved', 'resolved', 'created_at'),
    )

class SystemHealthMetrics(Base):
    """System health and performance metrics"""
    __tablename__ = "system_health_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(255), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    component = Column(String(255), index=True)  # api, database, cache, etc.
    hostname = Column(String(255), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON)
    
    # Thresholds for alerting
    warning_threshold = Column(Float)
    critical_threshold = Column(Float)
    
    # Indexes for monitoring queries
    __table_args__ = (
        Index('idx_health_metrics_component_name', 'component', 'metric_name'),
        Index('idx_health_metrics_time_series', 'metric_name', 'created_at'),
    )

class DataRetentionPolicies(Base):
    """Data retention policy configurations"""
    __tablename__ = "data_retention_policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(255), nullable=False, unique=True)
    retention_days = Column(Integer, nullable=False)
    archive_before_delete = Column(Boolean, default=True)
    archive_location = Column(String(500))
    last_cleanup = Column(DateTime)
    next_cleanup = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FeatureFlags(Base):
    """Feature flag management"""
    __tablename__ = "feature_flags"
    
    id = Column(String(255), primary_key=True)  # feature flag key
    name = Column(String(500), nullable=False)
    description = Column(Text)
    is_enabled = Column(Boolean, default=False, index=True)
    rollout_percentage = Column(Float, default=0.0)  # 0-100
    user_whitelist = Column(JSON)  # List of user IDs
    user_blacklist = Column(JSON)  # List of user IDs
    environment_whitelist = Column(JSON)  # List of environments
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)

class AuditLogs(Base):
    """Enhanced audit logging"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), index=True)
    action = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(255), index=True)
    resource_id = Column(String(255), index=True)
    old_values = Column(JSON)
    new_values = Column(JSON)
    client_ip = Column(String(45))
    user_agent = Column(Text)
    session_id = Column(String(255))
    api_endpoint = Column(String(500))
    http_method = Column(String(10))
    response_status = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Digital signature for tamper detection
    signature = Column(String(500))
    signature_algorithm = Column(String(50))
    
    # Compliance fields
    compliance_tags = Column(JSON)  # GDPR, SOX, etc.
    retention_date = Column(DateTime, index=True)
    
    # Indexes for audit queries
    __table_args__ = (
        Index('idx_audit_logs_user_action', 'user_id', 'action'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_logs_compliance', 'compliance_tags', postgresql_using='gin'),
    )

class PerformanceBaselines(Base):
    """Performance baseline tracking"""
    __tablename__ = "performance_baselines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(255), nullable=False, index=True)
    baseline_value = Column(Float, nullable=False)
    std_deviation = Column(Float)
    percentile_95 = Column(Float)
    percentile_99 = Column(Float)
    sample_count = Column(Integer)
    time_period = Column(String(50))  # daily, weekly, monthly
    calculated_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, index=True)
    metadata = Column(JSON)

# Migration functions for schema updates
def create_indexes():
    """Create additional indexes for performance"""
    # This would contain SQL commands to create additional indexes
    # if needed beyond what's defined in the table definitions
    pass

def create_partitions():
    """Create table partitions for large tables"""
    # This would contain SQL commands to partition large tables
    # like metrics, webhook_events, product_scans by date
    pass

# Example of a partitioned table (PostgreSQL specific)
class MetricsPartitioned(Base):
    """Partitioned metrics table for better performance"""
    __tablename__ = "metrics_partitioned"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    labels = Column(JSON)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    metric_type = Column(String(50), nullable=False)
    unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # This table would be partitioned by timestamp (monthly partitions)
    __table_args__ = {
        'postgresql_partition_by': 'RANGE (timestamp)',
    }

# Database initialization and migration scripts would be separate files
# that use these table definitions to create/update the schema
