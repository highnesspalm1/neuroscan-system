#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced alerting and notification system for production monitoring
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import time
import asyncio
import logging
import smtplib
import aiohttp
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict, deque
import os
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class AlertRule:
    """Definition of an alert rule"""
    name: str
    description: str
    condition: str
    threshold: float
    severity: AlertSeverity
    metric_name: str
    duration_minutes: int = 5
    cooldown_minutes: int = 15
    enabled: bool = True
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    details: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary"""
        return {
            "id": self.id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "labels": self.labels,
            "annotations": self.annotations
        }


class NotificationChannel:
    """Base class for notification channels"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", True)
    
    async def send(self, alert: Alert) -> bool:
        """Send notification for alert"""
        raise NotImplementedError
    
    def test_connection(self) -> bool:
        """Test notification channel connection"""
        return True


class EmailNotification(NotificationChannel):
    """Email notification channel"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.smtp_server = config.get("smtp_server", "localhost")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.from_email = config.get("from_email")
        self.to_emails = config.get("to_emails", [])
        self.use_tls = config.get("use_tls", True)
    
    async def send(self, alert: Alert) -> bool:
        """Send email notification"""
        try:
            if not self.enabled or not self.to_emails:
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[{alert.severity.value.upper()}] NeuroScan Alert: {alert.rule_name}"
            
            # Create email body
            body = self._create_email_body(alert)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent for alert {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _create_email_body(self, alert: Alert) -> str:
        """Create HTML email body"""
        severity_colors = {
            AlertSeverity.INFO: "#17a2b8",
            AlertSeverity.WARNING: "#ffc107",
            AlertSeverity.ERROR: "#dc3545",
            AlertSeverity.CRITICAL: "#6f42c1"
        }
        
        color = severity_colors.get(alert.severity, "#6c757d")
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 20px;">
                <h2 style="color: {color}; margin-top: 0;">
                    NeuroScan Alert: {alert.rule_name}
                </h2>
                <p><strong>Severity:</strong> {alert.severity.value.upper()}</p>
                <p><strong>Status:</strong> {alert.status.value.upper()}</p>
                <p><strong>Time:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Message:</strong> {alert.message}</p>
                
                {self._format_details_html(alert.details)}
                
                {self._format_labels_html(alert.labels)}
                
                <hr style="margin: 20px 0;">
                <p style="color: #6c757d; font-size: 12px;">
                    This alert was generated by NeuroScan monitoring system.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _format_details_html(self, details: Dict[str, Any]) -> str:
        """Format alert details as HTML"""
        if not details:
            return ""
        
        html = "<h4>Details:</h4><ul>"
        for key, value in details.items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        html += "</ul>"
        return html
    
    def _format_labels_html(self, labels: Dict[str, str]) -> str:
        """Format alert labels as HTML"""
        if not labels:
            return ""
        
        html = "<h4>Labels:</h4><ul>"
        for key, value in labels.items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        html += "</ul>"
        return html


class SlackNotification(NotificationChannel):
    """Slack notification channel"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.webhook_url = config.get("webhook_url")
        self.channel = config.get("channel")
        self.username = config.get("username", "NeuroScan Monitor")
    
    async def send(self, alert: Alert) -> bool:
        """Send Slack notification"""
        try:
            if not self.enabled or not self.webhook_url:
                return False
            
            payload = self._create_slack_payload(alert)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent for alert {alert.id}")
                        return True
                    else:
                        logger.error(f"Slack notification failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _create_slack_payload(self, alert: Alert) -> Dict:
        """Create Slack message payload"""
        color_map = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ffaa00",
            AlertSeverity.ERROR: "#ff0000",
            AlertSeverity.CRITICAL: "#800080"
        }
        
        color = color_map.get(alert.severity, "#cccccc")
        
        fields = [
            {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
            {"title": "Status", "value": alert.status.value.upper(), "short": True},
            {"title": "Time", "value": alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'), "short": False}
        ]
        
        # Add details as fields
        for key, value in alert.details.items():
            fields.append({"title": key, "value": str(value), "short": True})
        
        payload = {
            "username": self.username,
            "attachments": [{
                "color": color,
                "title": f"NeuroScan Alert: {alert.rule_name}",
                "text": alert.message,
                "fields": fields,
                "footer": "NeuroScan Monitoring",
                "ts": int(alert.created_at.timestamp())
            }]
        }
        
        if self.channel:
            payload["channel"] = self.channel
        
        return payload


class WebhookNotification(NotificationChannel):
    """Generic webhook notification channel"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.url = config.get("url")
        self.method = config.get("method", "POST")
        self.headers = config.get("headers", {})
        self.template = config.get("template", {})
    
    async def send(self, alert: Alert) -> bool:
        """Send webhook notification"""
        try:
            if not self.enabled or not self.url:
                return False
            
            payload = self._create_webhook_payload(alert)
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    self.method,
                    self.url,
                    json=payload,
                    headers=self.headers
                ) as response:
                    if 200 <= response.status < 300:
                        logger.info(f"Webhook notification sent for alert {alert.id}")
                        return True
                    else:
                        logger.error(f"Webhook notification failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    def _create_webhook_payload(self, alert: Alert) -> Dict:
        """Create webhook payload"""
        if self.template:
            # Use custom template
            payload = self.template.copy()
            # Replace template variables
            payload = self._replace_template_vars(payload, alert)
            return payload
        else:
            # Use default format
            return alert.to_dict()
    
    def _replace_template_vars(self, template: Any, alert: Alert) -> Any:
        """Replace template variables with alert data"""
        if isinstance(template, str):
            # Replace variables in string
            return template.format(
                alert_id=alert.id,
                rule_name=alert.rule_name,
                severity=alert.severity.value,
                status=alert.status.value,
                message=alert.message,
                created_at=alert.created_at.isoformat()
            )
        elif isinstance(template, dict):
            # Replace variables in dictionary
            return {k: self._replace_template_vars(v, alert) for k, v in template.items()}
        elif isinstance(template, list):
            # Replace variables in list
            return [self._replace_template_vars(item, alert) for item in template]
        else:
            return template


class AlertManager:
    """Main alert management system"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.notification_channels: Dict[str, NotificationChannel] = {}
        self.rule_states: Dict[str, Dict] = defaultdict(dict)
        self.cooldown_periods: Dict[str, datetime] = {}
        
        # Load configuration
        if config_file:
            self.load_config(config_file)
        else:
            self._setup_default_config()
    
    async def initialize(self):
        """Initialize the alert manager"""
        try:
            logger.info("Initializing Alert Manager...")
            
            # Test notification channels
            for name, channel in self.notification_channels.items():
                try:
                    # Could perform test notification here
                    logger.info(f"✅ Notification channel '{name}' ready")
                except Exception as e:
                    logger.warning(f"⚠️ Notification channel '{name}' failed test: {e}")
            
            logger.info(f"✅ Alert Manager initialized with {len(self.rules)} rules")
        except Exception as e:
            logger.error(f"Failed to initialize Alert Manager: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup alert manager resources"""
        try:
            logger.info("Cleaning up Alert Manager...")
            
            # Close any persistent connections in notification channels
            for channel in self.notification_channels.values():
                if hasattr(channel, 'close'):
                    await channel.close()
            
            # Clear data structures
            self.active_alerts.clear()
            self.rule_states.clear()
            self.cooldown_periods.clear()
            
            logger.info("✅ Alert Manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during Alert Manager cleanup: {e}")
    
    def load_config(self, config_file: str):
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Load notification channels
            for channel_config in config.get("notification_channels", []):
                self.add_notification_channel(channel_config)
            
            # Load alert rules
            for rule_config in config.get("alert_rules", []):
                self.add_alert_rule(rule_config)
                
            logger.info(f"Loaded configuration from {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._setup_default_config()
    
    def _setup_default_config(self):
        """Setup default configuration"""
        # Default alert rules
        default_rules = [
            {
                "name": "high_error_rate",
                "description": "High API error rate detected",
                "condition": "error_rate > 10",
                "threshold": 10.0,
                "severity": "warning",
                "metric_name": "api_error_rate",
                "duration_minutes": 5
            },
            {
                "name": "critical_error_rate",
                "description": "Critical API error rate detected",
                "condition": "error_rate > 25",
                "threshold": 25.0,
                "severity": "critical",
                "metric_name": "api_error_rate",
                "duration_minutes": 2
            },
            {
                "name": "high_response_time",
                "description": "High API response time detected",
                "condition": "avg_response_time > 2000",
                "threshold": 2000.0,
                "severity": "warning",
                "metric_name": "api_response_time_ms",
                "duration_minutes": 10
            },
            {
                "name": "database_connection_failure",
                "description": "Database connection failure",
                "condition": "db_connection_errors > 0",
                "threshold": 0.0,
                "severity": "critical",
                "metric_name": "database_errors",
                "duration_minutes": 1
            },
            {
                "name": "disk_space_warning",
                "description": "Low disk space warning",
                "condition": "disk_usage_percent > 80",
                "threshold": 80.0,
                "severity": "warning",
                "metric_name": "disk_usage_percent",
                "duration_minutes": 30
            },
            {
                "name": "memory_usage_high",
                "description": "High memory usage detected",
                "condition": "memory_usage_percent > 85",
                "threshold": 85.0,
                "severity": "warning",
                "metric_name": "memory_usage_percent",
                "duration_minutes": 15
            }
        ]
        
        for rule_config in default_rules:
            self.add_alert_rule(rule_config)
    
    def add_notification_channel(self, config: Dict[str, Any]):
        """Add notification channel"""
        channel_type = config.get("type")
        name = config.get("name")
        
        if not channel_type or not name:
            logger.error("Invalid notification channel config")
            return
        
        if channel_type == "email":
            channel = EmailNotification(name, config)
        elif channel_type == "slack":
            channel = SlackNotification(name, config)
        elif channel_type == "webhook":
            channel = WebhookNotification(name, config)
        else:
            logger.error(f"Unknown notification channel type: {channel_type}")
            return
        
        self.notification_channels[name] = channel
        logger.info(f"Added notification channel: {name} ({channel_type})")
    
    def add_alert_rule(self, config: Dict[str, Any]):
        """Add alert rule"""
        try:
            rule = AlertRule(
                name=config["name"],
                description=config["description"],
                condition=config["condition"],
                threshold=float(config["threshold"]),
                severity=AlertSeverity(config["severity"]),
                metric_name=config["metric_name"],
                duration_minutes=config.get("duration_minutes", 5),
                cooldown_minutes=config.get("cooldown_minutes", 15),
                enabled=config.get("enabled", True),
                labels=config.get("labels", {}),
                annotations=config.get("annotations", {})
            )
            
            self.rules[rule.name] = rule
            logger.info(f"Added alert rule: {rule.name}")
            
        except Exception as e:
            logger.error(f"Failed to add alert rule: {e}")
    
    def evaluate_rules(self, metrics: Dict[str, Any]):
        """Evaluate all alert rules against current metrics"""
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            # Check if rule is in cooldown
            if rule_name in self.cooldown_periods:
                if datetime.now() < self.cooldown_periods[rule_name]:
                    continue
            
            try:
                self._evaluate_rule(rule, metrics)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_name}: {e}")
    
    def _evaluate_rule(self, rule: AlertRule, metrics: Dict[str, Any]):
        """Evaluate a single alert rule"""
        metric_value = metrics.get(rule.metric_name)
        
        if metric_value is None:
            return
        
        # Simple threshold evaluation (can be extended for complex conditions)
        triggered = False
        
        if ">" in rule.condition:
            triggered = metric_value > rule.threshold
        elif "<" in rule.condition:
            triggered = metric_value < rule.threshold
        elif "==" in rule.condition:
            triggered = metric_value == rule.threshold
        elif "!=" in rule.condition:
            triggered = metric_value != rule.threshold
        
        if triggered:
            self._handle_rule_triggered(rule, metric_value, metrics)
        else:
            self._handle_rule_resolved(rule)
    
    def _handle_rule_triggered(self, rule: AlertRule, value: float, metrics: Dict[str, Any]):
        """Handle triggered alert rule"""
        # Check if alert already exists
        existing_alert = None
        for alert in self.active_alerts.values():
            if alert.rule_name == rule.name and alert.status == AlertStatus.ACTIVE:
                existing_alert = alert
                break
        
        if existing_alert:
            # Update existing alert
            existing_alert.updated_at = datetime.now()
            existing_alert.details.update({
                "current_value": value,
                "threshold": rule.threshold,
                "condition": rule.condition
            })
        else:
            # Create new alert
            alert_id = self._generate_alert_id(rule, value)
            alert = Alert(
                id=alert_id,
                rule_name=rule.name,
                severity=rule.severity,
                status=AlertStatus.ACTIVE,
                message=f"{rule.description} - Current value: {value}, Threshold: {rule.threshold}",
                details={
                    "current_value": value,
                    "threshold": rule.threshold,
                    "condition": rule.condition,
                    "metric_name": rule.metric_name
                },
                created_at=datetime.now(),
                updated_at=datetime.now(),
                labels=rule.labels.copy(),
                annotations=rule.annotations.copy()
            )
            
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Send notifications
            asyncio.create_task(self._send_notifications(alert))
            
            # Set cooldown period
            cooldown_time = datetime.now() + timedelta(minutes=rule.cooldown_minutes)
            self.cooldown_periods[rule.name] = cooldown_time
            
            logger.warning(f"Alert triggered: {rule.name} - {alert.message}")
    
    def _handle_rule_resolved(self, rule: AlertRule):
        """Handle resolved alert rule"""
        # Find and resolve any active alerts for this rule
        for alert in list(self.active_alerts.values()):
            if alert.rule_name == rule.name and alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                alert.updated_at = datetime.now()
                
                # Remove from active alerts
                del self.active_alerts[alert.id]
                
                # Send resolution notification
                asyncio.create_task(self._send_notifications(alert))
                
                logger.info(f"Alert resolved: {rule.name}")
    
    def _generate_alert_id(self, rule: AlertRule, value: float) -> str:
        """Generate unique alert ID"""
        data = f"{rule.name}_{value}_{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    async def _send_notifications(self, alert: Alert):
        """Send notifications for alert"""
        for channel in self.notification_channels.values():
            try:
                await channel.send(alert)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.name}: {e}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            alert.updated_at = datetime.now()
            
            logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
        
        return False
    
    def suppress_alert(self, alert_id: str) -> bool:
        """Suppress an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.SUPPRESSED
            alert.updated_at = datetime.now()
            
            logger.info(f"Alert suppressed: {alert_id}")
            return True
        
        return False
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        return [alert.to_dict() for alert in self.active_alerts.values()]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get alert history"""
        recent_alerts = list(self.alert_history)[-limit:]
        return [alert.to_dict() for alert in recent_alerts]
    
    def get_alert_statistics(self) -> Dict:
        """Get alert statistics"""
        now = datetime.now()
        
        # Count alerts by severity and time period
        stats = {
            "total_active": len(self.active_alerts),
            "by_severity": defaultdict(int),
            "last_24h": 0,
            "last_7d": 0,
            "resolution_rate": 0
        }
        
        # Analyze alert history
        total_alerts = 0
        resolved_alerts = 0
        
        for alert in self.alert_history:
            total_alerts += 1
            
            # Count by severity
            stats["by_severity"][alert.severity.value] += 1
            
            # Count by time period
            if alert.created_at > now - timedelta(hours=24):
                stats["last_24h"] += 1
            if alert.created_at > now - timedelta(days=7):
                stats["last_7d"] += 1
            
            # Count resolved alerts
            if alert.status == AlertStatus.RESOLVED:
                resolved_alerts += 1
        
        # Calculate resolution rate
        if total_alerts > 0:
            stats["resolution_rate"] = round(resolved_alerts / total_alerts * 100, 2)
        
        return dict(stats)


# Global alert manager instance
alert_manager = AlertManager()


# Alert management functions for external use
def setup_alerting(config_file: Optional[str] = None):
    """Setup alerting system"""
    global alert_manager
    alert_manager = AlertManager(config_file)


def evaluate_metrics(metrics: Dict[str, Any]):
    """Evaluate metrics against alert rules"""
    alert_manager.evaluate_rules(metrics)


def get_active_alerts() -> List[Dict]:
    """Get active alerts"""
    return alert_manager.get_active_alerts()


def acknowledge_alert(alert_id: str, user: str) -> bool:
    """Acknowledge an alert"""
    return alert_manager.acknowledge_alert(alert_id, user)


def suppress_alert(alert_id: str) -> bool:
    """Suppress an alert"""
    return alert_manager.suppress_alert(alert_id)


def get_alert_statistics() -> Dict:
    """Get alert statistics"""
    return alert_manager.get_alert_statistics()
