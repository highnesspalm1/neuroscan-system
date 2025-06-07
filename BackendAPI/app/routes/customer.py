#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Customer authentication and dashboard routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import timedelta, datetime
from typing import Optional

from ..core.database import get_db
from ..core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    verify_token
)
from ..schemas import (
    CustomerToken, 
    CustomerLogin, 
    Customer as CustomerSchema,
    CustomerDashboardStats,
    ScanLog as ScanLogSchema
)
from ..models import Customer, Product, Certificate, ScanLog
from ..core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="customer/token")


def authenticate_customer(db: Session, username: str, password: str) -> Optional[Customer]:
    """Authenticate customer with username and password"""
    customer = db.query(Customer).filter(
        and_(
            Customer.username == username,
            Customer.is_active == True
        )
    ).first()
    
    if not customer or not customer.hashed_password:
        return None
    if not verify_password(password, customer.hashed_password):
        return None
    return customer


def get_current_customer(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current customer from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        from jose import JWTError, jwt
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        role: str = payload.get("role", "")
        
        if username is None or role != "customer":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    customer = db.query(Customer).filter(
        and_(
            Customer.username == username,
            Customer.is_active == True
        )
    ).first()
    
    if customer is None:
        raise credentials_exception
    return customer


@router.post("/login", response_model=CustomerToken)
async def customer_login(
    customer_credentials: CustomerLogin, 
    db: Session = Depends(get_db)
):
    """Customer login endpoint"""
    
    customer = authenticate_customer(
        db, 
        customer_credentials.username, 
        customer_credentials.password
    )
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    customer.last_login = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": customer.username, "role": "customer"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "customer": customer
    }


@router.post("/token", response_model=CustomerToken)
async def customer_login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible customer token endpoint"""
    
    customer = authenticate_customer(db, form_data.username, form_data.password)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    customer.last_login = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": customer.username, "role": "customer"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=CustomerSchema)
async def get_current_customer_info(
    current_customer: Customer = Depends(get_current_customer)
):
    """Get current customer information"""
    return current_customer


@router.get("/dashboard", response_model=CustomerDashboardStats)
async def get_customer_dashboard(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Get customer dashboard statistics"""
    
    # Get customer's products
    total_products = db.query(Product).filter(
        Product.customer_id == current_customer.id
    ).count()
    
    # Get customer's certificates
    total_certificates = db.query(Certificate).filter(
        Certificate.customer_id == current_customer.id
    ).count()
    
    active_certificates = db.query(Certificate).filter(
        and_(
            Certificate.customer_id == current_customer.id,
            Certificate.status == "active"
        )
    ).count()
    
    # Get recent scans for customer's certificates
    recent_scans = db.query(ScanLog).join(Certificate).filter(
        Certificate.customer_id == current_customer.id
    ).order_by(ScanLog.scan_time.desc()).limit(10).all()
    
    # Get scans this month
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    scans_this_month = db.query(ScanLog).join(Certificate).filter(
        and_(
            Certificate.customer_id == current_customer.id,
            ScanLog.scan_time >= current_month_start
        )
    ).count()
    
    return {
        "total_products": total_products,
        "total_certificates": total_certificates,
        "active_certificates": active_certificates,
        "recent_scans": recent_scans,
        "scans_this_month": scans_this_month
    }


@router.get("/products")
async def get_customer_products(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get customer's products"""
    products = db.query(Product).filter(
        Product.customer_id == current_customer.id
    ).offset(skip).limit(limit).all()
    
    return products


@router.get("/certificates")
async def get_customer_certificates(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get customer's certificates"""
    certificates = db.query(Certificate).filter(
        Certificate.customer_id == current_customer.id
    ).offset(skip).limit(limit).all()
    
    return certificates


@router.get("/scan-logs")
async def get_customer_scan_logs(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get customer's scan logs"""
    scan_logs = db.query(ScanLog).join(Certificate).filter(
        Certificate.customer_id == current_customer.id
    ).order_by(ScanLog.scan_time.desc()).offset(skip).limit(limit).all()
    
    return scan_logs
