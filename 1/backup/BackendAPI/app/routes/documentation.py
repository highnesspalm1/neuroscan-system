#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced API documentation and schema management
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, Response
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from ..core.security import api_key_auth
from ..core.config import settings

router = APIRouter()


class APIDocumentationManager:
    """Enhanced API documentation manager"""
    
    def __init__(self):
        self.custom_schemas = {}
        self.api_examples = {}
        self.changelog = []
        self.version_info = {
            "version": "1.0.0",
            "release_date": "2024-01-01",
            "status": "stable"
        }
    
    def add_schema_example(self, schema_name: str, example: dict, description: str = ""):
        """Add example for API schema"""
        if schema_name not in self.api_examples:
            self.api_examples[schema_name] = []
        
        self.api_examples[schema_name].append({
            "description": description,
            "example": example,
            "added_at": datetime.now().isoformat()
        })
    
    def add_changelog_entry(self, version: str, changes: List[str], release_date: str = None):
        """Add changelog entry"""
        entry = {
            "version": version,
            "release_date": release_date or datetime.now().strftime("%Y-%m-%d"),
            "changes": changes,
            "added_at": datetime.now().isoformat()
        }
        self.changelog.append(entry)
        self.changelog.sort(key=lambda x: x["version"], reverse=True)
    
    def get_enhanced_openapi_schema(self, app) -> dict:
        """Get enhanced OpenAPI schema with custom examples"""
        schema = get_openapi(
            title="NeuroScan API",
            version=self.version_info["version"],
            description=self.get_api_description(),
            routes=app.routes,
        )
        
        # Add custom info
        schema["info"].update({
            "contact": {
                "name": "NeuroScan Support",
                "email": "support@neuroscan.company",
                "url": "https://neuroscan.company/support"
            },
            "license": {
                "name": "Proprietary",
                "url": "https://neuroscan.company/license"
            },
            "termsOfService": "https://neuroscan.company/terms",
            "x-api-version": self.version_info["version"],
            "x-release-date": self.version_info["release_date"],
            "x-api-status": self.version_info["status"]
        })
        
        # Add security schemes
        schema["components"]["securitySchemes"] = {
            "ApiKeyAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "API Key",
                "description": "API Key authentication. Use your API key as the bearer token."
            },
            "JWTAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token authentication for admin access."
            }
        }
        
        # Add global security requirement
        schema["security"] = [
            {"ApiKeyAuth": []},
            {"JWTAuth": []}
        ]
        
        # Add custom examples to schemas
        if "components" in schema and "schemas" in schema["components"]:
            for schema_name, examples in self.api_examples.items():
                if schema_name in schema["components"]["schemas"]:
                    schema["components"]["schemas"][schema_name]["examples"] = examples
        
        # Add rate limiting info
        schema["x-rateLimit"] = {
            "default": "100 requests per minute",
            "authenticated": "1000 requests per minute",
            "admin": "Unlimited"
        }
        
        return schema
    
    def get_api_description(self) -> str:
        """Get comprehensive API description"""
        return """
# NeuroScan Premium Product Authentication API

## Overview
The NeuroScan API provides comprehensive certificate verification and management capabilities for premium product authentication. This API enables secure verification of product authenticity through QR codes and certificate management.

## Key Features
- **Certificate Verification**: Public endpoints for verifying product authenticity
- **Certificate Management**: Admin endpoints for creating and managing certificates
- **PDF Label Generation**: Generate QR code labels for products
- **Real-time Updates**: WebSocket support for live notifications
- **Analytics & Monitoring**: Comprehensive monitoring and metrics
- **Rate Limiting**: Built-in protection against abuse

## Authentication
This API supports two authentication methods:
1. **API Key Authentication**: For external integrations (Bearer token)
2. **JWT Authentication**: For admin dashboard access

## Rate Limiting
- **Anonymous requests**: 100 requests per minute
- **Authenticated requests**: 1000 requests per minute  
- **Admin requests**: Unlimited

## Error Handling
All errors follow RFC 7807 Problem Details standard with additional context.

## WebSocket Support
Real-time updates available via WebSocket connections for:
- Certificate scans
- System events
- Admin notifications

## Support
For technical support, contact: support@neuroscan.company
        """.strip()


# Global documentation manager
doc_manager = APIDocumentationManager()

