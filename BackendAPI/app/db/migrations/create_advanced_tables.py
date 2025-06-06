#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration: Create Advanced Feature Tables
Migration for advanced caching, analytics, webhooks, and versioning features
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Text, Boolean, JSON, Float, BigInteger, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.config import settings

def upgrade():
    """Create advanced feature tables"""
    engine = create_engine(settings.DATABASE_URL)
    metadata = MetaData()
    
    # Create metrics table
    metrics = Table(
        'metrics',
        metadata,
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('name', String(255), nullable=False, index=True),
        Column('value', Float, nullable=False),
        Column('labels', JSON, nullable=True),
        Column('metric_type', String(50), nullable=False),  # counter, gauge, histogram, summary
        Column('created_at', DateTime, default=datetime.utcnow, index=True),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    
    # Create webhook_endpoints table
    webhook_endpoints = Table(
        'webhook_endpoints',
        metadata,
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('url', String(512), nullable=False),
        Column('secret', String(255), nullable=True),
        Column('events', JSON, nullable=False),  # List of subscribed events
        Column('active', Boolean, default=True),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        Column('last_delivery', DateTime, nullable=True),
        Column('delivery_count', Integer, default=0),
        Column('failure_count', Integer, default=0),
    )
    
    # Create webhook_deliveries table
    webhook_deliveries = Table(
        'webhook_deliveries',
        metadata,
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('endpoint_id', UUID(as_uuid=True), nullable=False),
        Column('event_type', String(100), nullable=False),
        Column('payload', JSON, nullable=False),
        Column('status', String(50), nullable=False),  # pending, delivered, failed, retrying
        Column('response_status', Integer, nullable=True),
        Column('response_body', Text, nullable=True),
        Column('attempt_count', Integer, default=0),
        Column('max_attempts', Integer, default=3),
        Column('next_attempt', DateTime, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow, index=True),
        Column('delivered_at', DateTime, nullable=True),
    )
    
    # Create cache_entries table
    cache_entries = Table(
        'cache_entries',
        metadata,
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('cache_key', String(512), nullable=False, unique=True, index=True),
        Column('value', Text, nullable=False),
        Column('compressed', Boolean, default=False),
        Column('size_bytes', Integer, nullable=False),
        Column('hit_count', Integer, default=0),
        Column('ttl_seconds', Integer, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('accessed_at', DateTime, default=datetime.utcnow),
        Column('expires_at', DateTime, nullable=True, index=True),
    )
    
    # Create api_versions table
    api_versions = Table(
        'api_versions',
        metadata,
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('version', String(50), nullable=False, unique=True),
        Column('status', String(50), nullable=False),  # active, deprecated, sunset
        Column('release_date', DateTime, nullable=False),
        Column('deprecation_date', DateTime, nullable=True),
        Column('sunset_date', DateTime, nullable=True),
        Column('migration_guide', Text, nullable=True),
        Column('breaking_changes', JSON, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow),
    )
    
    # Create enhanced_sessions table
    enhanced_sessions = Table(
        'enhanced_sessions',
        metadata,
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('session_id', String(255), nullable=False, unique=True, index=True),
        Column('user_id', UUID(as_uuid=True), nullable=True),
        Column('ip_address', String(45), nullable=False),
        Column('user_agent', Text, nullable=True),
        Column('metadata', JSON, nullable=True),
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('last_activity', DateTime, default=datetime.utcnow, index=True),
        Column('expires_at', DateTime, nullable=False, index=True),
        Column('active', Boolean, default=True),
    )
    
    # Create security_events table
    security_events = Table(
        'security_events',
        metadata,
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('event_type', String(100), nullable=False, index=True),
        Column('severity', String(20), nullable=False),  # low, medium, high, critical
        Column('source_ip', String(45), nullable=False),
        Column('user_id', UUID(as_uuid=True), nullable=True),
        Column('description', Text, nullable=False),
        Column('metadata', JSON, nullable=True),
        Column('resolved', Boolean, default=False),
        Column('created_at', DateTime, default=datetime.utcnow, index=True),
        Column('resolved_at', DateTime, nullable=True),
    )
    
    # Create performance_baselines table
    performance_baselines = Table(
        'performance_baselines',
        metadata,
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('metric_name', String(255), nullable=False),
        Column('baseline_value', Float, nullable=False),
        Column('threshold_warning', Float, nullable=False),
        Column('threshold_critical', Float, nullable=False),
        Column('measurement_window', Integer, nullable=False),  # seconds
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    
    # Create system_health table
    system_health = Table(
        'system_health',
        metadata,
        Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column('component', String(100), nullable=False, index=True),
        Column('status', String(20), nullable=False),  # healthy, warning, critical
        Column('metrics', JSON, nullable=False),
        Column('last_check', DateTime, default=datetime.utcnow, index=True),
        Column('created_at', DateTime, default=datetime.utcnow),
    )
    
    # Create indexes for better performance
    indexes = [
        Index('idx_metrics_name_created', metrics.c.name, metrics.c.created_at),
        Index('idx_webhook_deliveries_status', webhook_deliveries.c.status),
        Index('idx_webhook_deliveries_next_attempt', webhook_deliveries.c.next_attempt),
        Index('idx_cache_entries_expires', cache_entries.c.expires_at),
        Index('idx_enhanced_sessions_user_activity', enhanced_sessions.c.user_id, enhanced_sessions.c.last_activity),
        Index('idx_security_events_type_created', security_events.c.event_type, security_events.c.created_at),
        Index('idx_system_health_component_check', system_health.c.component, system_health.c.last_check),
    ]
    
    # Create all tables and indexes
    metadata.create_all(engine)
    
    print("✅ Advanced feature tables created successfully")
    print("📊 Created tables: metrics, webhook_endpoints, webhook_deliveries, cache_entries")
    print("🔀 Created tables: api_versions, enhanced_sessions, security_events")
    print("📈 Created tables: performance_baselines, system_health")
    print("🔍 Created performance indexes")

def downgrade():
    """Drop advanced feature tables"""
    engine = create_engine(settings.DATABASE_URL)
    metadata = MetaData()
    
    # Define tables to drop
    table_names = [
        'system_health',
        'performance_baselines', 
        'security_events',
        'enhanced_sessions',
        'api_versions',
        'cache_entries',
        'webhook_deliveries',
        'webhook_endpoints',
        'metrics'
    ]
    
    # Drop tables in reverse order
    for table_name in table_names:
        try:
            engine.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            print(f"🗑️ Dropped table: {table_name}")
        except Exception as e:
            print(f"⚠️ Error dropping table {table_name}: {e}")
    
    print("✅ Advanced feature tables dropped successfully")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
