#!/usr/bin/env python3
"""
Create a test customer with authentication credentials for testing the customer portal.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import asyncio
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.models import Customer
from app.core.database import engine
from app.core.security import get_password_hash

async def create_test_customer():
    """Create a test customer with authentication credentials."""
    
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if test customer already exists
        existing_customer = db.query(Customer).filter(
            Customer.username == "testcustomer"
        ).first()
        
        if existing_customer:
            print("✅ Test customer already exists!")
            print(f"   Username: {existing_customer.username}")
            print(f"   Customer: {existing_customer.name}")
            print(f"   Email: {existing_customer.email}")
            return existing_customer
          # Create test customer
        hashed_password = get_password_hash("password123")
        
        test_customer = Customer(
            name="Test Customer Company",
            email="test@customer.com",
            username="testcustomer",
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(test_customer)
        db.commit()
        db.refresh(test_customer)
        print("🎉 Test customer created successfully!")
        print(f"   Username: {test_customer.username}")
        print(f"   Password: password123")
        print(f"   Customer: {test_customer.name}")
        print(f"   Email: {test_customer.email}")
        print(f"   Customer ID: {test_customer.id}")
        print(f"   Active: {test_customer.is_active}")
        
        return test_customer
        
    except Exception as e:
        print(f"❌ Error creating test customer: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_test_customer())
