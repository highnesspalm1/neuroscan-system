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
    pass


class CustomerUpdate(CustomerBase):
    name: Optional[str] = None


class Customer(CustomerBase):
    id: int
    logo_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProductCreate(ProductBase):
    customer_id: int


class ProductUpdate(ProductBase):
    name: Optional[str] = None


class Product(ProductBase):
    id: int
    customer_id: int
    created_at: datetime
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
