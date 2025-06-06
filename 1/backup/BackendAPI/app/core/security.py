#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication and security utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import time
from functools import wraps
from collections import defaultdict, deque
import hashlib
import hmac
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request, Header
import logging

from .config import settings
from .database import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_api_key() -> str:
    """Create API key for external access"""
    from secrets import token_urlsafe
    return token_urlsafe(32)


def verify_api_key(api_key: str, db: Session = Depends(get_db)) -> bool:
    """Verify API key"""
    # This would check against database in real implementation
    # For now, return True for demonstration
    return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with sliding window algorithm"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Max calls per period
        self.period = period  # Period in seconds
        self.clients = defaultdict(deque)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Clean old entries
        now = time.time()
        client_calls = self.clients[client_ip]
        
        # Remove calls older than the period
        while client_calls and client_calls[0] < now - self.period:
            client_calls.popleft()
        
        # Check if rate limit exceeded
        if len(client_calls) >= self.calls:
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                headers={
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(now + self.period))
                }
            )
        
        # Add current call
        client_calls.append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(self.calls - len(client_calls))
        response.headers["X-RateLimit-Reset"] = str(int(now + self.period))
        
        return response


class APIKeyManager:
    """API Key management and validation"""
    
    def __init__(self):
        # In production, store in database
        self.api_keys = {
            "nsc_live_key_001": {
                "name": "Production Client",
                "permissions": ["read", "write", "admin"],
                "rate_limit": 1000,
                "created": datetime.now(),
                "last_used": None
            },
            "nsc_test_key_001": {
                "name": "Test Client", 
                "permissions": ["read"],
                "rate_limit": 100,
                "created": datetime.now(),
                "last_used": None
            }
        }
    
    def validate_key(self, api_key: str) -> Optional[dict]:
        """Validate API key and return key info"""
        if api_key in self.api_keys:
            key_info = self.api_keys[api_key]
            key_info["last_used"] = datetime.now()
            return key_info
        return None
    
    def check_permission(self, api_key: str, permission: str) -> bool:
        """Check if API key has specific permission"""
        key_info = self.validate_key(api_key)
        return key_info and permission in key_info.get("permissions", [])


# Global API key manager instance
api_key_manager = APIKeyManager()


class APIKeyBearer(HTTPBearer):
    """Custom API Key authentication"""
    
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        api_key = credentials.credentials
        key_info = api_key_manager.validate_key(api_key)
        
        if not key_info:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Add key info to request state
        request.state.api_key_info = key_info
        return key_info


# API Key dependency
api_key_auth = APIKeyBearer()


def require_permission(permission: str):
    """Decorator to require specific API permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs or args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request or not hasattr(request.state, 'api_key_info'):
                raise HTTPException(status_code=401, detail="Authentication required")
            
            key_info = request.state.api_key_info
            if permission not in key_info.get("permissions", []):
                raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class SignatureValidator:
    """Request signature validation for webhook security"""
    
    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify request signature"""
        expected = SignatureValidator.generate_signature(payload, secret)
        return hmac.compare_digest(expected, signature)


def validate_webhook_signature(secret_key: str):
    """Dependency for webhook signature validation"""
    async def _validate(
        request: Request,
        x_signature: str = Header(..., alias="X-Signature")
    ):
        body = await request.body()
        payload = body.decode()
        
        if not SignatureValidator.verify_signature(payload, x_signature, secret_key):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        return payload
    
    return _validate


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Get current user from JWT token"""
    try:
        payload = verify_token(credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"id": user_id, "email": payload.get("email"), "role": payload.get("role", "user")}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(lambda: None)) -> Optional[dict]:
    """Get current user from JWT token (optional)"""
    if not credentials:
        return None
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


class SecurityManager:
    """Central security management class"""
    
    def __init__(self):
        self.api_key_manager = APIKeyManager()
        self.signature_validator = SignatureValidator()
        self.active_sessions = {}
        
    async def initialize(self):
        """Initialize security manager"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Security manager initialized")
        
    async def cleanup(self):
        """Cleanup security manager"""
        self.active_sessions.clear()
        self.logger.info("Security manager cleaned up")
        
    def validate_api_key(self, api_key: str) -> Optional[dict]:
        """Validate API key"""
        return self.api_key_manager.validate_key(api_key)
        
    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        return self.signature_validator.verify_signature(payload, signature, secret)
        
    async def track_session(self, user_id: str, session_data: dict):
        """Track user session"""
        self.active_sessions[user_id] = {
            **session_data,
            'last_activity': datetime.utcnow()
        }
        
    async def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        expired = [
            user_id for user_id, session in self.active_sessions.items()
            if session.get('last_activity', datetime.min) < cutoff
        ]
        for user_id in expired:
            del self.active_sessions[user_id]
