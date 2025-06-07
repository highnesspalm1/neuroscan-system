#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Backend API
FastAPI-based REST API for certificate verification and management
Cloud-optimized for Render.com deployment
"""

import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, SessionLocal, Base
from app.core.security import RateLimitMiddleware
from app.core.database_init import init_database, check_database_health
from sqlalchemy import text
from app.routes import admin, verify, api_v1, pdf_labels, websockets, monitoring, documentation, webhooks_simple as webhooks, websocket, enhanced_api, monitoring_v2
from app.routes.monitoring import track_request_metrics
from app.core.caching import cache_manager
from app.core.analytics import analytics_engine
from app.routes.webhooks_simple import webhook_manager
from app.core.versioning import version_manager
from app.core.alerting import alert_manager
from app.core.observability import observability_dashboard
from app.core.database_init import init_database, check_database_health
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database with proper error handling
try:
    logger.info("Initializing database...")
    if init_database():
        logger.info("Database initialized successfully")
    else:
        logger.error("Database initialization failed")
except Exception as e:
    logger.error(f"Critical database error: {e}")
    # Continue startup - let the app handle database errors gracefully

# Initialize FastAPI app
app = FastAPI(
    title="NeuroScan API",
    description="""
    ## Premium Product Authentication System API
    
    ### Features:
    - **QR Code Verification**: Secure product authentication
    - **Certificate Management**: Digital certificate generation and validation
    - **Real-time Monitoring**: WebSocket-based live updates
    - **Advanced Security**: Rate limiting, API keys, signature validation
    - **Webhook Integration**: Event-driven notifications
    - **Comprehensive Monitoring**: Prometheus-compatible metrics
    
    ### API Extensibility:
    - WebSocket subscriptions for real-time events
    - Webhook endpoints for external integrations
    - Monitoring and metrics collection
    - Enhanced documentation with code examples
    - Rate limiting and advanced security features
    """,
    version="1.0.0",
    contact={
        "name": "NeuroCompany API Support",
        "url": "https://neurocompany.com/support",
        "email": "api@neurocompany.com"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://neurocompany.com/license"
    },    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[        {"name": "verification", "description": "Product verification operations"},
        {"name": "admin", "description": "Administrative operations"},
        {"name": "api", "description": "Core API operations"},
        {"name": "enhanced-api", "description": "Enhanced API with advanced features"},
        {"name": "pdf-labels", "description": "PDF label generation"},
        {"name": "websockets", "description": "WebSocket connections and real-time events"},
        {"name": "websocket", "description": "Basic WebSocket notifications"},
        {"name": "monitoring", "description": "API monitoring and metrics"},
        {"name": "monitoring-v2", "description": "Advanced monitoring with alerting"},
        {"name": "documentation", "description": "Enhanced API documentation"},
        {"name": "webhooks", "description": "Webhook management and delivery"}
    ]
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track all HTTP requests for monitoring"""
    return await track_request_metrics(request, call_next)

# Include routers
app.include_router(verify.router, prefix="/verify", tags=["verification"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(api_v1.router, prefix="/api/v1", tags=["api"])
app.include_router(enhanced_api.router, prefix="/api/v2", tags=["enhanced-api"])
app.include_router(pdf_labels.router, prefix="/labels", tags=["pdf-labels"])

# Include new API extensibility routers
app.include_router(websockets.router, prefix="/api/v1/ws", tags=["websockets"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])  # User's existing WebSocket
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(monitoring_v2.router, prefix="/api/v2/monitoring", tags=["monitoring-v2"])
app.include_router(documentation.router, prefix="/api/v1/docs", tags=["documentation"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    from app.routes.websockets import websocket_manager
    from app.routes.monitoring import metrics
    # webhook_manager is already imported at module level
      # Initialize advanced services
    await cache_manager.initialize()
    await analytics_engine.initialize()
    await webhook_manager.initialize()
    await version_manager.initialize()
    await alert_manager.initialize()
    await observability_dashboard.initialize()
    
    # Initialize existing services
    print("🚀 NeuroScan API starting up...")
    print("🔄 Advanced caching system initialized")
    print("📊 Business intelligence engine initialized")
    print("🪝 Advanced webhook system initialized")
    print("🔀 API versioning system initialized")
    print("🚨 Advanced alerting system initialized")
    print("👁️ Observability dashboard initialized")
    print("📈 Metrics collection initialized")
    print("🔌 WebSocket manager initialized")
    print("✅ NeuroScan API ready for requests")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    from app.routes.websockets import websocket_manager
      # Cleanup advanced services
    await cache_manager.cleanup()
    await analytics_engine.cleanup()
    await webhook_manager.cleanup()
    await alert_manager.cleanup()
    await observability_dashboard.cleanup()
    
    # Close all WebSocket connections
    await websocket_manager.disconnect_all()
    print("🛑 NeuroScan API shutting down...")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for cloud platforms (Render, Railway, etc.)"""
    try:
        # Test database connection
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            db_status = "connected"
            
            # Check if we're using PostgreSQL
            if "postgresql" in str(engine.url):
                db_type = "PostgreSQL"
            else:
                db_type = "SQLite"
                
        except Exception as e:
            db_status = f"error: {str(e)}"
            db_type = "unknown"
        finally:
            db.close()
        
        return {
            "status": "healthy",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "api_version": "1.0.0",
            "database": db_status,
            "database_type": db_type,
            "timestamp": "2025-06-06T12:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "NeuroScan Authentication API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "docs": "/docs",
        "health": "/health"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    # Get port from environment variable (Render sets PORT)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )
