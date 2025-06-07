#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin routes for internal management (Desktop App)
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import io
from datetime import datetime

from ..core.database import get_db, engine
from ..core.security import verify_token
from ..models import Customer, Product, Certificate, ScanLog
from ..schemas import (
    Customer as CustomerSchema, CustomerCreate, CustomerUpdate,
    Product as ProductSchema, ProductCreate, ProductUpdate,
    Certificate as CertificateSchema, CertificateCreate, CertificateUpdate,
    ScanLog as ScanLogSchema, DashboardStats,
    BulkCertificateCreate, BulkCertificateResponse
)
from ..utils.certificate_generator import generate_serial_number
from ..utils.pdf_label_generator import PDFLabelGenerator
from ..utils.pdf_label_generator import PDFLabelGenerator

router = APIRouter()


# Dashboard and Statistics
@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get dashboard statistics"""
    
    stats = DashboardStats(
        total_customers=db.query(Customer).count(),
        total_products=db.query(Product).count(),
        total_certificates=db.query(Certificate).count(),
        active_certificates=db.query(Certificate).filter(Certificate.status == "active").count(),
        scans_today=db.query(ScanLog).filter(
            ScanLog.scan_time >= "date('now')"
        ).count(),
        scans_this_week=db.query(ScanLog).filter(
            ScanLog.scan_time >= "datetime('now', '-7 days')"
        ).count(),
        recent_scans=db.query(ScanLog).order_by(ScanLog.scan_time.desc()).limit(10).all()
    )
    
    return stats


# Customer Management
@router.get("/customers", response_model=List[CustomerSchema])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get all customers"""
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers


@router.post("/customers", response_model=CustomerSchema)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Create a new customer"""
    from ..core.security import get_password_hash
    
    # Check if username is unique (if provided)
    if customer.username:
        existing_customer = db.query(Customer).filter(
            Customer.username == customer.username
        ).first()
        if existing_customer:
            raise HTTPException(
                status_code=400, 
                detail="Username already exists"
            )
    
    # Prepare customer data
    customer_data = customer.dict()
    
    # Hash password if provided
    if customer.password:
        customer_data["hashed_password"] = get_password_hash(customer.password)
        del customer_data["password"]  # Remove plain password
    
    db_customer = Customer(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/customers/{customer_id}", response_model=CustomerSchema)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get customer by ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerSchema)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Update customer"""
    from ..core.security import get_password_hash
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if username is unique (if being updated)
    if customer_update.username and customer_update.username != customer.username:
        existing_customer = db.query(Customer).filter(
            Customer.username == customer_update.username
        ).first()
        if existing_customer:
            raise HTTPException(
                status_code=400, 
                detail="Username already exists"
            )
    
    update_data = customer_update.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]  # Remove plain password
    
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Delete customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}


