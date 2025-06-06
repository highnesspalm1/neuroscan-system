#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLAlchemy models for NeuroScan
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True)
    logo_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="customer")
    certificates = relationship("Certificate", back_populates="customer")


class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="products")
    certificates = relationship("Certificate", back_populates="product")


class Certificate(Base):
    """Certificate model"""
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(String, default="active", index=True)  # active, inactive, revoked
    qr_code_path = Column(String)
    pdf_label_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True))
    
    # Relationships
    product = relationship("Product", back_populates="certificates")
    customer = relationship("Customer", back_populates="certificates")
    scan_logs = relationship("ScanLog", back_populates="certificate")


class ScanLog(Base):
    """Scan log model"""
    __tablename__ = "scan_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, ForeignKey("certificates.serial_number"), nullable=False)
    ip_address = Column(String)
    user_agent = Column(Text)
    scan_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="success")  # success, failed, suspicious
    location = Column(String)  # Geolocation if available
    
    # Relationships
    certificate = relationship("Certificate", back_populates="scan_logs")


class APIKey(Base):
    """API Key model for external access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)  # Human readable name
    customer_id = Column(Integer, ForeignKey("customers.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    last_used = Column(DateTime(timezone=True))
    
    # Relationships
    customer = relationship("Customer")
