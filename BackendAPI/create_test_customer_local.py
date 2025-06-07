#!/usr/bin/env python3
"""
Create a test customer with authentication credentials for live testing
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import Customer
from app.core.security import get_password_hash

def create_test_customer_local():
    """Create a test customer in the local database for testing"""
    db = SessionLocal()
    
    try:
        # Check if test customer already exists
        existing = db.query(Customer).filter(Customer.username == "testcustomer").first()
        if existing:
            print("✅ Test customer already exists!")
            print(f"   Username: {existing.username}")
            print(f"   Email: {existing.email}")
            print(f"   Active: {existing.is_active}")
            return existing
        
        # Create test customer
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
        db.refresh(test_customer)
        
        print("✅ Test customer created successfully!")
        print(f"   Username: {test_customer.username}")
        print(f"   Password: password123")
        print(f"   Email: {test_customer.email}")
        print(f"   Customer ID: {test_customer.id}")
        print(f"   Active: {test_customer.is_active}")
        
        return test_customer
        
    except Exception as e:
        print(f"❌ Error creating test customer: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    customer = create_test_customer_local()
    if customer:
        print(f"\n🎉 Ready to test Customer Portal with:")
        print(f"   🔐 Username: testcustomer") 
        print(f"   🔑 Password: password123")
