#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced monitoring routes with production alerting and observability
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import asyncio
import json

from ..core.security import api_key_auth, require_permission
from ..core.database import get_db
from ..core.alerting import (
    alert_manager, 
    get_active_alerts, 
    acknowledge_alert, 
    suppress_alert,
    get_alert_statistics,
    evaluate_metrics
)
from ..core.observability import (
    monitoring_dashboard,
    get_system_status,
    get_health_trends,
    get_performance_summary,
    get_metrics_history
)
from .monitoring import metrics, api_monitor

router = APIRouter()


@router.get("/monitoring/status")
async def get_monitoring_status(
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get comprehensive monitoring status"""
    try:
        # Get system status
        system_status = get_system_status()
        
        # Get active alerts
        active_alerts = get_active_alerts()
        
        # Get alert statistics
        alert_stats = get_alert_statistics()
        
        # Get performance summary
        performance = get_performance_summary()
        
        # Get health trends
        health_trends = get_health_trends(hours=1)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": system_status,
            "active_alerts": len(active_alerts),
            "alert_statistics": alert_stats,
            "performance_summary": performance,
            "health_trends": health_trends,
            "monitoring_enabled": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "monitoring_enabled": False
        }


@router.get("/monitoring/alerts")
async def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get alerts with filtering options"""
    if not require_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    alerts = get_active_alerts()
    
    # Apply filters
    if status:
        alerts = [alert for alert in alerts if alert.get("status") == status]
    
    if severity:
        alerts = [alert for alert in alerts if alert.get("severity") == severity]
    
    # Limit results
    alerts = alerts[:limit]
    
    return {
        "alerts": alerts,
        "total": len(alerts),
        "filters_applied": {
            "status": status,
            "severity": severity,
            "limit": limit
        },
        "timestamp": datetime.now().isoformat()
    }


@router.post("/monitoring/alerts/{alert_id}/acknowledge")
async def acknowledge_alert_endpoint(
    alert_id: str,
    acknowledgment_data: Dict[str, Any],
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Acknowledge an alert"""
    if not require_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    acknowledged_by = acknowledgment_data.get("acknowledged_by", "unknown")
    
    if acknowledge_alert(alert_id, acknowledged_by):
        return {
            "message": "Alert acknowledged successfully",
            "alert_id": alert_id,
            "acknowledged_by": acknowledged_by,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/monitoring/alerts/{alert_id}/suppress")
async def suppress_alert_endpoint(
    alert_id: str,
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Suppress an alert"""
    if not require_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    if suppress_alert(alert_id):
        return {
            "message": "Alert suppressed successfully",
            "alert_id": alert_id,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/monitoring/metrics/history")
async def get_metrics_history_endpoint(
    hours: int = 1,
    metric_names: Optional[str] = None,
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get historical metrics data"""
    if not require_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    try:
        history = get_metrics_history(hours)
        
        # Filter by metric names if specified
        if metric_names:
            requested_metrics = [name.strip() for name in metric_names.split(",")]
            # This would need to be implemented in the observability module
            # For now, return all history
        
        return {
            "metrics_history": history,
            "hours": hours,
            "data_points": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics history: {e}")


@router.get("/monitoring/health/detailed")
async def get_detailed_health(
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get detailed health information for all services"""
    try:
        system_status = get_system_status()
        health_trends = get_health_trends(hours=24)
        performance = get_performance_summary()
        
        # Calculate uptime
        uptime_data = {}
        for service, trends in health_trends.items():
            uptime_data[service] = {
                "availability_24h": trends.get("availability_percent", 0),
                "average_response_time": trends.get("average_response_time_ms", 0),
                "total_checks": trends.get("total_checks", 0)
            }
        
        return {
            "detailed_health": {
                "services": system_status.get("service_health", {}),
                "system_metrics": system_status.get("system_metrics", {}),
                "container_metrics": system_status.get("container_metrics", {}),
                "database_metrics": system_status.get("database_metrics", {}),
                "redis_metrics": system_status.get("redis_metrics", {})
            },
            "uptime_statistics": uptime_data,
            "performance_summary": performance,
            "overall_health": system_status.get("overall_health", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving detailed health: {e}")


@router.post("/monitoring/evaluate")
async def trigger_metrics_evaluation(
    background_tasks: BackgroundTasks,
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Manually trigger metrics evaluation against alert rules"""
    if not require_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    try:
        # Get current system metrics
        system_status = get_system_status()
        
        # Prepare metrics for evaluation
        evaluation_metrics = {
            "api_error_rate": 0,  # This should be calculated from actual data
            "api_response_time_ms": 0,  # This should be calculated from actual data
            "database_errors": 0,
            "disk_usage_percent": system_status.get("system_metrics", {}).get("disk_percent", 0),
            "memory_usage_percent": system_status.get("system_metrics", {}).get("memory_percent", 0),
            "cpu_usage_percent": system_status.get("system_metrics", {}).get("cpu_percent", 0)
        }
        
        # Calculate API metrics from monitoring data
        endpoint_stats = api_monitor.get_endpoint_stats()
        if endpoint_stats:
            total_requests = sum(stats["total_requests"] for stats in endpoint_stats.values())
            total_errors = sum(stats["error_count"] for stats in endpoint_stats.values())
            avg_response_times = [stats["average_response_time"] for stats in endpoint_stats.values()]
            
            if total_requests > 0:
                evaluation_metrics["api_error_rate"] = (total_errors / total_requests) * 100
            
            if avg_response_times:
                evaluation_metrics["api_response_time_ms"] = max(avg_response_times) * 1000
        
        # Add to background task for async evaluation
        background_tasks.add_task(evaluate_metrics, evaluation_metrics)
        
        return {
            "message": "Metrics evaluation triggered",
            "evaluated_metrics": evaluation_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering evaluation: {e}")


@router.get("/monitoring/dashboard")
async def get_dashboard_data(
    timeframe: str = "1h",
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get dashboard data for monitoring UI"""
    if not require_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    try:
        # Parse timeframe
        hours_map = {
            "1h": 1,
            "6h": 6,
            "24h": 24,
            "7d": 168
        }
        hours = hours_map.get(timeframe, 1)
        
        # Get comprehensive dashboard data
        system_status = get_system_status()
        health_trends = get_health_trends(hours)
        performance = get_performance_summary()
        metrics_history = get_metrics_history(hours)
        active_alerts = get_active_alerts()
        alert_stats = get_alert_statistics()
        
        # Get top endpoints
        top_endpoints = api_monitor.get_top_endpoints(limit=10, sort_by="requests")
        
        return {
            "timeframe": timeframe,
            "current_status": {
                "overall_health": system_status.get("overall_health", "unknown"),
                "healthy_services": system_status.get("healthy_services", 0),
                "total_services": system_status.get("total_services", 0),
                "active_alerts_count": len(active_alerts)
            },
            "system_metrics": system_status.get("system_metrics", {}),
            "service_health": system_status.get("service_health", {}),
            "container_metrics": system_status.get("container_metrics", {}),
            "database_metrics": system_status.get("database_metrics", {}),
            "redis_metrics": system_status.get("redis_metrics", {}),
            "performance_summary": performance,
            "health_trends": health_trends,
            "metrics_history": metrics_history,
            "active_alerts": active_alerts[:5],  # Show only top 5 alerts
            "alert_statistics": alert_stats,
            "top_endpoints": top_endpoints,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {e}")


@router.get("/monitoring/export")
async def export_monitoring_data(
    format: str = "json",
    hours: int = 24,
    include_history: bool = True,
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Export monitoring data for external analysis"""
    if not require_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    try:
        export_data = {
            "export_info": {
                "generated_at": datetime.now().isoformat(),
                "timeframe_hours": hours,
                "format": format,
                "include_history": include_history
            },
            "current_status": get_system_status(),
            "health_trends": get_health_trends(hours),
            "performance_summary": get_performance_summary(),
            "alert_statistics": get_alert_statistics(),
            "active_alerts": get_active_alerts()
        }
        
        if include_history:
            export_data["metrics_history"] = get_metrics_history(hours)
        
        if format == "json":
            return export_data
        else:
            # For other formats, we could implement CSV, XML, etc.
            raise HTTPException(status_code=400, detail="Only JSON format is currently supported")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {e}")


@router.post("/monitoring/test-alert")
async def test_alert_system(
    test_data: Dict[str, Any],
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Test the alerting system with a mock alert"""
    if not require_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    try:
        # Create test metrics that will trigger an alert
        test_metrics = {
            "api_error_rate": test_data.get("error_rate", 15.0),  # Above threshold
            "api_response_time_ms": test_data.get("response_time", 3000),  # Above threshold
            "memory_usage_percent": test_data.get("memory_usage", 90.0),  # Above threshold
            "disk_usage_percent": test_data.get("disk_usage", 85.0)  # Above threshold
        }
        
        # Evaluate test metrics
        evaluate_metrics(test_metrics)
        
        return {
            "message": "Test alert triggered",
            "test_metrics": test_metrics,
            "timestamp": datetime.now().isoformat(),
            "note": "Check your configured notification channels for test alerts"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing alert system: {e}")


# Background task to periodically evaluate metrics
async def periodic_monitoring_evaluation():
    """Background task for periodic monitoring evaluation"""
    while True:
        try:
            # Get current system status
            system_status = get_system_status()
            
            if system_status and "system_metrics" in system_status:
                # Prepare metrics for evaluation
                evaluation_metrics = {
                    "disk_usage_percent": system_status.get("system_metrics", {}).get("disk_percent", 0),
                    "memory_usage_percent": system_status.get("system_metrics", {}).get("memory_percent", 0),
                    "cpu_usage_percent": system_status.get("system_metrics", {}).get("cpu_percent", 0)
                }
                
                # Add API metrics
                endpoint_stats = api_monitor.get_endpoint_stats()
                if endpoint_stats:
                    total_requests = sum(stats["total_requests"] for stats in endpoint_stats.values())
                    total_errors = sum(stats["error_count"] for stats in endpoint_stats.values())
                    avg_response_times = [stats["average_response_time"] for stats in endpoint_stats.values()]
                    
                    if total_requests > 0:
                        evaluation_metrics["api_error_rate"] = (total_errors / total_requests) * 100
                    
                    if avg_response_times:
                        evaluation_metrics["api_response_time_ms"] = max(avg_response_times) * 1000
                
                # Evaluate metrics against alert rules
                evaluate_metrics(evaluation_metrics)
            
            # Wait 60 seconds before next evaluation
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in periodic monitoring evaluation: {e}")
            await asyncio.sleep(60)


# Start background monitoring task when module is imported
import logging
logger = logging.getLogger(__name__)

# Note: The background task would typically be started in the main application startup
# asyncio.create_task(periodic_monitoring_evaluation())
