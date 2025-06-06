# NeuroScan API Documentation

## Overview

The NeuroScan API provides comprehensive endpoints for product authentication, certificate management, and system monitoring. This RESTful API is built with FastAPI and includes advanced security features, real-time capabilities, and extensible integrations.

## Base URL

```
Production: https://api.neuroscan.com
Development: http://localhost:8000
```

## Authentication

### JWT Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### API Key Authentication

Some endpoints support API key authentication for external integrations:

```http
X-API-Key: <your_api_key>
```

### Getting an Access Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@neurocompany.com",
    "role": "admin"
  }
}
```

## Core Endpoints

### Certificate Verification

#### Verify Certificate by QR Code

```http
POST /verify
Content-Type: application/json

{
  "qr_data": "encrypted_qr_content",
  "signature": "verification_signature"
}
```

**Response:**
```json
{
  "valid": true,
  "certificate": {
    "id": "NS-2024-001",
    "customer_name": "Premium Customer Ltd.",
    "product_name": "Luxury Product",
    "serial_number": "NS-2024-001",
    "creation_date": "2024-01-15T10:30:00Z",
    "verification_count": 5,
    "last_verified": "2024-06-02T14:22:00Z"
  },
  "verification_id": "ver_1234567890"
}
```

#### Get Certificate Details

```http
GET /verify/{serial_number}
```

**Response:**
```json
{
  "certificate": {
    "id": "NS-2024-001",
    "customer_name": "Premium Customer Ltd.",
    "product_name": "Luxury Product",
    "serial_number": "NS-2024-001",
    "creation_date": "2024-01-15T10:30:00Z",
    "verification_count": 5,
    "qr_code_url": "https://api.neuroscan.com/qr/NS-2024-001.png"
  }
}
```

### Administrative Operations

#### Create New Certificate

```http
POST /admin/certificate
Authorization: Bearer <token>
Content-Type: application/json

{
  "customer_name": "Premium Customer Ltd.",
  "product_name": "Luxury Product",
  "serial_number": "NS-2024-002",
  "additional_data": {
    "manufacture_date": "2024-06-01",
    "warranty_period": "24 months"
  }
}
```

**Response:**
```json
{
  "id": "NS-2024-002",
  "customer_name": "Premium Customer Ltd.",
  "product_name": "Luxury Product",
  "serial_number": "NS-2024-002",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "pdf_label_url": "https://api.neuroscan.com/labels/NS-2024-002.pdf",
  "created_at": "2024-06-02T15:00:00Z"
}
```

#### List Certificates

```http
GET /admin/certificates?page=1&limit=20&customer=Premium%20Customer
Authorization: Bearer <token>
```

**Response:**
```json
{
  "certificates": [
    {
      "id": "NS-2024-001",
      "customer_name": "Premium Customer Ltd.",
      "product_name": "Luxury Product",
      "serial_number": "NS-2024-001",
      "creation_date": "2024-01-15T10:30:00Z",
      "verification_count": 5
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```

#### Delete Certificate

```http
DELETE /admin/certificate/{serial_number}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Certificate NS-2024-001 deleted successfully"
}
```

### PDF Label Generation

#### Generate PDF Label

```http
POST /labels/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "serial_number": "NS-2024-001",
  "format": "A4",
  "include_logo": true,
  "custom_text": "Premium Product Line"
}
```

**Response:**
```json
{
  "pdf_url": "https://api.neuroscan.com/labels/NS-2024-001.pdf",
  "download_token": "tmp_abc123xyz",
  "expires_at": "2024-06-02T16:00:00Z"
}
```

#### Download PDF Label

```http
GET /labels/download/{download_token}
```

Returns PDF file with appropriate headers.

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Authentication

```javascript
ws.send(JSON.stringify({
  "action": "authenticate",
  "token": "your_jwt_token"
}));
```

### Subscribe to Events

```javascript
// Subscribe to certificate events
ws.send(JSON.stringify({
  "action": "subscribe",
  "channel": "certificates"
}));

// Subscribe to system events
ws.send(JSON.stringify({
  "action": "subscribe",
  "channel": "system"
}));
```

### Event Types

#### Certificate Verification Event

```json
{
  "type": "certificate.verified",
  "data": {
    "serial_number": "NS-2024-001",
    "customer_name": "Premium Customer Ltd.",
    "timestamp": "2024-06-02T14:22:00Z",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}
```

#### Certificate Creation Event

```json
{
  "type": "certificate.created",
  "data": {
    "serial_number": "NS-2024-002",
    "customer_name": "Premium Customer Ltd.",
    "created_by": "admin",
    "timestamp": "2024-06-02T15:00:00Z"
  }
}
```

#### System Alert Event

```json
{
  "type": "system.alert",
  "data": {
    "level": "warning",
    "message": "High verification rate detected",
    "details": {
      "rate": "50 requests/minute",
      "threshold": "30 requests/minute"
    },
    "timestamp": "2024-06-02T15:05:00Z"
  }
}
```

## Webhook Integration

### Register Webhook

```http
POST /api/v1/webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://your-app.com/webhook/neuroscan",
  "events": ["certificate.verified", "certificate.created"],
  "secret": "your_webhook_secret",
  "description": "Production webhook for order system"
}
```

**Response:**
```json
{
  "id": "webhook_123",
  "url": "https://your-app.com/webhook/neuroscan",
  "events": ["certificate.verified", "certificate.created"],
  "secret": "your_webhook_secret",
  "active": true,
  "created_at": "2024-06-02T15:10:00Z"
}
```

### Webhook Payload

When events occur, NeuroScan will send HTTP POST requests to your webhook URL:

```http
POST https://your-app.com/webhook/neuroscan
Content-Type: application/json
X-NeuroScan-Signature: sha256=...
X-NeuroScan-Event: certificate.verified

{
  "event": "certificate.verified",
  "timestamp": "2024-06-02T14:22:00Z",
  "data": {
    "serial_number": "NS-2024-001",
    "customer_name": "Premium Customer Ltd.",
    "product_name": "Luxury Product",
    "verification_count": 6,
    "verifier_ip": "192.168.1.100"
  }
}
```

### Webhook Security

Verify webhook authenticity using the signature:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## Monitoring and Metrics

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-06-02T15:15:00Z",
  "version": "1.0.0",
  "uptime": 86400,
  "database": "connected",
  "redis": "connected"
}
```

### Database Health

```http
GET /health/db
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "healthy",
  "connection_pool": {
    "active": 5,
    "idle": 10,
    "total": 15
  },
  "query_performance": {
    "avg_response_time": "12ms",
    "slow_queries": 0
  }
}
```

### Metrics (Prometheus Format)

```http
GET /metrics
Authorization: Bearer <token>
```

Returns Prometheus-formatted metrics:

```
# HELP neuroscan_requests_total Total number of requests
# TYPE neuroscan_requests_total counter
neuroscan_requests_total{method="GET",endpoint="/verify"} 1234

# HELP neuroscan_request_duration_seconds Request duration in seconds
# TYPE neuroscan_request_duration_seconds histogram
neuroscan_request_duration_seconds_bucket{le="0.1"} 500
neuroscan_request_duration_seconds_bucket{le="0.5"} 900
neuroscan_request_duration_seconds_bucket{le="1.0"} 950
neuroscan_request_duration_seconds_bucket{le="+Inf"} 1000
```

### API Statistics

```http
GET /api/v1/monitoring/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "period": "24h",
  "requests": {
    "total": 10000,
    "successful": 9850,
    "failed": 150
  },
  "verifications": {
    "total": 5000,
    "unique_certificates": 1200,
    "top_products": [
      {"name": "Luxury Product", "count": 1500},
      {"name": "Premium Device", "count": 1200}
    ]
  },
  "performance": {
    "avg_response_time": "45ms",
    "p95_response_time": "120ms",
    "p99_response_time": "250ms"
  }
}
```

## Security Features

### Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **General endpoints**: 100 requests per minute per IP
- **Verification endpoints**: 50 requests per minute per IP
- **Admin endpoints**: 30 requests per minute per user

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1717334400
```

### API Key Management

```http
POST /api/v1/api-keys
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "External Integration",
  "permissions": ["verify:read", "certificates:read"],
  "expires_at": "2025-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "key_id": "ak_123456",
  "api_key": "ns_live_abc123xyz789...",
  "name": "External Integration",
  "permissions": ["verify:read", "certificates:read"],
  "created_at": "2024-06-02T15:20:00Z",
  "expires_at": "2025-12-31T23:59:59Z"
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "CERTIFICATE_NOT_FOUND",
    "message": "Certificate with serial number NS-2024-999 not found",
    "details": {
      "serial_number": "NS-2024-999",
      "suggestions": [
        "Check if the serial number is correct",
        "Verify the certificate exists in the system"
      ]
    }
  },
  "request_id": "req_123456789"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Invalid username or password |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |
