#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook system for external integrations and notifications
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import aiohttp
import hashlib
import hmac
from dataclasses import dataclass, asdict
from uuid import uuid4
import logging

from ..core.security import api_key_auth, SignatureValidator, validate_webhook_signature
from ..core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    CERTIFICATE_SCANNED = "certificate.scanned"
    CERTIFICATE_CREATED = "certificate.created"
    CERTIFICATE_UPDATED = "certificate.updated"
    CERTIFICATE_STATUS_CHANGED = "certificate.status_changed"
    PRODUCT_CREATED = "product.created"
    CUSTOMER_CREATED = "customer.created"
    SYSTEM_ALERT = "system.alert"
    API_RATE_LIMITED = "api.rate_limited"


@dataclass
class WebhookPayload:
    """Webhook payload structure"""
    event: str
    timestamp: str
    data: Dict[str, Any]
    webhook_id: str
    api_version: str = "1.0"
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration"""
    id: str
    url: str
    secret: str
    events: List[str]
    active: bool
    created_at: str
    last_used: Optional[str] = None
    retry_count: int = 3
    timeout_seconds: int = 30
    headers: Dict[str, str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


class WebhookManager:
    """Webhook management and delivery system"""
    
    def __init__(self):
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.delivery_queue = None
        self.failed_deliveries: List[Dict] = []
        self.delivery_stats = {
            "total_sent": 0,
            "successful": 0,
            "failed": 0,
            "retries": 0
        }
        self._worker_task = None
        
    async def initialize(self):
        """Initialize the webhook manager"""
        if self.delivery_queue is None:
            self.delivery_queue = asyncio.Queue()
            self._worker_task = asyncio.create_task(self._delivery_worker())
    
    def register_endpoint(self, url: str, secret: str, events: List[str], 
                         headers: Dict[str, str] = None) -> str:
        """Register a new webhook endpoint"""
        endpoint_id = str(uuid4())
        
        endpoint = WebhookEndpoint(
            id=endpoint_id,
            url=url,
            secret=secret,
            events=events,
            active=True,
            created_at=datetime.now().isoformat(),
            headers=headers or {}
        )
        
        self.endpoints[endpoint_id] = endpoint
        logger.info(f"Registered webhook endpoint: {endpoint_id} -> {url}")
        
        return endpoint_id
    
    def update_endpoint(self, endpoint_id: str, **kwargs) -> bool:
        """Update webhook endpoint configuration"""
        if endpoint_id not in self.endpoints:
            return False
        
        endpoint = self.endpoints[endpoint_id]
        for key, value in kwargs.items():
            if hasattr(endpoint, key):
                setattr(endpoint, key, value)
        
        return True
    
    def deactivate_endpoint(self, endpoint_id: str) -> bool:
        """Deactivate webhook endpoint"""
        if endpoint_id in self.endpoints:
            self.endpoints[endpoint_id].active = False
            return True
        return False
    
    def delete_endpoint(self, endpoint_id: str) -> bool:
        """Delete webhook endpoint"""
        if endpoint_id in self.endpoints:
            del self.endpoints[endpoint_id]
            return True
        return False
    
    async def send_webhook(self, event: WebhookEvent, data: Dict[str, Any]) -> List[str]:
        """Send webhook to all registered endpoints for the event"""
        # Ensure initialization
        if self.delivery_queue is None:
            await self.initialize()
            
        payload = WebhookPayload(
            event=event.value,
            timestamp=datetime.now().isoformat(),
            data=data,
            webhook_id=str(uuid4())
        )
        
        delivered_to = []
        
        for endpoint_id, endpoint in self.endpoints.items():
            if not endpoint.active:
                continue
            
            if event.value not in endpoint.events and "all" not in endpoint.events:
                continue
            
            # Queue for delivery
            await self.delivery_queue.put((endpoint_id, payload))
            delivered_to.append(endpoint_id)
        
        return delivered_to
    
    async def _delivery_worker(self):
        """Background worker for webhook delivery"""
        while True:
            try:
                endpoint_id, payload = await self.delivery_queue.get()
                await self._deliver_webhook(endpoint_id, payload)
                self.delivery_queue.task_done()
            except Exception as e:
                logger.error(f"Webhook delivery worker error: {e}")
                await asyncio.sleep(1)
    
    async def _deliver_webhook(self, endpoint_id: str, payload: WebhookPayload):
        """Deliver webhook to specific endpoint"""
        if endpoint_id not in self.endpoints:
            return
        
        endpoint = self.endpoints[endpoint_id]
        payload_json = json.dumps(payload.to_dict())
        
        # Generate signature
        signature = SignatureValidator.generate_signature(payload_json, endpoint.secret)
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": payload.event,
            "X-Webhook-ID": payload.webhook_id,
            "User-Agent": "NeuroScan-Webhook/1.0"
        }
        
        # Add custom headers
        if endpoint.headers:
            headers.update(endpoint.headers)
        
        # Attempt delivery with retries
        for attempt in range(endpoint.retry_count + 1):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=endpoint.timeout_seconds)) as session:
                    async with session.post(endpoint.url, data=payload_json, headers=headers) as response:
                        if 200 <= response.status < 300:
                            # Success
                            endpoint.last_used = datetime.now().isoformat()
                            self.delivery_stats["successful"] += 1
                            logger.info(f"Webhook delivered successfully to {endpoint.url}")
                            return
                        else:
                            logger.warning(f"Webhook delivery failed with status {response.status} to {endpoint.url}")
            
            except Exception as e:
                logger.error(f"Webhook delivery attempt {attempt + 1} failed to {endpoint.url}: {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < endpoint.retry_count:
                await asyncio.sleep(2 ** attempt)
                self.delivery_stats["retries"] += 1
        
        # All retries failed
        self.delivery_stats["failed"] += 1
        self.failed_deliveries.append({
            "endpoint_id": endpoint_id,
            "endpoint_url": endpoint.url,
            "payload": payload.to_dict(),
            "failed_at": datetime.now().isoformat(),
            "attempts": endpoint.retry_count + 1
        })
        
        logger.error(f"Webhook delivery completely failed to {endpoint.url} after {endpoint.retry_count + 1} attempts")
    
    def get_stats(self) -> dict:
        """Get webhook delivery statistics"""
        return {
            "endpoints": {
                "total": len(self.endpoints),
                "active": sum(1 for ep in self.endpoints.values() if ep.active),
                "inactive": sum(1 for ep in self.endpoints.values() if not ep.active)
            },
            "deliveries": self.delivery_stats.copy(),
            "queue_size": self.delivery_queue.qsize(),
            "failed_deliveries": len(self.failed_deliveries)
        }
    
    def get_endpoints(self) -> List[dict]:
        """Get all webhook endpoints"""
        return [endpoint.to_dict() for endpoint in self.endpoints.values()]
    
    def get_failed_deliveries(self, limit: int = 100) -> List[dict]:
        """Get recent failed deliveries"""
        return self.failed_deliveries[-limit:]


# Global webhook manager
webhook_manager = WebhookManager()


@router.post("/endpoints")
async def create_webhook_endpoint(
    endpoint_data: dict,
    api_key_info: dict = Depends(api_key_auth)
):
    """Create new webhook endpoint"""
    from ..core.security import api_key_manager
    
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    url = endpoint_data.get("url")
    secret = endpoint_data.get("secret")
    events = endpoint_data.get("events", [])
    headers = endpoint_data.get("headers", {})
    
    if not url or not secret:
        raise HTTPException(status_code=400, detail="URL and secret are required")
    
    if not events:
        raise HTTPException(status_code=400, detail="At least one event type is required")
    
    # Validate events
    valid_events = [e.value for e in WebhookEvent] + ["all"]
    invalid_events = [event for event in events if event not in valid_events]
    if invalid_events:
        raise HTTPException(status_code=400, detail=f"Invalid events: {invalid_events}")
    
    endpoint_id = webhook_manager.register_endpoint(url, secret, events, headers)
    
    return {
        "endpoint_id": endpoint_id,
        "url": url,
        "events": events,
        "status": "created"
    }


@router.get("/endpoints")
async def list_webhook_endpoints(
    api_key_info: dict = Depends(api_key_auth)
):
    """List all webhook endpoints"""
    from ..core.security import api_key_manager
    
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    return {
        "endpoints": webhook_manager.get_endpoints(),
        "stats": webhook_manager.get_stats()
    }


@router.get("/endpoints/{endpoint_id}")
async def get_webhook_endpoint(
    endpoint_id: str,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get specific webhook endpoint"""
    from ..core.security import api_key_manager
    
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    if endpoint_id not in webhook_manager.endpoints:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    return webhook_manager.endpoints[endpoint_id].to_dict()


@router.put("/endpoints/{endpoint_id}")
async def update_webhook_endpoint(
    endpoint_id: str,
    update_data: dict,
    api_key_info: dict = Depends(api_key_auth)
):
    """Update webhook endpoint"""
    from ..core.security import api_key_manager
    
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    if not webhook_manager.update_endpoint(endpoint_id, **update_data):
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    return {
        "endpoint_id": endpoint_id,
        "status": "updated"
    }


@router.delete("/endpoints/{endpoint_id}")
async def delete_webhook_endpoint(
    endpoint_id: str,
    api_key_info: dict = Depends(api_key_auth)
):
    """Delete webhook endpoint"""
    from ..core.security import api_key_manager
    
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    if not webhook_manager.delete_endpoint(endpoint_id):
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    return {
        "endpoint_id": endpoint_id,
        "status": "deleted"
    }


@router.post("/endpoints/{endpoint_id}/test")
async def test_webhook_endpoint(
    endpoint_id: str,
    background_tasks: BackgroundTasks,
    api_key_info: dict = Depends(api_key_auth)
):
    """Test webhook endpoint with a sample payload"""
    from ..core.security import api_key_manager
    
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    if endpoint_id not in webhook_manager.endpoints:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    # Send test webhook
    test_data = {
        "test": True,
        "message": "This is a test webhook",
        "endpoint_id": endpoint_id,
        "timestamp": datetime.now().isoformat()
    }
    
    background_tasks.add_task(
        webhook_manager.send_webhook,
        WebhookEvent.SYSTEM_ALERT,
        test_data
    )
    
    return {
        "endpoint_id": endpoint_id,
        "status": "test_sent",
        "message": "Test webhook queued for delivery"
    }


