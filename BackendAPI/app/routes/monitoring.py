#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API monitoring, metrics, and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time
import asyncio
from dataclasses import dataclass
from enum import Enum
import json

from ..core.security import api_key_auth, require_permission, api_key_manager
from ..core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricEntry:
    """Single metric entry"""
    timestamp: float
    value: float
    labels: Dict[str, str] = None


class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_entries))
        self.metric_types: Dict[str, MetricType] = {}
        self.metric_descriptions: Dict[str, str] = {}
        
        # Initialize default metrics
        self._init_default_metrics()
    
    def _init_default_metrics(self):
        """Initialize default system metrics"""
        self.register_metric("api_requests_total", MetricType.COUNTER, "Total API requests")
        self.register_metric("api_request_duration", MetricType.HISTOGRAM, "API request duration in seconds")
        self.register_metric("api_errors_total", MetricType.COUNTER, "Total API errors")
        self.register_metric("active_connections", MetricType.GAUGE, "Active WebSocket connections")
        self.register_metric("certificate_scans_total", MetricType.COUNTER, "Total certificate scans")
        self.register_metric("pdf_generations_total", MetricType.COUNTER, "Total PDF generations")
        self.register_metric("database_queries_total", MetricType.COUNTER, "Total database queries")
        self.register_metric("rate_limit_hits", MetricType.COUNTER, "Rate limit violations")
    
    def register_metric(self, name: str, metric_type: MetricType, description: str):
        """Register a new metric"""
        self.metric_types[name] = metric_type
        self.metric_descriptions[name] = description
    
    def record(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric value"""
        entry = MetricEntry(
            timestamp=time.time(),
            value=value,
            labels=labels or {}
        )
        self.metrics[metric_name].append(entry)
    
    def increment(self, metric_name: str, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        self.record(metric_name, 1.0, labels)
    
    def set_gauge(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        self.record(metric_name, value, labels)
    
    def get_metric_values(self, metric_name: str, since: float = None) -> List[MetricEntry]:
        """Get metric values since timestamp"""
        if metric_name not in self.metrics:
            return []
        
        entries = list(self.metrics[metric_name])
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        
        return entries
    
    def get_metric_summary(self, metric_name: str, duration_seconds: int = 3600) -> Dict:
        """Get metric summary for the specified duration"""
        since = time.time() - duration_seconds
        entries = self.get_metric_values(metric_name, since)
        
        if not entries:
            return {
                "metric": metric_name,
                "type": self.metric_types.get(metric_name, MetricType.COUNTER).value,
                "description": self.metric_descriptions.get(metric_name, ""),
                "count": 0,
                "duration_seconds": duration_seconds
            }
        
        values = [e.value for e in entries]
        metric_type = self.metric_types.get(metric_name, MetricType.COUNTER)
        
        summary = {
            "metric": metric_name,
            "type": metric_type.value,
            "description": self.metric_descriptions.get(metric_name, ""),
            "count": len(entries),
            "duration_seconds": duration_seconds,
            "first_timestamp": entries[0].timestamp,
            "last_timestamp": entries[-1].timestamp
        }
        
        if metric_type == MetricType.COUNTER:
            summary.update({
                "total": sum(values),
                "rate_per_second": sum(values) / duration_seconds if duration_seconds > 0 else 0
            })
        elif metric_type == MetricType.GAUGE:
            summary.update({
                "current": values[-1] if values else 0,
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values)
            })
        elif metric_type in [MetricType.HISTOGRAM, MetricType.TIMER]:
            sorted_values = sorted(values)
            count = len(sorted_values)
            summary.update({
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "p50": sorted_values[int(count * 0.5)] if count > 0 else 0,
                "p90": sorted_values[int(count * 0.9)] if count > 0 else 0,
                "p95": sorted_values[int(count * 0.95)] if count > 0 else 0,
                "p99": sorted_values[int(count * 0.99)] if count > 0 else 0
            })
        
        return summary
    
    def get_all_metrics_summary(self, duration_seconds: int = 3600) -> Dict:
        """Get summary of all metrics"""
        return {
            metric_name: self.get_metric_summary(metric_name, duration_seconds)
            for metric_name in self.metric_types.keys()
        }


# Global metrics collector
metrics = MetricsCollector()


class APIMonitor:
    """API monitoring and analytics"""
    
    def __init__(self):
        self.request_times: defaultdict = defaultdict(list)
        self.error_counts: defaultdict = defaultdict(int)
        self.endpoint_stats: defaultdict = defaultdict(lambda: {
            "count": 0,
            "total_time": 0,
            "errors": 0,
            "last_accessed": None
        })
    
    def record_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """Record API request metrics"""
        key = f"{method} {endpoint}"
        
        # Update endpoint stats
        self.endpoint_stats[key]["count"] += 1
        self.endpoint_stats[key]["total_time"] += duration
        self.endpoint_stats[key]["last_accessed"] = datetime.now().isoformat()
        
        if status_code >= 400:
            self.endpoint_stats[key]["errors"] += 1
            metrics.increment("api_errors_total", {"endpoint": endpoint, "method": method, "status": str(status_code)})
        
        # Record metrics
        metrics.increment("api_requests_total", {"endpoint": endpoint, "method": method, "status": str(status_code)})
        metrics.record("api_request_duration", duration, {"endpoint": endpoint, "method": method})
    
    def get_endpoint_stats(self, since_hours: int = 24) -> Dict:
        """Get endpoint statistics"""
        stats = {}
        for endpoint, data in self.endpoint_stats.items():
            avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
            error_rate = data["errors"] / data["count"] if data["count"] > 0 else 0
            
            stats[endpoint] = {
                "total_requests": data["count"],
                "average_response_time": round(avg_time, 3),
                "error_count": data["errors"],
                "error_rate": round(error_rate * 100, 2),  # percentage
                "last_accessed": data["last_accessed"]
            }
        
        return stats
    
    def get_top_endpoints(self, limit: int = 10, sort_by: str = "requests") -> List:
        """Get top endpoints by requests or errors"""
        sorted_endpoints = []
        
        if sort_by == "requests":
            sorted_endpoints = sorted(
                self.endpoint_stats.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )
        elif sort_by == "errors":
            sorted_endpoints = sorted(
                self.endpoint_stats.items(),
                key=lambda x: x[1]["errors"],
                reverse=True
            )
        elif sort_by == "response_time":
            sorted_endpoints = sorted(
                self.endpoint_stats.items(),
                key=lambda x: x[1]["total_time"] / x[1]["count"] if x[1]["count"] > 0 else 0,
                reverse=True
            )
        
        return [
            {
                "endpoint": endpoint,
                "requests": data["count"],
                "errors": data["errors"],
                "avg_response_time": round(data["total_time"] / data["count"] if data["count"] > 0 else 0, 3),
                "error_rate": round(data["errors"] / data["count"] * 100 if data["count"] > 0 else 0, 2)
            }
            for endpoint, data in sorted_endpoints[:limit]
        ]


# Global API monitor
api_monitor = APIMonitor()


@router.get("/metrics")
async def get_metrics(
    duration_hours: int = 1,
    metric_names: Optional[str] = None,
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get application metrics (requires API key)"""
    duration_seconds = duration_hours * 3600
    
    if metric_names:
        # Get specific metrics
        requested_metrics = [name.strip() for name in metric_names.split(",")]
        result = {}
        for metric_name in requested_metrics:
            if metric_name in metrics.metric_types:
                result[metric_name] = metrics.get_metric_summary(metric_name, duration_seconds)
        return result
    else:
        # Get all metrics
        return metrics.get_all_metrics_summary(duration_seconds)


@router.get("/metrics/prometheus")
async def get_prometheus_metrics(
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get metrics in Prometheus format"""
    lines = []
    duration_seconds = 3600  # Last hour
    
    for metric_name, metric_type in metrics.metric_types.items():
        summary = metrics.get_metric_summary(metric_name, duration_seconds)
        description = metrics.metric_descriptions.get(metric_name, "")
        
        # Add help line
        lines.append(f"# HELP {metric_name} {description}")
        lines.append(f"# TYPE {metric_name} {metric_type.value}")
        
        if metric_type == MetricType.COUNTER:
            lines.append(f"{metric_name}_total {summary.get('total', 0)}")
        elif metric_type == MetricType.GAUGE:
            lines.append(f"{metric_name} {summary.get('current', 0)}")
        elif metric_type in [MetricType.HISTOGRAM, MetricType.TIMER]:
            lines.append(f"{metric_name}_count {summary.get('count', 0)}")
            lines.append(f"{metric_name}_sum {summary.get('total', 0)}")
            for percentile in [50, 90, 95, 99]:
                value = summary.get(f'p{percentile}', 0)
                lines.append(f"{metric_name}{{quantile=\"0.{percentile:02d}\"}} {value}")
        
        lines.append("")  # Empty line between metrics
    
    return "\n".join(lines)


@router.get("/monitoring/endpoints")
async def get_endpoint_monitoring(
    limit: int = 20,
    sort_by: str = "requests",
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get endpoint monitoring data"""
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    return {
        "top_endpoints": api_monitor.get_top_endpoints(limit, sort_by),
        "endpoint_stats": api_monitor.get_endpoint_stats(),
        "generated_at": datetime.now().isoformat()
    }


@router.get("/monitoring/health")
async def get_health_metrics(
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get health monitoring data"""
    # Basic health metrics
    recent_errors = metrics.get_metric_summary("api_errors_total", 300)  # Last 5 minutes
    recent_requests = metrics.get_metric_summary("api_requests_total", 300)
    
    error_rate = 0
    if recent_requests.get("total", 0) > 0:
        error_rate = recent_errors.get("total", 0) / recent_requests.get("total", 0) * 100
    
    health_status = "healthy"
    if error_rate > 10:  # More than 10% error rate
        health_status = "degraded"
    elif error_rate > 25:  # More than 25% error rate
        health_status = "unhealthy"
    
    return {
        "status": health_status,
        "error_rate_percent": round(error_rate, 2),
        "recent_requests": recent_requests.get("total", 0),
        "recent_errors": recent_errors.get("total", 0),
        "uptime_seconds": time.time() - (recent_requests.get("first_timestamp", time.time())),
        "timestamp": datetime.now().isoformat()
    }


@router.post("/monitoring/alerts")
async def create_alert_rule(
    alert_data: dict,
    request: Request = None,
    api_key_info: dict = Depends(api_key_auth)
):
    """Create monitoring alert rule (admin only)"""
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    # This would typically integrate with an alerting system
    # For now, return a placeholder response
    return {
        "message": "Alert rule created",
        "alert_id": f"alert_{int(time.time())}",
        "rule": alert_data
    }


# Middleware function to track requests (to be added to main.py)
async def track_request_metrics(request: Request, call_next):
    """Middleware to track request metrics"""
    start_time = time.time()
    
    # Get endpoint info
    method = request.method
    path = request.url.path
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Record metrics
    api_monitor.record_request(path, method, duration, response.status_code)
    
    return response
