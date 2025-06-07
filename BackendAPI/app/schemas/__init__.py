#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic schemas for API requests and responses
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# Customer schemas
class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None


class CustomerCreate(CustomerBase):
    username: Optional[str] = None  # Optional for admin creation
    password: Optional[str] = None  # Optional for admin creation


class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class Customer(CustomerBase):
    id: int
    username: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    logo_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[str] = None


class ProductCreate(ProductBase):
    customer_id: int


class ProductUpdate(ProductBase):
    name: Optional[str] = None


class Product(ProductBase):
    id: int
    customer_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer: Optional[Customer] = None
    
    class Config:
        from_attributes = True


# Certificate schemas
class CertificateBase(BaseModel):
    serial_number: str
    status: Optional[str] = "active"


class CertificateCreate(BaseModel):
    product_id: int
    customer_id: int


class CertificateUpdate(BaseModel):
    status: Optional[str] = None


class Certificate(CertificateBase):
    id: int
    product_id: int
    customer_id: int
    qr_code_path: Optional[str] = None
    pdf_label_path: Optional[str] = None
    created_at: datetime
    verified_at: Optional[datetime] = None
    product: Optional[Product] = None
    customer: Optional[Customer] = None
    
    class Config:
        from_attributes = True


# Verification schemas
class VerificationRequest(BaseModel):
    serial_number: str


class VerificationResponse(BaseModel):
    valid: bool
    serial_number: str
    product_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_logo: Optional[str] = None
    status: str
    verified_at: Optional[datetime] = None
    message: str


# Scan log schemas
class ScanLogCreate(BaseModel):
    serial_number: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[str] = None


class ScanLog(BaseModel):
    id: int
    serial_number: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    scan_time: datetime
    status: str
    location: Optional[str] = None
    
    class Config:
        from_attributes = True


# API Key schemas
class APIKeyCreate(BaseModel):
    name: str
    customer_id: Optional[int] = None


class APIKey(BaseModel):
    id: int
    name: str
    customer_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class APIKeyResponse(APIKey):
    key: str  # Only returned when creating new key


# Statistics schemas
class DashboardStats(BaseModel):
    total_customers: int
    total_products: int
    total_certificates: int
    active_certificates: int
    scans_today: int
    scans_this_week: int
    recent_scans: List[ScanLog]


# Bulk operation schemas
class BulkCertificateCreate(BaseModel):
    product_id: int
    customer_id: int
    count: int = 1


class BulkCertificateResponse(BaseModel):
    created_count: int
    certificates: List[Certificate]


# User authentication schemas
class UserBase(BaseModel):
    username: str
    email: str
    role: str = "user"
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[User] = None


class TokenData(BaseModel):
    username: Optional[str] = None


# Customer authentication schemas
class CustomerLogin(BaseModel):
    username: str
    password: str


class CustomerToken(BaseModel):
    access_token: str
    token_type: str
    customer: Optional[Customer] = None


class CustomerDashboardStats(BaseModel):
    total_products: int
    total_certificates: int
    active_certificates: int
    recent_scans: List[ScanLog]
    scans_this_month: int