# Product Management
@router.get("/products", response_model=List[ProductSchema])
async def get_products(
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get all products, optionally filtered by customer"""
    query = db.query(Product)
    if customer_id:
        query = query.filter(Product.customer_id == customer_id)
    products = query.offset(skip).limit(limit).all()
    return products


@router.post("/products", response_model=ProductSchema)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Create a new product"""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == product.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/products/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Update product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Delete product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


# Certificate Management
@router.get("/certificates", response_model=List[CertificateSchema])
async def get_certificates(
    customer_id: Optional[int] = None,
    product_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get certificates with optional filters"""
    query = db.query(Certificate)
    
    if customer_id:
        query = query.filter(Certificate.customer_id == customer_id)
    if product_id:
        query = query.filter(Certificate.product_id == product_id)
    if status:
        query = query.filter(Certificate.status == status)
    
    certificates = query.offset(skip).limit(limit).all()
    return certificates


@router.post("/certificates", response_model=CertificateSchema)
async def create_certificate(
    certificate: CertificateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Create a new certificate"""
    # Verify product and customer exist
    product = db.query(Product).filter(Product.id == certificate.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    customer = db.query(Customer).filter(Customer.id == certificate.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate unique serial number
    serial_number = generate_serial_number(certificate.product_id, certificate.customer_id)
    
    # Ensure uniqueness
    while db.query(Certificate).filter(Certificate.serial_number == serial_number).first():
        serial_number = generate_serial_number(certificate.product_id, certificate.customer_id)
    
    db_certificate = Certificate(
        serial_number=serial_number,
        product_id=certificate.product_id,
        customer_id=certificate.customer_id
    )
    
    db.add(db_certificate)
    db.commit()
    db.refresh(db_certificate)
    return db_certificate


@router.post("/certificates/bulk", response_model=BulkCertificateResponse)
async def create_bulk_certificates(
    bulk_request: BulkCertificateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Create multiple certificates at once"""
    # Verify product and customer exist
    product = db.query(Product).filter(Product.id == bulk_request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    customer = db.query(Customer).filter(Customer.id == bulk_request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    certificates = []
    for _ in range(bulk_request.count):
        # Generate unique serial number
        serial_number = generate_serial_number(bulk_request.product_id, bulk_request.customer_id)
        
        # Ensure uniqueness
        while db.query(Certificate).filter(Certificate.serial_number == serial_number).first():
            serial_number = generate_serial_number(bulk_request.product_id, bulk_request.customer_id)
        
        db_certificate = Certificate(
            serial_number=serial_number,
            product_id=bulk_request.product_id,
            customer_id=bulk_request.customer_id
        )
        
        db.add(db_certificate)
        certificates.append(db_certificate)
    
    db.commit()
    
    # Refresh all certificates
    for cert in certificates:
        db.refresh(cert)
    
    return BulkCertificateResponse(
        created_count=len(certificates),
        certificates=certificates
    )


@router.put("/certificates/{certificate_id}", response_model=CertificateSchema)
async def update_certificate(
    certificate_id: int,
    certificate_update: CertificateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Update certificate status"""
    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    update_data = certificate_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(certificate, field, value)
    
    db.commit()
    db.refresh(certificate)
    return certificate


# Scan Logs
@router.get("/scan-logs", response_model=List[ScanLogSchema])
async def get_scan_logs(
    serial_number: Optional[str] = None,
    days: int = 30,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get scan logs"""
    query = db.query(ScanLog)
    
    if serial_number:
        query = query.filter(ScanLog.serial_number == serial_number)
      # Filter by days
    query = query.filter(ScanLog.scan_time >= f"datetime('now', '-{days} days')")
    
    scan_logs = query.order_by(ScanLog.scan_time.desc()).offset(skip).limit(limit).all()
    return scan_logs


# PDF Label Generation
@router.get("/labels/product/{product_id}")
async def generate_product_label(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Generate PDF label for a specific product"""
    
    # Get product from database
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get associated certificate if exists
    certificate = db.query(Certificate).filter(Certificate.product_id == product_id).first()
    
    # Prepare label data
    label_data = {
        "product_id": product.id,
        "product_name": product.name,
        "product_description": product.description or "",
        "verification_url": f"https://neuroscan.company/verify/{product.serial_number}",
        "certificate_id": certificate.id if certificate else None,
        "additional_info": {
            "Model": product.model if hasattr(product, 'model') else None,
            "Category": product.category if hasattr(product, 'category') else None,
        }
    }
    
    # Generate PDF label
    generator = PDFLabelGenerator()
    pdf_buffer = generator.generate_single_label(**label_data)
    
    # Return PDF as streaming response
    return StreamingResponse(
        io.BytesIO(pdf_buffer.read()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=label_{product_id}.pdf"}
    )


@router.get("/labels/certificate/{certificate_id}")
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
        "issue_date": certificate.issue_date.strftime("%Y-%m-%d") if certificate.issue_date else "N/A",
        "expiry_date": certificate.expiry_date.strftime("%Y-%m-%d") if certificate.expiry_date else "N/A",
        "status": certificate.status,
        "type": certificate.certificate_type if hasattr(certificate, 'certificate_type') else "Premium",
        "verification_url": f"https://neuroscan.company/verify/cert/{certificate.id}"
    }
    
    # Generate PDF certificate label
    generator = PDFLabelGenerator()
    pdf_buffer = generator.generate_certificate_label(certificate_data)
    
    # Return PDF as streaming response
    return StreamingResponse(
        io.BytesIO(pdf_buffer.read()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=certificate_label_{certificate_id}.pdf"}
    )


@router.post("/labels/batch")
async def generate_batch_labels(
    product_ids: List[str],
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Generate batch PDF labels for multiple products"""
    
    if len(product_ids) > 50:  # Limit batch size
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 50 products")
    
    # Get products from database
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    
    # Prepare batch data
    batch_data = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "verification_url": f"https://neuroscan.company/verify/{product.serial_number}"
        }
        batch_data.append(product_data)
    
    # Generate batch labels PDF
    generator = PDFLabelGenerator()
    pdf_buffer = generator.generate_batch_labels(batch_data)
    
    # Return PDF as streaming response
    return StreamingResponse(
        io.BytesIO(pdf_buffer.read()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=batch_labels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
    )


@router.get("/labels/all-products")
async def generate_all_products_labels(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Generate labels for all products (with limit)"""
    
    # Get all products (limited)
    products = db.query(Product).limit(limit).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    
    # Prepare batch data
    batch_data = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "verification_url": f"https://neuroscan.company/verify/{product.serial_number}"
        }
        batch_data.append(product_data)
    
    # Generate batch labels PDF
    generator = PDFLabelGenerator()
    pdf_buffer = generator.generate_batch_labels(batch_data)
    
    # Return PDF as streaming response
    return StreamingResponse(
        io.BytesIO(pdf_buffer.read()),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=all_products_labels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
    )


# Database Migration Endpoints
@router.post("/migrate")
async def run_database_migration(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Run database migration to add new product fields"""
    try:
        # SQL commands to add new columns
        migration_sql = [
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS sku VARCHAR(255)",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS category VARCHAR(255)", 
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS price VARCHAR(50)",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE",
            "CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
            "UPDATE products SET updated_at = created_at WHERE updated_at IS NULL"
        ]
        
        # Execute migration commands
        for sql in migration_sql:
            db.execute(text(sql))
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Database migration completed successfully",
            "fields_added": ["sku", "category", "price", "updated_at"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.post("/init-db")
async def initialize_database(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Initialize/recreate database schema with all fields"""
    try:
        # Import Base and create all tables with updated schema
        from ..models import Base
        Base.metadata.create_all(bind=engine)
        
        return {
            "status": "success", 
            "message": "Database schema initialized successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")


@router.get("/db-schema")
async def get_database_schema(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Get current database schema information"""
    try:
        # Query to get column information for products table
        schema_query = """
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'products' 
        ORDER BY ordinal_position
        """
        
        result = db.execute(text(schema_query))
        columns = [dict(row) for row in result]
        
        return {
            "status": "success",
            "table": "products",
            "columns": columns,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Fallback for SQLite or other databases
        try:
            # Get a sample product to see available fields
            sample_product = db.query(Product).first()
            if sample_product:
                available_fields = list(sample_product.__dict__.keys())
                available_fields = [f for f in available_fields if not f.startswith('_')]
            else:
                available_fields = ["No products found"]
                
            return {
                "status": "success",
                "table": "products", 
                "available_fields": available_fields,
                "note": "Schema info from sample record (SQLite)",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Schema query failed: {str(e2)}")
