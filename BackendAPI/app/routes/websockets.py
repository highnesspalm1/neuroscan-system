#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket routes for real-time updates and notifications
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime
import logging

from ..core.security import api_key_manager
from ..models import ScanLog, Certificate

router = APIRouter()
logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket connection manager for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, api_key: str = None):
        """Accept WebSocket connection"""
        await websocket.accept()
        
        # Validate API key if provided
        if api_key:
            key_info = api_key_manager.validate_key(api_key)
            if not key_info:
                await websocket.close(code=1008, reason="Invalid API key")
                return False
            
            self.client_info[websocket] = {
                "api_key": api_key,
                "key_info": key_info,
                "connected_at": datetime.now(),
                "subscriptions": []
            }
        else:
            self.client_info[websocket] = {
                "api_key": None,
                "key_info": None,
                "connected_at": datetime.now(),
                "subscriptions": []
            }
        
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")
        return True
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.client_info:
            del self.client_info[websocket]
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict, subscription_type: str = None):
        """Broadcast message to all connected clients or filtered by subscription"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                client_info = self.client_info.get(websocket, {})
                
                # Check subscription filter
                if subscription_type:
                    subscriptions = client_info.get("subscriptions", [])
                    if subscription_type not in subscriptions:
                        continue
                
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def subscribe_client(self, websocket: WebSocket, subscription_type: str):
        """Subscribe client to specific event types"""
        if websocket in self.client_info:
            subscriptions = self.client_info[websocket].get("subscriptions", [])
            if subscription_type not in subscriptions:
                subscriptions.append(subscription_type)
                self.client_info[websocket]["subscriptions"] = subscriptions
    
    async def unsubscribe_client(self, websocket: WebSocket, subscription_type: str):
        """Unsubscribe client from specific event types"""
        if websocket in self.client_info:
            subscriptions = self.client_info[websocket].get("subscriptions", [])
            if subscription_type in subscriptions:
                subscriptions.remove(subscription_type)
                self.client_info[websocket]["subscriptions"] = subscriptions
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        total_connections = len(self.active_connections)
        authenticated_connections = sum(1 for info in self.client_info.values() if info.get("api_key"))
        
        subscription_stats = {}
        for info in self.client_info.values():
            for sub in info.get("subscriptions", []):
                subscription_stats[sub] = subscription_stats.get(sub, 0) + 1
        
        return {
            "total_connections": total_connections,
            "authenticated_connections": authenticated_connections,
            "anonymous_connections": total_connections - authenticated_connections,
            "subscription_stats": subscription_stats
        }


# Global WebSocket manager
websocket_manager = WebSocketManager()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, api_key: str = None):
    """Main WebSocket connection endpoint"""
    connected = await websocket_manager.connect(websocket, api_key)
    if not connected:
        return
    
    try:
        # Send welcome message
        await websocket_manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "status": "connected",
                "timestamp": datetime.now().isoformat(),
                "message": "Welcome to NeuroScan WebSocket API"
            }),
            websocket
        )
        
        while True:
            # Receive and handle client messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_client_message(websocket, message)
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }),
                    websocket
                )
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


async def handle_client_message(websocket: WebSocket, message: dict):
    """Handle incoming WebSocket messages from clients"""
    message_type = message.get("type")
    
    if message_type == "subscribe":
        subscription_type = message.get("subscription")
        if subscription_type in ["scans", "certificates", "system", "all"]:
            await websocket_manager.subscribe_client(websocket, subscription_type)
            await websocket_manager.send_personal_message(
                json.dumps({
                    "type": "subscription_confirmed",
                    "subscription": subscription_type,
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
        else:
            await websocket_manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "message": f"Invalid subscription type: {subscription_type}"
                }),
                websocket
            )
    
    elif message_type == "unsubscribe":
        subscription_type = message.get("subscription")
        await websocket_manager.unsubscribe_client(websocket, subscription_type)
        await websocket_manager.send_personal_message(
            json.dumps({
                "type": "unsubscription_confirmed",
                "subscription": subscription_type,
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
    
    elif message_type == "ping":
        await websocket_manager.send_personal_message(
            json.dumps({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
    
    elif message_type == "get_stats":
        # Check if client has admin permissions
        client_info = websocket_manager.client_info.get(websocket, {})
        key_info = client_info.get("key_info", {})
        
        if "admin" in key_info.get("permissions", []):
            stats = websocket_manager.get_stats()
            await websocket_manager.send_personal_message(
                json.dumps({
                    "type": "stats",
                    "data": stats,
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
        else:
            await websocket_manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "message": "Admin permissions required"
                }),
                websocket
            )


# Event notification functions (to be called from other parts of the application)
async def notify_scan_event(scan_data: dict):
    """Notify all subscribed clients about a new scan"""
    message = {
        "type": "scan_event",
        "data": scan_data,
        "timestamp": datetime.now().isoformat()
    }
    await websocket_manager.broadcast(message, "scans")
    await websocket_manager.broadcast(message, "all")


async def notify_certificate_event(certificate_data: dict, event_type: str = "created"):
    """Notify all subscribed clients about certificate events"""
    message = {
        "type": "certificate_event",
        "event": event_type,  # created, updated, deleted, status_changed
        "data": certificate_data,
        "timestamp": datetime.now().isoformat()
    }
    await websocket_manager.broadcast(message, "certificates")
    await websocket_manager.broadcast(message, "all")


async def notify_system_event(event_data: dict, event_type: str = "info"):
    """Notify all subscribed clients about system events"""
    message = {
        "type": "system_event",
        "event": event_type,  # info, warning, error, maintenance
        "data": event_data,
        "timestamp": datetime.now().isoformat()
    }
    await websocket_manager.broadcast(message, "system")
    await websocket_manager.broadcast(message, "all")


@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics (admin only)"""
    return websocket_manager.get_stats()