@router.get("/events")
async def list_webhook_events():
    """List available webhook events"""
    return {
        "events": [
            {
                "name": event.value,
                "description": _get_event_description(event)
            }
            for event in WebhookEvent
        ]
    }


@router.get("/stats")
async def get_webhook_stats(
    api_key_info: dict = Depends(api_key_auth)
):
    """Get webhook delivery statistics"""
    return webhook_manager.get_stats()


@router.get("/failed-deliveries")
async def get_failed_deliveries(
    limit: int = 50,
    api_key_info: dict = Depends(api_key_auth)
):
    """Get recent failed webhook deliveries"""
    from ..core.security import api_key_manager
    
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    return {
        "failed_deliveries": webhook_manager.get_failed_deliveries(limit),
        "total_failed": len(webhook_manager.failed_deliveries)
    }


@router.post("/receive")
async def receive_webhook(
    request: Request,
    webhook_secret: str,
    payload: str = Depends(validate_webhook_signature("default_secret"))
):
    """Receive webhook from external system (example endpoint)"""
    try:
        data = json.loads(payload)
        
        # Process the webhook data
        logger.info(f"Received webhook: {data}")
        
        return {
            "status": "received",
            "message": "Webhook processed successfully"
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")


def _get_event_description(event: WebhookEvent) -> str:
    """Get description for webhook event"""
    descriptions = {
        WebhookEvent.CERTIFICATE_SCANNED: "Triggered when a certificate is scanned/verified",
        WebhookEvent.CERTIFICATE_CREATED: "Triggered when a new certificate is created",
        WebhookEvent.CERTIFICATE_UPDATED: "Triggered when a certificate is updated",
        WebhookEvent.CERTIFICATE_STATUS_CHANGED: "Triggered when certificate status changes",
        WebhookEvent.PRODUCT_CREATED: "Triggered when a new product is created",
        WebhookEvent.CUSTOMER_CREATED: "Triggered when a new customer is created",
        WebhookEvent.SYSTEM_ALERT: "Triggered for system alerts and notifications",
        WebhookEvent.API_RATE_LIMITED: "Triggered when API rate limits are exceeded"
    }
    return descriptions.get(event, "No description available")


# Helper functions to trigger webhooks (to be called from other modules)
async def trigger_certificate_scanned(certificate_data: dict):
    """Trigger webhook for certificate scan"""
    await webhook_manager.send_webhook(WebhookEvent.CERTIFICATE_SCANNED, certificate_data)


async def trigger_certificate_created(certificate_data: dict):
    """Trigger webhook for certificate creation"""
    await webhook_manager.send_webhook(WebhookEvent.CERTIFICATE_CREATED, certificate_data)


async def trigger_certificate_updated(certificate_data: dict):
    """Trigger webhook for certificate update"""
    await webhook_manager.send_webhook(WebhookEvent.CERTIFICATE_UPDATED, certificate_data)


async def trigger_product_created(product_data: dict):
    """Trigger webhook for product creation"""
    await webhook_manager.send_webhook(WebhookEvent.PRODUCT_CREATED, product_data)


async def trigger_system_alert(alert_data: dict):
    """Trigger webhook for system alert"""
    await webhook_manager.send_webhook(WebhookEvent.SYSTEM_ALERT, alert_data)