# Add default examples
doc_manager.add_schema_example("VerificationResponse", {
    "valid": True,
    "serial_number": "NSC-2024-PRD001-CUST001-001",
    "product_name": "Premium Audio Device",
    "customer_name": "TechCorp Ltd",
    "status": "active",
    "verified_at": "2024-01-15T10:30:00Z",
    "message": "Product is authentic"
}, "Successful verification response")

doc_manager.add_schema_example("CertificateCreate", {
    "product_id": "PRD001",
    "customer_id": "CUST001"
}, "Create new certificate request")

doc_manager.add_schema_example("ProductCreate", {
    "name": "Premium Audio Device",
    "description": "High-quality wireless headphones",
    "model": "PAD-2024",
    "category": "Audio",
    "customer_id": "CUST001"
}, "Create new product request")

# Add changelog entries
doc_manager.add_changelog_entry("1.0.0", [
    "Initial API release",
    "Certificate verification endpoints",
    "Admin management endpoints",
    "PDF label generation",
    "WebSocket support",
    "Monitoring and metrics"
], "2024-01-01")


@router.get("/schema")
async def get_api_schema(
    format: str = "json",
    include_examples: bool = True,
    request: Request = None
):
    """Get OpenAPI schema in JSON or YAML format"""
    app = request.app
    schema = doc_manager.get_enhanced_openapi_schema(app)
    
    if not include_examples:
        # Remove examples from schema
        if "components" in schema and "schemas" in schema["components"]:
            for schema_def in schema["components"]["schemas"].values():
                schema_def.pop("examples", None)
    
    if format.lower() == "yaml":
        try:
            import yaml
            yaml_content = yaml.dump(schema, default_flow_style=False)
            return Response(content=yaml_content, media_type="application/x-yaml")
        except ImportError:
            raise HTTPException(status_code=400, detail="YAML format not supported. Install PyYAML.")
    
    return JSONResponse(content=schema)


