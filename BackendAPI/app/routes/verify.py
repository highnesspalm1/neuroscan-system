#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification routes for public certificate checking
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from ..core.database import get_db
from ..models import Certificate, ScanLog, Product, Customer
from ..schemas import VerificationResponse, ScanLogCreate

router = APIRouter()


@router.get("/{serial_number}", response_model=VerificationResponse)
async def verify_certificate(
    serial_number: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify a certificate by serial number
    Public endpoint - no authentication required
    """
    
    # Find certificate
    certificate = db.query(Certificate).filter(
        Certificate.serial_number == serial_number
    ).first()
    
    if not certificate:
        # Log failed scan attempt
        scan_log = ScanLog(
            serial_number=serial_number,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            status="failed"
        )
        db.add(scan_log)
        db.commit()
        
        return VerificationResponse(
            valid=False,
            serial_number=serial_number,
            status="not_found",
            message="Certificate not found. This may be a counterfeit product."
        )
    
    # Check certificate status
    if certificate.status != "active":
        # Log suspicious scan
        scan_log = ScanLog(
            serial_number=serial_number,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            status="suspicious"
        )
        db.add(scan_log)
        db.commit()
        
        return VerificationResponse(
            valid=False,
            serial_number=serial_number,
            status=certificate.status,
            message=f"Certificate status: {certificate.status}"
        )
    
    # Get product and customer info
    product = db.query(Product).filter(Product.id == certificate.product_id).first()
    customer = db.query(Customer).filter(Customer.id == certificate.customer_id).first()
    
    # Log successful scan
    scan_log = ScanLog(
        serial_number=serial_number,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        status="success"
    )
    db.add(scan_log)
    
    # Update certificate verified timestamp
    certificate.verified_at = datetime.utcnow()
    
    db.commit()
    
    return VerificationResponse(
        valid=True,
        serial_number=serial_number,
        product_name=product.name if product else None,
        customer_name=customer.name if customer else None,
        customer_logo=customer.logo_path if customer else None,
        status="active",
        verified_at=certificate.verified_at,
        message="Product is authentic and verified."
    )


@router.post("/check", response_model=VerificationResponse)
async def check_certificate(
    verification_request: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Alternative endpoint for POST requests (for API clients)
    """
    serial_number = verification_request.get("serial_number")
    if not serial_number:
        raise HTTPException(status_code=400, detail="Serial number is required")
    
    return await verify_certificate(serial_number, request, db)
