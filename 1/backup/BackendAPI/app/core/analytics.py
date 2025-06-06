"""
Advanced analytics and business intelligence module
"""
import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class TimeRange(Enum):
    """Time range options for analytics"""
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"
    QUARTER = "3m"
    YEAR = "1y"

@dataclass
class AnalyticsQuery:
    """Analytics query configuration"""
    metric_name: str
    time_range: TimeRange
    aggregation: str = "sum"  # sum, avg, max, min, count
    group_by: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None

@dataclass
class MetricDefinition:
    """Metric definition"""
    name: str
    type: MetricType
    description: str
    unit: str
    labels: List[str]
    retention_days: int = 90

@dataclass
class AnalyticsResult:
    """Analytics query result"""
    metric_name: str
    time_range: str
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    generated_at: datetime

class BusinessIntelligenceEngine:
    """Advanced business intelligence and analytics engine"""
    
    def __init__(self, db_session: AsyncSession = None):
        self.db = db_session
        self.metrics_registry = {}
        self.kpi_definitions = {}
        self._register_default_metrics()
    
    async def initialize(self):
        """Initialize the analytics engine"""
        try:
            # Initialize metrics storage
            logger.info("Initializing Business Intelligence Engine...")
            
            # Load any persisted metrics definitions
            if self.db:
                # Could load custom metrics definitions from database
                pass
                
            logger.info("✅ Business Intelligence Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Business Intelligence Engine: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up Business Intelligence Engine...")
            
            # Save any pending metrics
            if self.db:
                # Could save metrics data to database
                pass
                
            # Clear in-memory data
            self.metrics_registry.clear()
            
            logger.info("✅ Business Intelligence Engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during Business Intelligence Engine cleanup: {e}")
    
    def _register_default_metrics(self):
        """Register default business metrics"""
        default_metrics = [
            MetricDefinition(
                name="product_scans_total",
                type=MetricType.COUNTER,
                description="Total number of product scans",
                unit="count",
                labels=["product_id", "user_id", "scan_result"]
            ),
            MetricDefinition(
                name="user_registrations_total",
                type=MetricType.COUNTER,
                description="Total user registrations",
                unit="count",
                labels=["registration_method", "user_type"]
            ),
            MetricDefinition(
                name="api_requests_total",
                type=MetricType.COUNTER,
                description="Total API requests",
                unit="count",
                labels=["endpoint", "method", "status_code"]
            ),
            MetricDefinition(
                name="certificate_generations_total",
                type=MetricType.COUNTER,
                description="Total certificate generations",
                unit="count",
                labels=["certificate_type", "user_id"]
            ),
            MetricDefinition(
                name="revenue_total",
                type=MetricType.COUNTER,
                description="Total revenue",
                unit="currency",
                labels=["product_category", "payment_method"]
            ),
            MetricDefinition(
                name="active_users_gauge",
                type=MetricType.GAUGE,
                description="Number of active users",
                unit="count",
                labels=["time_period"]
            ),
            MetricDefinition(
                name="scan_response_time",
                type=MetricType.HISTOGRAM,
                description="Product scan response time",
                unit="seconds",
                labels=["scan_type"]
            )
        ]
        
        for metric in default_metrics:
            self.metrics_registry[metric.name] = metric
    
    async def record_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None, timestamp: datetime = None):
        """Record a metric value"""
        timestamp = timestamp or datetime.utcnow()
        labels = labels or {}
        
        if metric_name not in self.metrics_registry:
            logger.warning(f"Unknown metric: {metric_name}")
            return
        
        metric_def = self.metrics_registry[metric_name]
        
        # Validate labels
        for required_label in metric_def.labels:
            if required_label not in labels:
                logger.warning(f"Missing required label '{required_label}' for metric {metric_name}")
                return
        
        # Store metric in database
        query = text("""
            INSERT INTO metrics (name, value, labels, timestamp, metric_type, unit)
            VALUES (:name, :value, :labels, :timestamp, :metric_type, :unit)
        """)
        
        await self.db.execute(query, {
            'name': metric_name,
            'value': value,
            'labels': json.dumps(labels),
            'timestamp': timestamp,
            'metric_type': metric_def.type.value,
            'unit': metric_def.unit
        })
        await self.db.commit()
    
    async def query_metrics(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Query metrics with aggregation and filtering"""
        # Build time range filter
        end_time = datetime.utcnow()
        time_delta_map = {
            TimeRange.HOUR: timedelta(hours=1),
            TimeRange.DAY: timedelta(days=1),
            TimeRange.WEEK: timedelta(weeks=1),
            TimeRange.MONTH: timedelta(days=30),
            TimeRange.QUARTER: timedelta(days=90),
            TimeRange.YEAR: timedelta(days=365)
        }
        start_time = end_time - time_delta_map[query.time_range]
        
        # Build SQL query
        base_query = """
            SELECT 
                name,
                {aggregation}(value) as value,
                labels,
                DATE_TRUNC('hour', timestamp) as time_bucket
            FROM metrics 
            WHERE name = :metric_name 
                AND timestamp >= :start_time 
                AND timestamp <= :end_time
        """
        
        group_by_clause = "GROUP BY name, labels, time_bucket"
        if query.group_by:
            # Add custom grouping
            group_fields = []
            for field in query.group_by:
                group_fields.append(f"JSON_EXTRACT(labels, '$.{field}') as {field}")
            
            if group_fields:
                base_query = base_query.replace("labels,", f"labels, {', '.join(group_fields)},")
                group_by_clause += f", {', '.join(field.split(' as ')[1] for field in group_fields)}"
        
        # Add filters
        filter_conditions = []
        if query.filters:
            for key, value in query.filters.items():
                filter_conditions.append(f"JSON_EXTRACT(labels, '$.{key}') = '{value}'")
        
        if filter_conditions:
            base_query += f" AND {' AND '.join(filter_conditions)}"
        
        base_query += f" {group_by_clause} ORDER BY time_bucket"
        
        if query.limit:
            base_query += f" LIMIT {query.limit}"
        
        # Execute query
        sql_query = text(base_query.format(aggregation=query.aggregation))
        result = await self.db.execute(sql_query, {
            'metric_name': query.metric_name,
            'start_time': start_time,
            'end_time': end_time
        })
        
        rows = result.fetchall()
        
        # Process results
        data = []
        values = []
        for row in rows:
            row_dict = {
                'timestamp': row.time_bucket.isoformat(),
                'value': float(row.value),
                'labels': json.loads(row.labels) if row.labels else {}
            }
            if query.group_by:
                for field in query.group_by:
                    if hasattr(row, field):
                        row_dict[field] = getattr(row, field)
            data.append(row_dict)
            values.append(float(row.value))
        
        # Calculate summary statistics
        summary = {}
        if values:
            summary = {
                'total': sum(values),
                'average': np.mean(values),
                'min': min(values),
                'max': max(values),
                'count': len(values),
                'std_dev': float(np.std(values))
            }
        
        return AnalyticsResult(
            metric_name=query.metric_name,
            time_range=query.time_range.value,
            data=data,
            summary=summary,
            generated_at=datetime.utcnow()
        )
    
    async def get_business_kpis(self, time_range: TimeRange) -> Dict[str, Any]:
        """Get key business KPIs"""
        kpis = {}
        
        # Total scans
        scan_query = AnalyticsQuery(
            metric_name="product_scans_total",
            time_range=time_range,
            aggregation="sum"
        )
        scan_result = await self.query_metrics(scan_query)
        kpis['total_scans'] = scan_result.summary.get('total', 0)
        
        # Successful vs failed scans
        success_query = AnalyticsQuery(
            metric_name="product_scans_total",
            time_range=time_range,
            aggregation="sum",
            filters={'scan_result': 'success'}
        )
        success_result = await self.query_metrics(success_query)
        
        failed_query = AnalyticsQuery(
            metric_name="product_scans_total",
            time_range=time_range,
            aggregation="sum",
            filters={'scan_result': 'failed'}
        )
        failed_result = await self.query_metrics(failed_query)
        
        total_scans = success_result.summary.get('total', 0) + failed_result.summary.get('total', 0)
        kpis['scan_success_rate'] = (success_result.summary.get('total', 0) / total_scans * 100) if total_scans > 0 else 0
        
        # New user registrations
        user_query = AnalyticsQuery(
            metric_name="user_registrations_total",
            time_range=time_range,
            aggregation="sum"
        )
        user_result = await self.query_metrics(user_query)
        kpis['new_users'] = user_result.summary.get('total', 0)
        
        # Certificate generations
        cert_query = AnalyticsQuery(
            metric_name="certificate_generations_total",
            time_range=time_range,
            aggregation="sum"
        )
        cert_result = await self.query_metrics(cert_query)
        kpis['certificates_generated'] = cert_result.summary.get('total', 0)
        
        # Revenue
        revenue_query = AnalyticsQuery(
            metric_name="revenue_total",
            time_range=time_range,
            aggregation="sum"
        )
        revenue_result = await self.query_metrics(revenue_query)
        kpis['total_revenue'] = revenue_result.summary.get('total', 0)
        
        # API performance
        api_query = AnalyticsQuery(
            metric_name="api_requests_total",
            time_range=time_range,
            aggregation="sum"
        )
        api_result = await self.query_metrics(api_query)
        kpis['api_requests'] = api_result.summary.get('total', 0)
        
        # Average response time
        response_query = AnalyticsQuery(
            metric_name="scan_response_time",
            time_range=time_range,
            aggregation="avg"
        )
        response_result = await self.query_metrics(response_query)
        kpis['avg_response_time'] = response_result.summary.get('average', 0)
        
        return kpis
    
    async def get_user_behavior_analytics(self, time_range: TimeRange) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        analytics = {}
        
        # Most scanned products
        query = text("""
            SELECT 
                JSON_EXTRACT(labels, '$.product_id') as product_id,
                COUNT(*) as scan_count
            FROM metrics 
            WHERE name = 'product_scans_total'
                AND timestamp >= :start_time
            GROUP BY JSON_EXTRACT(labels, '$.product_id')
            ORDER BY scan_count DESC
            LIMIT 10
        """)
        
        end_time = datetime.utcnow()
        time_delta_map = {
            TimeRange.HOUR: timedelta(hours=1),
            TimeRange.DAY: timedelta(days=1),
            TimeRange.WEEK: timedelta(weeks=1),
            TimeRange.MONTH: timedelta(days=30),
            TimeRange.QUARTER: timedelta(days=90),
            TimeRange.YEAR: timedelta(days=365)
        }
        start_time = end_time - time_delta_map[time_range]
        
        result = await self.db.execute(query, {'start_time': start_time})
        top_products = [{'product_id': row.product_id, 'scan_count': row.scan_count} for row in result.fetchall()]
        analytics['top_scanned_products'] = top_products
        
        # Peak usage hours
        hourly_query = text("""
            SELECT 
                EXTRACT(HOUR FROM timestamp) as hour,
                COUNT(*) as activity_count
            FROM metrics 
            WHERE timestamp >= :start_time
            GROUP BY EXTRACT(HOUR FROM timestamp)
            ORDER BY activity_count DESC
        """)
        
        result = await self.db.execute(hourly_query, {'start_time': start_time})
        peak_hours = [{'hour': int(row.hour), 'activity_count': row.activity_count} for row in result.fetchall()]
        analytics['peak_usage_hours'] = peak_hours
        
        # Geographic distribution (if available)
        geo_query = text("""
            SELECT 
                JSON_EXTRACT(labels, '$.country') as country,
                COUNT(DISTINCT JSON_EXTRACT(labels, '$.user_id')) as unique_users
            FROM metrics 
            WHERE name = 'product_scans_total'
                AND timestamp >= :start_time
                AND JSON_EXTRACT(labels, '$.country') IS NOT NULL
            GROUP BY JSON_EXTRACT(labels, '$.country')
            ORDER BY unique_users DESC
            LIMIT 10
        """)
        
        result = await self.db.execute(geo_query, {'start_time': start_time})
        geo_distribution = [{'country': row.country, 'unique_users': row.unique_users} for row in result.fetchall()]
        analytics['geographic_distribution'] = geo_distribution
        
        return analytics
    
    async def generate_predictive_insights(self, metric_name: str, days_ahead: int = 7) -> Dict[str, Any]:
        """Generate predictive insights using simple trend analysis"""
        # Get historical data for the last 30 days
        query = AnalyticsQuery(
            metric_name=metric_name,
            time_range=TimeRange.MONTH,
            aggregation="sum",
            group_by=None
        )
        
        result = await self.query_metrics(query)
        
        if not result.data:
            return {'prediction': 'No data available for prediction'}
        
        # Extract time series data
        timestamps = []
        values = []
        for point in result.data:
            timestamps.append(datetime.fromisoformat(point['timestamp']))
            values.append(point['value'])
        
        if len(values) < 7:  # Need at least a week of data
            return {'prediction': 'Insufficient data for prediction'}
        
        # Simple linear trend analysis
        df = pd.DataFrame({'timestamp': timestamps, 'value': values})
        df['timestamp_num'] = pd.to_numeric(df['timestamp'])
        
        # Calculate trend
        trend = np.polyfit(df['timestamp_num'], df['value'], 1)[0]
        
        # Project forward
        last_timestamp = timestamps[-1]
        predictions = []
        
        for i in range(1, days_ahead + 1):
            future_timestamp = last_timestamp + timedelta(days=i)
            # Simple linear projection
            predicted_value = values[-1] + (trend * i * 24 * 3600 * 1000000000)  # Convert days to nanoseconds
            predictions.append({
                'timestamp': future_timestamp.isoformat(),
                'predicted_value': max(0, predicted_value),  # Don't predict negative values
                'confidence': 'medium' if i <= 3 else 'low'
            })
        
        return {
            'metric_name': metric_name,
            'trend_direction': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable',
            'trend_strength': abs(trend),
            'predictions': predictions,
            'model_type': 'linear_trend',
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def get_anomaly_detection(self, metric_name: str, sensitivity: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies in metric data using statistical methods"""
        query = AnalyticsQuery(
            metric_name=metric_name,
            time_range=TimeRange.WEEK,
            aggregation="avg"
        )
        
        result = await self.query_metrics(query)
        
        if len(result.data) < 10:  # Need sufficient data points
            return []
        
        values = [point['value'] for point in result.data]
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        anomalies = []
        for point in result.data:
            z_score = abs((point['value'] - mean_val) / std_val) if std_val > 0 else 0
            
            if z_score > sensitivity:
                anomalies.append({
                    'timestamp': point['timestamp'],
                    'value': point['value'],
                    'expected_range': [mean_val - sensitivity * std_val, mean_val + sensitivity * std_val],
                    'z_score': z_score,
                    'severity': 'high' if z_score > 3 else 'medium'
                })
        
        return anomalies
    
    async def export_analytics_report(self, time_range: TimeRange, format: str = "json") -> Dict[str, Any]:
        """Export comprehensive analytics report"""
        report = {
            'report_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'time_range': time_range.value,
                'format': format
            }
        }
        
        # Get KPIs
        report['business_kpis'] = await self.get_business_kpis(time_range)
        
        # Get user behavior analytics
        report['user_behavior'] = await self.get_user_behavior_analytics(time_range)
        
        # Get predictions for key metrics
        key_metrics = ['product_scans_total', 'user_registrations_total', 'revenue_total']
        predictions = {}
        for metric in key_metrics:
            try:
                predictions[metric] = await self.generate_predictive_insights(metric)
            except Exception as e:
                logger.error(f"Failed to generate prediction for {metric}: {e}")
                predictions[metric] = {'error': str(e)}
        
        report['predictions'] = predictions
        
        # Get anomalies for key metrics
        anomalies = {}
        for metric in key_metrics:
            try:
                anomalies[metric] = await self.get_anomaly_detection(metric)
            except Exception as e:
                logger.error(f"Failed to detect anomalies for {metric}: {e}")
                anomalies[metric] = []
        
        report['anomalies'] = anomalies
        
        return report
    
    async def create_custom_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom analytics dashboard"""
        dashboard = {
            'dashboard_id': dashboard_config.get('id', 'custom_dashboard'),
            'title': dashboard_config.get('title', 'Custom Dashboard'),
            'created_at': datetime.utcnow().isoformat(),
            'widgets': []
        }
        
        for widget_config in dashboard_config.get('widgets', []):
            widget_type = widget_config.get('type', 'metric')
            
            if widget_type == 'metric':
                query = AnalyticsQuery(
                    metric_name=widget_config['metric_name'],
                    time_range=TimeRange(widget_config.get('time_range', 'DAY')),
                    aggregation=widget_config.get('aggregation', 'sum'),
                    group_by=widget_config.get('group_by'),
                    filters=widget_config.get('filters')
                )
                
                result = await self.query_metrics(query)
                
                widget = {
                    'id': widget_config.get('id', f"widget_{len(dashboard['widgets'])}"),
                    'title': widget_config.get('title', widget_config['metric_name']),
                    'type': widget_type,
                    'data': result.data,
                    'summary': result.summary
                }
                
                dashboard['widgets'].append(widget)
            
            elif widget_type == 'kpi':
                kpis = await self.get_business_kpis(TimeRange(widget_config.get('time_range', 'DAY')))
                
                widget = {
                    'id': widget_config.get('id', f"kpi_widget_{len(dashboard['widgets'])}"),
                    'title': widget_config.get('title', 'Business KPIs'),
                    'type': widget_type,
                    'data': kpis
                }
                
                dashboard['widgets'].append(widget)
        
        return dashboard

# Utility functions for common analytics operations
async def track_user_action(analytics_engine: BusinessIntelligenceEngine, user_id: str, action: str, context: Dict[str, str] = None):
    """Track a user action for analytics"""
    labels = {'user_id': user_id, 'action': action}
    if context:
        labels.update(context)
    
    await analytics_engine.record_metric('user_actions_total', 1, labels)

async def track_api_call(analytics_engine: BusinessIntelligenceEngine, endpoint: str, method: str, status_code: int, response_time: float):
    """Track API call metrics"""
    labels = {
        'endpoint': endpoint,
        'method': method,
        'status_code': str(status_code)
    }
    
    await analytics_engine.record_metric('api_requests_total', 1, labels)
    await analytics_engine.record_metric('api_response_time', response_time, labels)

async def track_business_event(analytics_engine: BusinessIntelligenceEngine, event_type: str, value: float, metadata: Dict[str, str] = None):
    """Track business events with monetary value"""
    labels = {'event_type': event_type}
    if metadata:
        labels.update(metadata)
    
    await analytics_engine.record_metric('business_events_total', 1, labels)
    if value > 0:
        await analytics_engine.record_metric('revenue_total', value, labels)


# Global analytics engine instance
analytics_engine = BusinessIntelligenceEngine()
