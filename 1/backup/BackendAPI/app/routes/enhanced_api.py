"""
Enhanced API routes integrating advanced features
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime, timedelta
import logging

from ..core.database import get_db
from ..core.caching import AdvancedCacheManager, cache_result, invalidate_cache
from ..core.analytics import BusinessIntelligenceEngine, TimeRange, AnalyticsQuery, track_api_call, track_user_action
from ..routes.webhooks_simple import emit_product_scan_event, emit_security_alert, SimpleWebhookManager
from ..core.webhooks import WebhookManager
from ..core.versioning import ApiVersionManager, VersionStrategy
from ..core.security import SecurityManager
from ..core.observability import SystemMonitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["Enhanced API"])
security = HTTPBearer()

# Global managers (would be initialized in main.py)
cache_manager: Optional[AdvancedCacheManager] = None
analytics_engine: Optional[BusinessIntelligenceEngine] = None
webhook_manager: Optional[SimpleWebhookManager] = None
version_manager: Optional[ApiVersionManager] = None
security_manager: Optional[SecurityManager] = None
system_monitor: Optional[SystemMonitor] = None

async def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Extract user information from JWT token"""
    # This would integrate with your actual authentication system
    return {
        "id": "user123",
        "email": "user@example.com",
        "role": "premium"
    }

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    time_range: str = "1w",
    include_predictions: bool = False,
    db: AsyncSession = Depends(get_db),
    user: Dict = Depends(get_user_from_token)
):
    """Get comprehensive analytics dashboard"""
    try:
        # Track API call
        if analytics_engine:
            await track_api_call(analytics_engine, "/analytics/dashboard", "GET", 200, 0.5)
        
        # Check cache first
        cache_key = f"analytics_dashboard:{time_range}:{include_predictions}:{user['id']}"
        if cache_manager:
            cached_result = await cache_manager.get(cache_key, namespace="analytics")
            if cached_result:
                return cached_result
        
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics service unavailable")
        
        # Get business KPIs
        time_range_enum = TimeRange(time_range)
        kpis = await analytics_engine.get_business_kpis(time_range_enum)
        
        # Get user behavior analytics
        user_behavior = await analytics_engine.get_user_behavior_analytics(time_range_enum)
        
        # Get predictions if requested
        predictions = {}
        if include_predictions:
            key_metrics = ['product_scans_total', 'user_registrations_total']
            for metric in key_metrics:
                try:
                    predictions[metric] = await analytics_engine.generate_predictive_insights(metric)
                except Exception as e:
                    logger.error(f"Failed to generate prediction for {metric}: {e}")
                    predictions[metric] = {'error': str(e)}
        
        # Get anomalies
        anomalies = {}
        for metric in ['product_scans_total', 'api_requests_total']:
            try:
                anomalies[metric] = await analytics_engine.get_anomaly_detection(metric)
            except Exception as e:
                logger.error(f"Failed to detect anomalies for {metric}: {e}")
                anomalies[metric] = []
        
        result = {
            'dashboard_data': {
                'kpis': kpis,
                'user_behavior': user_behavior,
                'anomalies': anomalies,
                'time_range': time_range,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
        
        if include_predictions:
            result['dashboard_data']['predictions'] = predictions
        
        # Cache result for 5 minutes
        if cache_manager:
            await cache_manager.set(cache_key, result, ttl=300, namespace="analytics")
        
        return result
        
    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        if analytics_engine:
            await track_api_call(analytics_engine, "/analytics/dashboard", "GET", 500, 0.5)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/custom-query")
async def execute_custom_analytics_query(
    query_config: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    user: Dict = Depends(get_user_from_token)
):
    """Execute a custom analytics query"""
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics service unavailable")
        
        # Track user action
        if analytics_engine:
            await track_user_action(analytics_engine, user['id'], "custom_analytics_query", 
                                   {'query_type': query_config.get('metric_name', 'unknown')})
        
        # Validate query configuration
        required_fields = ['metric_name', 'time_range']
        for field in required_fields:
            if field not in query_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create analytics query
        query = AnalyticsQuery(
            metric_name=query_config['metric_name'],
            time_range=TimeRange(query_config['time_range']),
            aggregation=query_config.get('aggregation', 'sum'),
            group_by=query_config.get('group_by'),
            filters=query_config.get('filters'),
            limit=query_config.get('limit')
        )
        
        # Execute query
        result = await analytics_engine.query_metrics(query)
        
        return {
            'query_result': {
                'metric_name': result.metric_name,
                'time_range': result.time_range,
                'data': result.data,
                'summary': result.summary,
                'generated_at': result.generated_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Custom analytics query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/stats")
async def get_cache_stats(
    user: Dict = Depends(get_user_from_token)
):
    """Get cache performance statistics"""
    try:
        if not cache_manager:
            raise HTTPException(status_code=503, detail="Cache service unavailable")
        
        stats = await cache_manager.get_stats()
        
        return {
            'cache_stats': stats,
            'retrieved_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache/invalidate")
async def invalidate_cache_pattern(
    pattern: str,
    namespace: Optional[str] = None,
    user: Dict = Depends(get_user_from_token)
):
    """Invalidate cache entries matching pattern"""
    try:
        if not cache_manager:
            raise HTTPException(status_code=503, detail="Cache service unavailable")
        
        # Check user permissions (admin only)
        if user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        invalidated_count = await cache_manager.invalidate_pattern(pattern, namespace)
        
        # Track admin action
        if analytics_engine:
            await track_user_action(analytics_engine, user['id'], "cache_invalidation", 
                                   {'pattern': pattern, 'namespace': namespace, 'count': invalidated_count})
        
        return {
            'invalidated_count': invalidated_count,
            'pattern': pattern,
            'namespace': namespace,
            'invalidated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks/endpoints")
async def list_webhook_endpoints(
    user: Dict = Depends(get_user_from_token)
):
    """List all webhook endpoints"""
    try:
        if not webhook_manager:
            raise HTTPException(status_code=503, detail="Webhook service unavailable")
        
        # Return sanitized endpoint information (no secrets)
        endpoints = []
        for endpoint_id, endpoint in webhook_manager.endpoints.items():
            endpoints.append({
                'id': endpoint.id,
                'url': endpoint.url,
                'events': [event.value for event in endpoint.events],
                'active': endpoint.active,
                'timeout': endpoint.timeout,
                'max_retries': endpoint.max_retries,
                'created_at': endpoint.created_at.isoformat() if endpoint.created_at else None
            })
        
        return {
            'endpoints': endpoints,
            'total_count': len(endpoints)
        }
        
    except Exception as e:
        logger.error(f"List webhook endpoints error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhooks/endpoints/{endpoint_id}/stats")
async def get_webhook_endpoint_stats(
    endpoint_id: str,
    days: int = 7,
    user: Dict = Depends(get_user_from_token)
):
    """Get delivery statistics for a webhook endpoint"""
    try:
        if not webhook_manager:
            raise HTTPException(status_code=503, detail="Webhook service unavailable")
        
        stats = await webhook_manager.get_endpoint_stats(endpoint_id, days)
        
        return {
            'endpoint_id': endpoint_id,
            'stats': stats,
            'period_days': days,
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Webhook stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/events/{event_id}/retry")
async def retry_webhook_event(
    event_id: str,
    user: Dict = Depends(get_user_from_token)
):
    """Retry a failed webhook event"""
    try:
        if not webhook_manager:
            raise HTTPException(status_code=503, detail="Webhook service unavailable")
        
        # Check user permissions
        if user.get('role') not in ['admin', 'developer']:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get event status first
        event_status = await webhook_manager.get_event_status(event_id)
        if not event_status:
            raise HTTPException(status_code=404, detail="Webhook event not found")
        
        if event_status['status'] != 'failed':
            raise HTTPException(status_code=400, detail="Only failed events can be retried")
        
        # Retry the event
        retry_count = await webhook_manager.retry_failed_events(
            endpoint_id=event_status['endpoint_id']
        )
        
        # Track admin action
        if analytics_engine:
            await track_user_action(analytics_engine, user['id'], "webhook_retry", 
                                   {'event_id': event_id})
        
        return {
            'event_id': event_id,
            'retry_initiated': True,
            'retry_count': retry_count,
            'retried_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Webhook retry error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/versions")
async def get_api_versions():
    """Get information about all API versions"""
    try:
        if not version_manager:
            raise HTTPException(status_code=503, detail="Version management unavailable")
        
        versions = version_manager.list_all_versions()
        current_versions = version_manager.get_current_versions()
        
        return {
            'versions': versions,
            'current_versions': current_versions,
            'default_version': version_manager.default_version,
            'versioning_strategy': version_manager.strategy.value
        }
        
    except Exception as e:
        logger.error(f"API versions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/health/comprehensive")
async def get_comprehensive_health_check(
    include_metrics: bool = True,
    include_dependencies: bool = True
):
    """Get comprehensive system health information"""
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.1.0',
            'uptime': '24h 15m 32s'  # This would be calculated from actual uptime
        }
        
        # System metrics
        if include_metrics and system_monitor:
            try:
                system_metrics = await system_monitor.get_system_metrics()
                health_data['system_metrics'] = system_metrics
            except Exception as e:
                logger.error(f"Failed to get system metrics: {e}")
                health_data['system_metrics'] = {'error': str(e)}
        
        # Service dependencies
        if include_dependencies:
            dependencies = {}
            
            # Check cache
            if cache_manager:
                try:
                    cache_stats = await cache_manager.get_stats()
                    dependencies['cache'] = {
                        'status': 'healthy',
                        'hit_rate': cache_stats.get('hit_rate', 0),
                        'memory_usage': cache_stats.get('memory_usage', 0)
                    }
                except Exception as e:
                    dependencies['cache'] = {'status': 'unhealthy', 'error': str(e)}
            
            # Check analytics
            if analytics_engine:
                dependencies['analytics'] = {'status': 'healthy'}
            else:
                dependencies['analytics'] = {'status': 'unavailable'}
            
            # Check webhooks
            if webhook_manager:
                dependencies['webhooks'] = {
                    'status': 'healthy',
                    'active_endpoints': len(webhook_manager.endpoints)
                }
            else:
                dependencies['webhooks'] = {'status': 'unavailable'}
            
            health_data['dependencies'] = dependencies
        
        # Determine overall health status
        if include_dependencies:
            unhealthy_deps = [
                name for name, dep in health_data.get('dependencies', {}).items()
                if dep.get('status') == 'unhealthy'
            ]
            if unhealthy_deps:
                health_data['status'] = 'degraded'
                health_data['unhealthy_dependencies'] = unhealthy_deps
        
        return health_data
        
    except Exception as e:
        logger.error(f"Comprehensive health check error: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

@router.post("/products/{product_id}/scan")
async def scan_product_enhanced(
    product_id: str,
    scan_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: Dict = Depends(get_user_from_token)
):
    """Enhanced product scanning with caching, analytics, and webhooks"""
    try:
        # Extract client information
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', 'unknown')
        
        # Check cache for recent scan results
        cache_key = f"product_scan:{product_id}:{user['id']}"
        scan_result = None
        
        if cache_manager:
            cached_result = await cache_manager.get(cache_key, namespace="scans")
            if cached_result:
                scan_result = cached_result
                # Track cache hit
                if analytics_engine:
                    await track_user_action(analytics_engine, user['id'], "product_scan_cached", 
                                           {'product_id': product_id})
        
        # Perform actual scan if not cached
        if not scan_result:
            # Simulate product scanning logic
            scan_result = {
                'product_id': product_id,
                'scan_status': 'success',
                'authenticity_score': 0.95,
                'scan_timestamp': datetime.utcnow().isoformat(),
                'scan_engine_version': '2.1.0',
                'metadata': {
                    'scan_duration_ms': 150,
                    'client_ip': client_ip,
                    'user_agent': user_agent
                }
            }
            
            # Cache the result for 10 minutes
            if cache_manager:
                await cache_manager.set(cache_key, scan_result, ttl=600, namespace="scans")
        
        # Track analytics
        if analytics_engine:
            await track_user_action(analytics_engine, user['id'], "product_scan", {
                'product_id': product_id,
                'scan_result': scan_result['scan_status'],
                'authenticity_score': str(scan_result['authenticity_score'])
            })
            
            # Record metric
            await analytics_engine.record_metric(
                'product_scans_total', 
                1, 
                {
                    'product_id': product_id,
                    'user_id': user['id'],
                    'scan_result': scan_result['scan_status']
                }
            )
        
        # Emit webhook event
        if webhook_manager:
            background_tasks.add_task(
                emit_product_scan_event,
                webhook_manager,
                product_id,
                user['id'],
                scan_result['scan_status'],
                {
                    'authenticity_score': scan_result['authenticity_score'],
                    'client_ip': client_ip
                }
            )
        
        # Security monitoring for suspicious activity
        if scan_result['authenticity_score'] < 0.5 and security_manager:
            background_tasks.add_task(
                emit_security_alert,
                webhook_manager,
                "low_authenticity_scan",
                "medium",
                {
                    'product_id': product_id,
                    'user_id': user['id'],
                    'authenticity_score': scan_result['authenticity_score'],
                    'client_ip': client_ip
                }
            )
        
        return {
            'scan_result': scan_result,
            'cached': 'cached_result' in locals(),
            'scanned_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Enhanced product scan error: {e}")
        if analytics_engine:
            await track_api_call(analytics_engine, f"/products/{product_id}/scan", "POST", 500, 0.0)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/export")
async def export_analytics_report(
    background_tasks: BackgroundTasks,
    time_range: str = "1w",
    format: str = "json",
    user: Dict = Depends(get_user_from_token)
):
    """Export comprehensive analytics report"""
    try:
        if not analytics_engine:
            raise HTTPException(status_code=503, detail="Analytics service unavailable")
        
        # Check user permissions
        if user.get('role') not in ['admin', 'analyst']:
            raise HTTPException(status_code=403, detail="Insufficient permissions for analytics export")
        
        # Generate report
        time_range_enum = TimeRange(time_range)
        report = await analytics_engine.export_analytics_report(time_range_enum, format)
        
        # Track admin action
        await track_user_action(analytics_engine, user['id'], "analytics_export", {
            'time_range': time_range,
            'format': format
        })
        
        return {
            'report': report,
            'export_metadata': {
                'exported_by': user['id'],
                'exported_at': datetime.utcnow().isoformat(),
                'time_range': time_range,
                'format': format
            }
        }
        
    except Exception as e:
        logger.error(f"Analytics export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize managers (this would be called from main.py)
async def initialize_enhanced_services(
    redis_client,
    db_session: AsyncSession
):
    """Initialize all enhanced services"""
    global cache_manager, analytics_engine, webhook_manager, version_manager, security_manager, system_monitor
    
    try:
        # Initialize cache manager
        from ..core.caching import CacheConfig
        cache_config = CacheConfig(
            default_ttl=3600,
            max_size=10000,
            namespace="neuroscan_v2"
        )
        cache_manager = AdvancedCacheManager(redis_client, cache_config)
        
        # Initialize analytics engine
        analytics_engine = BusinessIntelligenceEngine(db_session)
        
        # Initialize webhook manager
        from ..core.webhooks import WebhookEventProcessor
        event_processor = WebhookEventProcessor()
        webhook_manager = WebhookManager(db_session, event_processor)
        await webhook_manager.load_endpoints()
        await webhook_manager.start_delivery_workers(num_workers=3)
        
        # Initialize version manager
        from ..core.versioning import setup_api_versioning
        version_manager = setup_api_versioning()
        
        # Initialize system monitor
        system_monitor = SystemMonitor()
        
        logger.info("Enhanced services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize enhanced services: {e}")
        raise
