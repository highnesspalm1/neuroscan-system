#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Label Generation API routes for NeuroScan Premium Product Authentication System

This module provides REST API endpoints for generating various types of PDF labels
including product labels, certificate labels, and batch labels for physical products.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io

from ..core.database import get_db
from ..core.security import verify_token
from ..models import Product, Certificate
from ..utils.pdf_label_generator import PDFLabelGenerator
from ..schemas import Product as ProductSchema

router = APIRouter()


@router.get("/product/{product_id}", 
            summary="Generate Product Label",
            description="Generate a PDF label for a specific product with QR code and product information")
async def generate_product_label(
    product_id: str,
    include_certificate: bool = Query(True, description="Include certificate information if available"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Generate PDF label for a specific product"""
    
    # Get product from database
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get associated certificate if requested and exists
    certificate = None
    if include_certificate:
        certificate = db.query(Certificate).filter(Certificate.product_id == product_id).first()
    
    # Prepare label data
    label_data = {
        "product_id": product.id,
        "product_name": product.name,
        "product_description": getattr(product, 'description', '') or '',
        "verification_url": f"https://neuroscan.company/verify/{getattr(product, 'serial_number', product.id)}",
        "certificate_id": certificate.id if certificate else None,
        "additional_info": {}
    }
    
    # Add optional product attributes
    if hasattr(product, 'model') and product.model:
        label_data["additional_info"]["Model"] = product.model
    if hasattr(product, 'category') and product.category:
        label_data["additional_info"]["Category"] = product.category
    if hasattr(product, 'manufacturer') and product.manufacturer:
        label_data["additional_info"]["Manufacturer"] = product.manufacturer
    
    try:
        # Generate PDF label
        generator = PDFLabelGenerator()
        pdf_buffer = generator.generate_single_label(**label_data)
        
        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=product_label_{product_id}.pdf",
                "Content-Type": "application/pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF label: {str(e)}")


@router.get("/certificate/{certificate_id}",
            summary="Generate Certificate Label", 
            description="Generate a PDF label for a specific certificate with enhanced security features")
async def generate_certificate_label(
    certificate_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Generate PDF label for a specific certificate"""
    
    # Get certificate from database
    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    # Prepare certificate label data
    certificate_data = {
        "id": certificate.id,
        "issue_date": certificate.issue_date.strftime("%Y-%m-%d") if hasattr(certificate, 'issue_date') and certificate.issue_date else "N/A",
        "expiry_date": certificate.expiry_date.strftime("%Y-%m-%d") if hasattr(certificate, 'expiry_date') and certificate.expiry_date else "N/A",
        "status": getattr(certificate, 'status', 'active'),
        "type": getattr(certificate, 'certificate_type', 'Premium'),
        "verification_url": f"https://neuroscan.company/verify/cert/{certificate.id}"
    }
    
    try:
        # Generate PDF certificate label
        generator = PDFLabelGenerator()
        pdf_buffer = generator.generate_certificate_label(certificate_data)
        
        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=certificate_label_{certificate_id}.pdf",
                "Content-Type": "application/pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating certificate label: {str(e)}")


@router.post("/batch",
             summary="Generate Batch Labels",
             description="Generate PDF labels for multiple products in a single document")
async def generate_batch_labels(
    product_ids: List[str],
    labels_per_page: int = Query(8, ge=2, le=16, description="Number of labels per page (2-16)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Generate batch PDF labels for multiple products"""
    
    if len(product_ids) > 100:  # Limit batch size for performance
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 100 products")
    
    if not product_ids:
        raise HTTPException(status_code=400, detail="Product IDs list cannot be empty")
    
    # Get products from database
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found with provided IDs")
    
    # Prepare batch data
    batch_data = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "verification_url": f"https://neuroscan.company/verify/{getattr(product, 'serial_number', product.id)}"
        }
        batch_data.append(product_data)
    
    try:
        # Generate batch labels PDF
        generator = PDFLabelGenerator()
        pdf_buffer = generator.generate_batch_labels(batch_data, labels_per_page=labels_per_page)
        
        # Return PDF as streaming response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=batch_labels_{timestamp}.pdf",
                "Content-Type": "application/pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating batch labels: {str(e)}")


@router.get("/all-products",
            summary="Generate All Products Labels",
            description="Generate PDF labels for all products in the database (with pagination)")
async def generate_all_products_labels(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of products to include"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    labels_per_page: int = Query(8, ge=2, le=16, description="Number of labels per page"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Generate labels for all products with pagination"""
    
    # Get products from database with pagination
    products = db.query(Product).offset(offset).limit(limit).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    
    # Prepare batch data
    batch_data = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "verification_url": f"https://neuroscan.company/verify/{getattr(product, 'serial_number', product.id)}"
        }
        batch_data.append(product_data)
    
    try:
        # Generate batch labels PDF
        generator = PDFLabelGenerator()
        pdf_buffer = generator.generate_batch_labels(batch_data, labels_per_page=labels_per_page)
        
        # Return PDF as streaming response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=all_products_labels_{timestamp}.pdf",
                "Content-Type": "application/pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating all products labels: {str(e)}")


@router.get("/template-preview",
            summary="Generate Template Preview",
            description="Generate a sample PDF label template for preview purposes")
async def generate_template_preview(
    label_type: str = Query("product", enum=["product", "certificate"], description="Type of label template"),
    current_user: dict = Depends(verify_token)
):
    """Generate a sample label template for preview"""
    
    try:
        generator = PDFLabelGenerator()
        
        if label_type == "product":
            # Sample product data
            sample_data = {
                "product_id": "SAMPLE-001",
                "product_name": "Premium Sample Product",
                "product_description": "This is a sample product label for preview purposes",
                "verification_url": "https://neuroscan.company/verify/SAMPLE-001",
                "certificate_id": "CERT-SAMPLE-001",
                "additional_info": {
                    "Model": "PSP-2024",
                    "Category": "Electronics"
                }
            }
            pdf_buffer = generator.generate_single_label(**sample_data)
            filename = "sample_product_label.pdf"
            
        else:  # certificate
            # Sample certificate data
            sample_cert_data = {
                "id": "CERT-SAMPLE-001",
                "issue_date": datetime.now().strftime("%Y-%m-%d"),
                "expiry_date": "2025-12-31",
                "status": "active",
                "type": "Premium",
                "verification_url": "https://neuroscan.company/verify/cert/CERT-SAMPLE-001"
            }
            pdf_buffer = generator.generate_certificate_label(sample_cert_data)
            filename = "sample_certificate_label.pdf"
        
        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating template preview: {str(e)}")


@router.get("/stats",
            summary="Get PDF Generation Statistics",
            description="Get statistics about PDF label generation usage")
async def get_pdf_stats(
    current_user: dict = Depends(verify_token)
):
    """Get PDF generation statistics"""
    
    # This would typically track usage in a database
    # For now, return mock statistics
    stats = {
        "total_labels_generated": 0,
        "product_labels": 0,
        "certificate_labels": 0,
        "batch_labels": 0,
        "last_generated": None,
        "most_popular_format": "product",
        "available_templates": ["product", "certificate", "batch"]
    }
    
    return stats