| `CERTIFICATE_NOT_FOUND` | 404 | Certificate does not exist |
| `INVALID_QR_CODE` | 400 | QR code format is invalid |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

## SDK and Libraries

### Python SDK

```python
from neuroscan import NeuroScanClient

client = NeuroScanClient(
    api_key="your_api_key",
    base_url="https://api.neuroscan.com"
)

# Verify certificate
result = client.verify_certificate("NS-2024-001")
print(f"Certificate valid: {result.valid}")

# Create certificate
cert = client.create_certificate(
    customer_name="Premium Customer Ltd.",
    product_name="Luxury Product",
    serial_number="NS-2024-003"
)
print(f"Certificate created: {cert.serial_number}")
```

### JavaScript SDK

```javascript
import { NeuroScanClient } from 'neuroscan-js';

const client = new NeuroScanClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.neuroscan.com'
});

// Verify certificate
const result = await client.verifyCertificate('NS-2024-001');
console.log(`Certificate valid: ${result.valid}`);

// Subscribe to real-time events
client.subscribe('certificates', (event) => {
  console.log('Certificate event:', event);
});
```

## Testing

### Sandbox Environment

Use the sandbox environment for testing:

```
Sandbox URL: https://sandbox-api.neuroscan.com
Test API Key: ns_test_abc123xyz789...
```

### Test Certificates

Pre-created test certificates for development:

| Serial Number | Customer | Product | Status |
|---------------|----------|---------|--------|
| `TEST-001` | Test Customer | Test Product | Valid |
| `TEST-002` | Test Customer | Test Product | Valid |
| `TEST-INVALID` | Test Customer | Test Product | Invalid |

## Support

- **Documentation**: [docs.neuroscan.com](https://docs.neuroscan.com)
- **API Status**: [status.neuroscan.com](https://status.neuroscan.com)
- **Support Email**: api-support@neurocompany.com
- **Developer Forum**: [forum.neuroscan.com](https://forum.neuroscan.com)

---

For more detailed examples and integration guides, visit our [Developer Portal](https://developers.neuroscan.com).
