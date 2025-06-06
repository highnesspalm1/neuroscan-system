#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket routes for real-time communication
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter
from typing import List, Dict
import json
import asyncio
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user_optional

router = APIRouter(prefix="/ws", tags=["websocket"])

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message)
        except:
            pass
    
    async def send_user_message(self, message: str, user_id: str):
        """Send message to all connections of a specific user"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id][:]:
                try:
                    await connection.send_text(message)
                except:
                    self.user_connections[user_id].remove(connection)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connections"""
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

# Global connection manager
manager = ConnectionManager()

@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    """WebSocket endpoint for general notifications"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Echo back for testing
            await manager.send_personal_message(
                json.dumps({
                    "type": "echo",
                    "message": data,
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.websocket("/admin/{user_id}")
async def websocket_admin(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for admin users"""
    await manager.connect(websocket, user_id)
    try:
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "type": "welcome",
                "message": "Connected to NeuroScan admin channel",
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }),
                    websocket
                )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# Utility functions for broadcasting events
async def broadcast_verification_event(qr_code: str, status: str):
    """Broadcast verification event to all connected clients"""
    message = json.dumps({
        "type": "verification",
        "qr_code": qr_code,
        "status": status,
        "timestamp": datetime.now().isoformat()
    })
    await manager.broadcast(message)

async def broadcast_admin_event(event_type: str, data: dict):
    """Broadcast admin event to admin users"""
    message = json.dumps({
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })
    
    # Send to all admin connections
    for user_id, connections in manager.user_connections.items():
        if user_id.startswith("admin_"):
            for connection in connections[:]:
                try:
                    await connection.send_text(message)
                except:
                    connections.remove(connection)