@router.get("/docs/interactive", response_class=HTMLResponse)
async def get_interactive_docs():
    """Get enhanced interactive API documentation"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NeuroScan API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
        <style>
            .topbar {{ display: none; }}
            .swagger-ui .topbar {{ display: none; }}
            .info .title {{ color: #2E86C1; }}
            .swagger-ui .info .description {{ max-width: none; }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({{
                url: '/api/docs/schema',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                docExpansion: "list",
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                tryItOutEnabled: true,
                requestInterceptor: function(request) {{
                    // Add API key if available in localStorage
                    const apiKey = localStorage.getItem('neuroscan_api_key');
                    if (apiKey) {{
                        request.headers['Authorization'] = 'Bearer ' + apiKey;
                    }}
                    return request;
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/changelog")
async def get_api_changelog():
    """Get API changelog"""
    return {
        "api_version": doc_manager.version_info["version"],
        "changelog": doc_manager.changelog,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/examples")
async def get_api_examples(
    schema_name: Optional[str] = None
):
    """Get API usage examples"""
    if schema_name:
        return {
            "schema": schema_name,
            "examples": doc_manager.api_examples.get(schema_name, [])
        }
    
    return {
        "available_schemas": list(doc_manager.api_examples.keys()),
        "examples": doc_manager.api_examples
    }


@router.post("/examples")
async def add_api_example(
    example_data: dict,
    api_key_info: dict = Depends(api_key_auth)
):
    """Add new API example (admin only)"""
    from ..core.security import api_key_manager
    
    if not api_key_manager.check_permission(api_key_info.get("api_key", ""), "admin"):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    schema_name = example_data.get("schema_name")
    example = example_data.get("example")
    description = example_data.get("description", "")
    
    if not schema_name or not example:
        raise HTTPException(status_code=400, detail="schema_name and example are required")
    
    doc_manager.add_schema_example(schema_name, example, description)
    
    return {
        "message": "Example added successfully",
        "schema_name": schema_name
    }


@router.get("/postman")
async def get_postman_collection():
    """Get Postman collection for API testing"""
    collection = {
        "info": {
            "name": "NeuroScan API",
            "description": "Premium Product Authentication API",
            "version": doc_manager.version_info["version"],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{api_key}}",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "base_url",
                "value": "https://api.neuroscan.company",
                "type": "string"
            },
            {
                "key": "api_key",
                "value": "your_api_key_here",
                "type": "string"
            }
        ],
        "item": [
            {
                "name": "Verification",
                "item": [
                    {
                        "name": "Verify Certificate",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/verify/NSC-2024-PRD001-CUST001-001",
                                "host": ["{{base_url}}"],
                                "path": ["verify", "NSC-2024-PRD001-CUST001-001"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "Admin",
                "item": [
                    {
                        "name": "Get Dashboard Stats",
                        "request": {
                            "method": "GET",
                            "header": [],
                            "url": {
                                "raw": "{{base_url}}/admin/dashboard",
                                "host": ["{{base_url}}"],
                                "path": ["admin", "dashboard"]
                            }
                        }
                    },
                    {
                        "name": "Create Certificate",
                        "request": {
                            "method": "POST",
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "product_id": "PRD001",
                                    "customer_id": "CUST001"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/admin/certificates",
                                "host": ["{{base_url}}"],
                                "path": ["admin", "certificates"]
                            }
                        }
                    }
                ]
            }
        ]
    }
    
    return JSONResponse(
        content=collection,
        headers={"Content-Disposition": "attachment; filename=neuroscan-api.postman_collection.json"}
    )


@router.get("/sdk/examples")
async def get_sdk_examples(language: str = "python"):
    """Get SDK usage examples for different programming languages"""
    examples = {
        "python": {
            "install": "pip install requests",
            "verify_certificate": '''
import requests

# Verify a certificate
response = requests.get("https://api.neuroscan.company/verify/NSC-2024-PRD001-CUST001-001")
result = response.json()

if result["valid"]:
    print(f"Product {result['product_name']} is authentic!")
else:
    print(f"Verification failed: {result['message']}")
            '''.strip(),
            "admin_create_certificate": '''
import requests

headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

data = {
    "product_id": "PRD001",
    "customer_id": "CUST001"
}

response = requests.post(
    "https://api.neuroscan.company/admin/certificates",
    headers=headers,
    json=data
)

certificate = response.json()
print(f"Created certificate: {certificate['serial_number']}")
            '''.strip()
        },
        "javascript": {
            "install": "npm install axios",
            "verify_certificate": '''
const axios = require('axios');

// Verify a certificate
async function verifyCertificate(serialNumber) {
    try {
        const response = await axios.get(`https://api.neuroscan.company/verify/${serialNumber}`);
        const result = response.data;
        
        if (result.valid) {
            console.log(`Product ${result.product_name} is authentic!`);
        } else {
            console.log(`Verification failed: ${result.message}`);
        }
    } catch (error) {
        console.error('Verification error:', error.message);
    }
}

verifyCertificate('NSC-2024-PRD001-CUST001-001');
            '''.strip(),
            "admin_create_certificate": '''
const axios = require('axios');

async function createCertificate(productId, customerId) {
    try {
        const response = await axios.post(
            'https://api.neuroscan.company/admin/certificates',
            {
                product_id: productId,
                customer_id: customerId
            },
            {
                headers: {
                    'Authorization': 'Bearer YOUR_API_KEY',
                    'Content-Type': 'application/json'
                }
            }
        );
        
        const certificate = response.data;
        console.log(`Created certificate: ${certificate.serial_number}`);
    } catch (error) {
        console.error('Create certificate error:', error.message);
    }
}

createCertificate('PRD001', 'CUST001');
            '''.strip()
        },
        "curl": {
            "verify_certificate": '''
# Verify a certificate
curl -X GET "https://api.neuroscan.company/verify/NSC-2024-PRD001-CUST001-001"
            '''.strip(),
            "admin_create_certificate": '''
# Create a certificate (requires API key)
curl -X POST "https://api.neuroscan.company/admin/certificates" \\
     -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{
         "product_id": "PRD001",
         "customer_id": "CUST001"
     }'
            '''.strip()
        }
    }
    
    if language not in examples:
        return {"error": f"Language '{language}' not supported", "available_languages": list(examples.keys())}
    
    return {
        "language": language,
        "examples": examples[language]
    }


@router.get("/status")
async def get_api_status():
    """Get API status and version information"""
    return {
        "status": "operational",
        "version": doc_manager.version_info["version"],
        "release_date": doc_manager.version_info["release_date"],
        "api_status": doc_manager.version_info["status"],
        "features": [
            "Certificate Verification",
            "Admin Management",
            "PDF Label Generation",
            "WebSocket Support",
            "Real-time Monitoring",
            "Rate Limiting"
        ],
        "uptime": "99.9%",
        "last_updated": datetime.now().isoformat()
    }
