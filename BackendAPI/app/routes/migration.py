#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database migration endpoints for production deployment
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from typing import Dict, Any

from ..core.database import get_db, engine
from ..core.security import get_password_hash
from ..models import Customer, User
from ..schemas import User as UserSchema

router = APIRouter()

def get_current_admin_user(db: Session = Depends(get_db)) -> User:
    """Get current admin user - simplified for migration"""
    # For migration purposes, allow if any admin exists
    admin = db.query(User).filter(User.role == "admin").first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No admin user found"
        )
    return admin

@router.post("/migrate-customer-auth")
async def migrate_customer_auth(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Migrate customer table to add authentication fields"""
    
    try:
        # Check current table structure
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('customers')]
        
        print(f"Current customer table columns: {columns}")
        
        # Migration SQL for PostgreSQL
        migration_sql = """
        -- Add customer authentication fields if they don't exist
        DO $$
        BEGIN
            -- Add username column if it doesn't exist
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'username'
            ) THEN
                ALTER TABLE customers ADD COLUMN username VARCHAR(100);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_username ON customers(username);
            END IF;
            
            -- Add hashed_password column if it doesn't exist
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'hashed_password'
            ) THEN
                ALTER TABLE customers ADD COLUMN hashed_password VARCHAR(255);
            END IF;
            
            -- Add is_active column if it doesn't exist
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'is_active'
            ) THEN
                ALTER TABLE customers ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
            END IF;
            
            -- Add last_login column if it doesn't exist
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'last_login'
            ) THEN
                ALTER TABLE customers ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
            END IF;
            
        END $$;
        """
        
        # Execute migration
        db.execute(text(migration_sql))
        db.commit()
        
        # Verify migration
        inspector = inspect(engine)
        new_columns = [col['name'] for col in inspector.get_columns('customers')]
        
        # Create test customer if none exists
        existing_customer = db.query(Customer).filter(Customer.username == "testcustomer").first()
        if not existing_customer:
            hashed_password = get_password_hash("password123")
            
            test_customer = Customer(
                name="Test Customer",
                email="test@customer.com",
                username="testcustomer",
                hashed_password=hashed_password,
                is_active=True
            )
            
            db.add(test_customer)
            db.commit()
            
            return {
                "status": "success",
                "message": "Customer authentication migration completed",
                "columns_before": columns,
                "columns_after": new_columns,
                "test_customer_created": True,
                "test_credentials": {
                    "username": "testcustomer",
                    "password": "password123"
                }
            }
        else:
            return {
                "status": "success", 
                "message": "Customer authentication migration completed",
                "columns_before": columns,
                "columns_after": new_columns,
                "test_customer_created": False,
                "existing_customer": existing_customer.username
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )

@router.get("/check-customer-schema")
async def check_customer_schema(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Check current customer table schema"""
    
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns('customers')
        indexes = inspector.get_indexes('customers')
        
        # Check for existing customers
        customer_count = db.query(Customer).count()
        customers_with_auth = db.query(Customer).filter(Customer.username.isnot(None)).count()
        
        return {
            "status": "success",
            "table_exists": True,
            "columns": [{"name": col["name"], "type": str(col["type"])} for col in columns],
            "indexes": [idx["name"] for idx in indexes],
            "customer_count": customer_count,
            "customers_with_auth": customers_with_auth,
            "auth_fields_exist": {
                "username": any(col["name"] == "username" for col in columns),
                "hashed_password": any(col["name"] == "hashed_password" for col in columns),
                "is_active": any(col["name"] == "is_active" for col in columns),
                "last_login": any(col["name"] == "last_login" for col in columns)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Schema check failed: {str(e)}"
        }
