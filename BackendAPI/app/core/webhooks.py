"""
Advanced webhook system with event processing and delivery guarantees
"""
import asyncio
import aiohttp
import json
import hmac
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import backoff

logger = logging.getLogger(__name__)

class WebhookStatus(Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"

class EventType(Enum):
    """Types of webhook events"""
    PRODUCT_SCANNED = "product.scanned"
    USER_REGISTERED = "user.registered"
    CERTIFICATE_GENERATED = "certificate.generated"
    SECURITY_ALERT = "security.alert"
    PAYMENT_COMPLETED = "payment.completed"
    API_RATE_LIMIT_EXCEEDED = "api.rate_limit_exceeded"
    SYSTEM_HEALTH_DEGRADED = "system.health_degraded"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    DATA_EXPORT_REQUESTED = "data.export_requested"
    CUSTOM_EVENT = "custom.event"

@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration"""
    id: str
    url: str
    secret: str
    events: List[EventType]
    active: bool = True
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    created_at: datetime = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class WebhookEvent:
    """Webhook event data"""
    id: str
    event_type: EventType
    payload: Dict[str, Any]
    endpoint_id: str
    status: WebhookStatus = WebhookStatus.PENDING
    created_at: datetime = None
    scheduled_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    attempts: int = 0
    last_error: Optional[str] = None
    signature: Optional[str] = None

@dataclass
class WebhookDeliveryResult:
    """Result of webhook delivery attempt"""
    success: bool
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    delivery_time: Optional[float] = None

class WebhookEventProcessor:
    """Process and transform webhook events"""
    
    def __init__(self):
        self.event_processors: Dict[EventType, List[Callable]] = {}
        self.global_processors: List[Callable] = []
    
    def register_processor(self, event_type: EventType, processor: Callable):
        """Register an event processor for specific event type"""
        if event_type not in self.event_processors:
            self.event_processors[event_type] = []
        self.event_processors[event_type].append(processor)
    
    def register_global_processor(self, processor: Callable):
        """Register a global event processor for all events"""
        self.global_processors.append(processor)
    
    async def process_event(self, event: WebhookEvent) -> WebhookEvent:
        """Process event through registered processors"""
        # Apply global processors
        for processor in self.global_processors:
            try:
                if asyncio.iscoroutinefunction(processor):
                    event = await processor(event)
                else:
                    event = processor(event)
            except Exception as e:
                logger.error(f"Global processor failed: {e}")
        
        # Apply event-specific processors
        if event.event_type in self.event_processors:
            for processor in self.event_processors[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(processor):
                        event = await processor(event)
                    else:
                        event = processor(event)
                except Exception as e:
                    logger.error(f"Event processor failed for {event.event_type}: {e}")
        
        return event

class WebhookManager:
    """Advanced webhook management with delivery guarantees"""
    
    def __init__(self, db_session: AsyncSession, event_processor: WebhookEventProcessor = None):
        self.db = db_session
        self.event_processor = event_processor or WebhookEventProcessor()
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.delivery_queue = asyncio.Queue()
        self.delivery_workers = []
        self.is_running = False
        self._setup_default_processors()
    
    def _setup_default_processors(self):
        """Setup default event processors"""
        # Add timestamp processor
        self.event_processor.register_global_processor(self._add_timestamp)
        
        # Add security processor for sensitive data
        self.event_processor.register_processor(EventType.SECURITY_ALERT, self._process_security_alert)
        self.event_processor.register_processor(EventType.USER_REGISTERED, self._process_user_registration)
    
    async def _add_timestamp(self, event: WebhookEvent) -> WebhookEvent:
        """Add timestamp to event payload"""
        if 'timestamp' not in event.payload:
            event.payload['timestamp'] = datetime.utcnow().isoformat()
        return event
    
    async def _process_security_alert(self, event: WebhookEvent) -> WebhookEvent:
        """Process security alerts with additional context"""
        event.payload['severity_level'] = event.payload.get('severity', 'medium')
        event.payload['requires_immediate_attention'] = event.payload.get('severity') == 'critical'
        return event
    
    async def _process_user_registration(self, event: WebhookEvent) -> WebhookEvent:
        """Process user registration events"""
        # Remove sensitive data
        if 'password' in event.payload:
            del event.payload['password']
        if 'email' in event.payload:
            # Mask email for privacy
            email = event.payload['email']
            masked_email = email[:2] + '*' * (len(email.split('@')[0]) - 2) + '@' + email.split('@')[1]
            event.payload['email_masked'] = masked_email
        return event
    
    async def register_endpoint(self, endpoint: WebhookEndpoint) -> bool:
        """Register a new webhook endpoint"""
        try:
            # Store in database
            query = text("""
                INSERT INTO webhook_endpoints 
                (id, url, secret, events, active, headers, timeout, max_retries, retry_delay, created_at, metadata)
                VALUES (:id, :url, :secret, :events, :active, :headers, :timeout, :max_retries, :retry_delay, :created_at, :metadata)
            """)
            
            await self.db.execute(query, {
                'id': endpoint.id,
                'url': endpoint.url,
                'secret': endpoint.secret,
                'events': json.dumps([event.value for event in endpoint.events]),
                'active': endpoint.active,
                'headers': json.dumps(endpoint.headers) if endpoint.headers else None,
                'timeout': endpoint.timeout,
                'max_retries': endpoint.max_retries,
                'retry_delay': endpoint.retry_delay,
                'created_at': endpoint.created_at or datetime.utcnow(),
                'metadata': json.dumps(endpoint.metadata) if endpoint.metadata else None
            })
            await self.db.commit()
            
            # Store in memory
            self.endpoints[endpoint.id] = endpoint
            
            logger.info(f"Webhook endpoint registered: {endpoint.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register webhook endpoint: {e}")
            return False
    
    async def unregister_endpoint(self, endpoint_id: str) -> bool:
        """Unregister a webhook endpoint"""
        try:
            query = text("DELETE FROM webhook_endpoints WHERE id = :id")
            await self.db.execute(query, {'id': endpoint_id})
            await self.db.commit()
            
            self.endpoints.pop(endpoint_id, None)
            
            logger.info(f"Webhook endpoint unregistered: {endpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister webhook endpoint: {e}")
            return False
    
    async def load_endpoints(self):
        """Load webhook endpoints from database"""
        try:
            query = text("SELECT * FROM webhook_endpoints WHERE active = true")
            result = await self.db.execute(query)
            
            for row in result.fetchall():
                endpoint = WebhookEndpoint(
                    id=row.id,
                    url=row.url,
                    secret=row.secret,
                    events=[EventType(event) for event in json.loads(row.events)],
                    active=row.active,
                    headers=json.loads(row.headers) if row.headers else None,
                    timeout=row.timeout,
                    max_retries=row.max_retries,
                    retry_delay=row.retry_delay,
                    created_at=row.created_at,
                    metadata=json.loads(row.metadata) if row.metadata else None
                )
                self.endpoints[endpoint.id] = endpoint
            
            logger.info(f"Loaded {len(self.endpoints)} webhook endpoints")
            
        except Exception as e:
            logger.error(f"Failed to load webhook endpoints: {e}")
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def emit_event(self, event_type: EventType, payload: Dict[str, Any], metadata: Dict[str, Any] = None) -> List[str]:
        """Emit an event to all registered webhooks"""
        event_ids = []
        
        # Find endpoints that are subscribed to this event type
        matching_endpoints = [
            endpoint for endpoint in self.endpoints.values()
            if event_type in endpoint.events and endpoint.active
        ]
        
        for endpoint in matching_endpoints:
            event_id = str(uuid.uuid4())
            event = WebhookEvent(
                id=event_id,
                event_type=event_type,
                payload=payload.copy(),
                endpoint_id=endpoint.id,
                created_at=datetime.utcnow()
            )
            
            # Process event through processors
            event = await self.event_processor.process_event(event)
            
            # Generate signature
            payload_str = json.dumps(event.payload, sort_keys=True)
            event.signature = self._generate_signature(payload_str, endpoint.secret)
            
            # Store event in database
            await self._store_event(event)
            
            # Queue for delivery
            await self.delivery_queue.put(event)
            
            event_ids.append(event_id)
        
        logger.info(f"Emitted event {event_type.value} to {len(matching_endpoints)} endpoints")
        return event_ids
    
    async def _store_event(self, event: WebhookEvent):
        """Store webhook event in database"""
        try:
            query = text("""
                INSERT INTO webhook_events 
                (id, event_type, payload, endpoint_id, status, created_at, scheduled_at, attempts, signature)
                VALUES (:id, :event_type, :payload, :endpoint_id, :status, :created_at, :scheduled_at, :attempts, :signature)
            """)
            
            await self.db.execute(query, {
                'id': event.id,
                'event_type': event.event_type.value,
                'payload': json.dumps(event.payload),
                'endpoint_id': event.endpoint_id,
                'status': event.status.value,
                'created_at': event.created_at,
                'scheduled_at': event.scheduled_at,
                'attempts': event.attempts,
                'signature': event.signature
            })
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to store webhook event: {e}")
    
    async def _update_event_status(self, event: WebhookEvent):
        """Update webhook event status in database"""
        try:
            query = text("""
                UPDATE webhook_events 
                SET status = :status, delivered_at = :delivered_at, attempts = :attempts, last_error = :last_error
                WHERE id = :id
            """)
            
            await self.db.execute(query, {
                'id': event.id,
                'status': event.status.value,
                'delivered_at': event.delivered_at,
                'attempts': event.attempts,
                'last_error': event.last_error
            })
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update webhook event status: {e}")
    
    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=3)
    async def _deliver_webhook(self, event: WebhookEvent, endpoint: WebhookEndpoint) -> WebhookDeliveryResult:
        """Deliver webhook to endpoint with retries"""
        start_time = datetime.utcnow()
        
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': f'sha256={event.signature}',
            'X-Webhook-Event-Type': event.event_type.value,
            'X-Webhook-Event-ID': event.id,
            'User-Agent': 'NeuroScan-Webhook/1.0'
        }
        
        if endpoint.headers:
            headers.update(endpoint.headers)
        
        try:
            timeout = aiohttp.ClientTimeout(total=endpoint.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    endpoint.url,
                    json=event.payload,
                    headers=headers
                ) as response:
                    response_body = await response.text()
                    delivery_time = (datetime.utcnow() - start_time).total_seconds()
                    
                    if response.status in [200, 201, 202]:
                        return WebhookDeliveryResult(
                            success=True,
                            status_code=response.status,
                            response_body=response_body,
                            delivery_time=delivery_time
                        )
                    else:
                        return WebhookDeliveryResult(
                            success=False,
                            status_code=response.status,
                            response_body=response_body,
                            error_message=f"HTTP {response.status}",
                            delivery_time=delivery_time
                        )
        
        except asyncio.TimeoutError:
            return WebhookDeliveryResult(
                success=False,
                error_message="Request timeout",
                delivery_time=(datetime.utcnow() - start_time).total_seconds()
            )
        except Exception as e:
            return WebhookDeliveryResult(
                success=False,
                error_message=str(e),
                delivery_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _delivery_worker(self):
        """Worker to process webhook delivery queue"""
        while self.is_running:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self.delivery_queue.get(), timeout=1.0)
                
                endpoint = self.endpoints.get(event.endpoint_id)
                if not endpoint or not endpoint.active:
                    logger.warning(f"Endpoint not found or inactive: {event.endpoint_id}")
                    continue
                
                event.attempts += 1
                event.status = WebhookStatus.RETRYING if event.attempts > 1 else WebhookStatus.PENDING
                
                # Attempt delivery
                result = await self._deliver_webhook(event, endpoint)
                
                if result.success:
                    event.status = WebhookStatus.DELIVERED
                    event.delivered_at = datetime.utcnow()
                    logger.info(f"Webhook delivered successfully: {event.id}")
                else:
                    event.last_error = result.error_message
                    
                    if event.attempts >= endpoint.max_retries:
                        event.status = WebhookStatus.FAILED
                        logger.error(f"Webhook delivery failed after {event.attempts} attempts: {event.id}")
                    else:
                        # Schedule retry
                        event.status = WebhookStatus.RETRYING
                        event.scheduled_at = datetime.utcnow() + timedelta(seconds=endpoint.retry_delay * event.attempts)
                        
                        # Re-queue with delay
                        asyncio.create_task(self._schedule_retry(event, endpoint.retry_delay * event.attempts))
                        logger.warning(f"Webhook delivery failed, scheduled retry: {event.id}")
                
                # Update status in database
                await self._update_event_status(event)
                
                # Mark task as done
                self.delivery_queue.task_done()
                
            except asyncio.TimeoutError:
                continue  # No events in queue, continue
            except Exception as e:
                logger.error(f"Delivery worker error: {e}")
    
    async def _schedule_retry(self, event: WebhookEvent, delay: int):
        """Schedule event retry after delay"""
        await asyncio.sleep(delay)
        await self.delivery_queue.put(event)
    
    async def start_delivery_workers(self, num_workers: int = 3):
        """Start webhook delivery workers"""
        self.is_running = True
        
        for i in range(num_workers):
            worker = asyncio.create_task(self._delivery_worker())
            self.delivery_workers.append(worker)
        
        logger.info(f"Started {num_workers} webhook delivery workers")
    
    async def stop_delivery_workers(self):
        """Stop webhook delivery workers"""
        self.is_running = False
        
        # Wait for workers to finish
        if self.delivery_workers:
            await asyncio.gather(*self.delivery_workers, return_exceptions=True)
        
        self.delivery_workers.clear()
        logger.info("Stopped webhook delivery workers")
    
    async def get_event_status(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a webhook event"""
        try:
            query = text("SELECT * FROM webhook_events WHERE id = :id")
            result = await self.db.execute(query, {'id': event_id})
            row = result.fetchone()
            
            if row:
                return {
                    'id': row.id,
                    'event_type': row.event_type,
                    'endpoint_id': row.endpoint_id,
                    'status': row.status,
                    'created_at': row.created_at.isoformat(),
                    'delivered_at': row.delivered_at.isoformat() if row.delivered_at else None,
                    'attempts': row.attempts,
                    'last_error': row.last_error
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get event status: {e}")
            return None
    
    async def get_endpoint_stats(self, endpoint_id: str, days: int = 7) -> Dict[str, Any]:
        """Get delivery statistics for an endpoint"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = text("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(attempts) as avg_attempts
                FROM webhook_events 
                WHERE endpoint_id = :endpoint_id AND created_at >= :start_date
                GROUP BY status
            """)
            
            result = await self.db.execute(query, {
                'endpoint_id': endpoint_id,
                'start_date': start_date
            })
            
            stats = {'total': 0, 'by_status': {}}
            for row in result.fetchall():
                stats['by_status'][row.status] = {
                    'count': row.count,
                    'avg_attempts': float(row.avg_attempts)
                }
                stats['total'] += row.count
            
            # Calculate success rate
            delivered = stats['by_status'].get('delivered', {}).get('count', 0)
            stats['success_rate'] = (delivered / stats['total'] * 100) if stats['total'] > 0 else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get endpoint stats: {e}")
            return {}
    
    async def retry_failed_events(self, endpoint_id: str = None, hours: int = 24) -> int:
        """Retry failed webhook events"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            conditions = ["status = 'failed'", "created_at >= :cutoff_time"]
            params = {'cutoff_time': cutoff_time}
            
            if endpoint_id:
                conditions.append("endpoint_id = :endpoint_id")
                params['endpoint_id'] = endpoint_id
            
            query = text(f"""
                SELECT * FROM webhook_events 
                WHERE {' AND '.join(conditions)}
                ORDER BY created_at DESC
            """)
            
            result = await self.db.execute(query, params)
            
            retry_count = 0
            for row in result.fetchall():
                event = WebhookEvent(
                    id=row.id,
                    event_type=EventType(row.event_type),
                    payload=json.loads(row.payload),
                    endpoint_id=row.endpoint_id,
                    status=WebhookStatus.PENDING,
                    created_at=row.created_at,
                    attempts=0,  # Reset attempts for retry
                    signature=row.signature
                )
                
                await self.delivery_queue.put(event)
                retry_count += 1
            
            logger.info(f"Queued {retry_count} failed events for retry")
            return retry_count
            
        except Exception as e:
            logger.error(f"Failed to retry events: {e}")
            return 0

# Utility functions for common webhook scenarios
async def emit_product_scan_event(webhook_manager: WebhookManager, product_id: str, user_id: str, scan_result: str, metadata: Dict[str, Any] = None):
    """Emit product scan event"""
    payload = {
        'product_id': product_id,
        'user_id': user_id,
        'scan_result': scan_result,
        'scanned_at': datetime.utcnow().isoformat()
    }
    
    if metadata:
        payload.update(metadata)
    
    return await webhook_manager.emit_event(EventType.PRODUCT_SCANNED, payload)

async def emit_security_alert(webhook_manager: WebhookManager, alert_type: str, severity: str, details: Dict[str, Any]):
    """Emit security alert event"""
    payload = {
        'alert_type': alert_type,
        'severity': severity,
        'details': details,
        'detected_at': datetime.utcnow().isoformat()
    }
    
    return await webhook_manager.emit_event(EventType.SECURITY_ALERT, payload)

async def emit_user_registration(webhook_manager: WebhookManager, user_data: Dict[str, Any]):
    """Emit user registration event"""
    payload = {
        'user_id': user_data.get('id'),
        'email': user_data.get('email'),
        'registration_method': user_data.get('registration_method', 'web'),
        'registered_at': datetime.utcnow().isoformat()
    }
    
    return await webhook_manager.emit_event(EventType.USER_REGISTERED, payload)
