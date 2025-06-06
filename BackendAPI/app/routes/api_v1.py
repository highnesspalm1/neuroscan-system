#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
External API routes (v1) for third-party integrations
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..core.security import verify_api_key
from ..models import Certificate, Product, Customer
from ..schemas import VerificationResponse

router = APIRouter()


async def get_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    """Dependency to verify API key"""
    if not verify_api_key(x_api_key, db):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@router.get("/verify/{serial_number}", response_model=VerificationResponse)
async def api_verify_certificate(
    serial_number: str,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    API endpoint for external verification
    Requires API key authentication
    """
    
    # Find certificate
    certificate = db.query(Certificate).filter(
        Certificate.serial_number == serial_number
    ).first()
    
    if not certificate:
        return VerificationResponse(
            valid=False,
            serial_number=serial_number,
            status="not_found",
            message="Certificate not found"
        )
    
    # Check certificate status
    if certificate.status != "active":
        return VerificationResponse(
            valid=False,
            serial_number=serial_number,
            status=certificate.status,
            message=f"Certificate status: {certificate.status}"
        )
    
    # Get product and customer info
    product = db.query(Product).filter(Product.id == certificate.product_id).first()
    customer = db.query(Customer).filter(Customer.id == certificate.customer_id).first()
    
    return VerificationResponse(
        valid=True,
        serial_number=serial_number,
        product_name=product.name if product else None,
        customer_name=customer.name if customer else None,
        customer_logo=customer.logo_path if customer else None,
        status="active",
        verified_at=certificate.verified_at,
        message="Product is authentic"
    )


@router.post("/certificates")
async def api_create_certificate(
    product_id: int,
    customer_id: int,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    API endpoint to create certificates externally
    For shop integrations, etc.
    """
    # Verify product and customer exist
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # This would use the same certificate creation logic as admin routes
    # Implementation details would depend on business requirements
    
    return {"message": "Certificate creation endpoint - implement based on requirements"}


@router.get("/health")
async def api_health():
    """Public health check for API"""
    return {"status": "healthy", "api_version": "v1"}
