#!/usr/bin/env python3
"""
Create sample data for testing the customer portal.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from app.models import Customer, Product, Certificate, ScanLog
from app.core.database import engine
import random
import uuid

async def create_sample_data():
    """Create sample products, certificates, and scan logs for testing."""
    
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get the test customer
        customer = db.query(Customer).filter(Customer.username == "testcustomer").first()
        if not customer:
            print("❌ Test customer not found! Please run create_test_customer.py first.")
            return
            
        print(f"📦 Creating sample data for customer: {customer.name}")
        
        # Create sample products
        sample_products = [
            {
                "name": "Premium Laptop Pro",
                "sku": "LAPTOP-001",
                "description": "High-performance laptop with advanced security features",
                "category": "Electronics",
                "price": "$1,299.99"
            },
            {
                "name": "Wireless Headphones Elite",
                "sku": "AUDIO-001", 
                "description": "Premium wireless headphones with noise cancellation",
                "category": "Audio",
                "price": "$299.99"
            },
            {
                "name": "Smart Watch Series X",
                "sku": "WATCH-001",
                "description": "Advanced smartwatch with health monitoring",
                "category": "Wearables",
                "price": "$399.99"
            },
            {
                "name": "Gaming Keyboard RGB",
                "sku": "KEYB-001",
                "description": "Mechanical gaming keyboard with RGB lighting",
                "category": "Gaming",
                "price": "$149.99"
            },
            {
                "name": "Wireless Mouse Pro",
                "sku": "MOUSE-001",
                "description": "High-precision wireless gaming mouse",
                "category": "Gaming", 
                "price": "$79.99"
            }
        ]
        
        created_products = []
        for product_data in sample_products:
            # Check if product already exists
            existing = db.query(Product).filter(
                Product.customer_id == customer.id,
                Product.sku == product_data["sku"]
            ).first()
            
            if not existing:
                product = Product(
                    customer_id=customer.id,
                    name=product_data["name"],
                    sku=product_data["sku"],
                    description=product_data["description"],
                    category=product_data["category"],
                    price=product_data["price"]
                )
                db.add(product)
                db.flush()  # Get the ID
                created_products.append(product)
                print(f"   ✓ Created product: {product.name}")
            else:
                created_products.append(existing)
                print(f"   ⚠ Product already exists: {existing.name}")
        
        # Create sample certificates
        statuses = ["active", "expired", "revoked"]
        for i, product in enumerate(created_products):
            # Check if certificate already exists
            existing_cert = db.query(Certificate).filter(
                Certificate.customer_id == customer.id,
                Certificate.product_id == product.id
            ).first()
            
            if not existing_cert:
                # Create certificate with varying statuses and dates
                if i == 0:  # First product - active certificate
                    status = "active"
                    issued_date = datetime.now() - timedelta(days=30)
                    expires_at = datetime.now() + timedelta(days=365)                elif i == 1:  # Second product - expired certificate
                    status = "expired"
                    issued_date = datetime.now() - timedelta(days=400)
                    expires_at = datetime.now() - timedelta(days=30)
                else:  # Other products - active certificates
                    status = "active"
                    issued_date = datetime.now() - timedelta(days=random.randint(1, 90))
                    expires_at = datetime.now() + timedelta(days=random.randint(30, 365))
                
                certificate = Certificate(
                    customer_id=customer.id,
                    product_id=product.id,
                    serial_number=f"CERT-{uuid.uuid4().hex[:8].upper()}",
                    status=status
                )
                db.add(certificate)
                print(f"   ✓ Created certificate for {product.name}: {certificate.serial_number} ({status})")
            else:
                print(f"   ⚠ Certificate already exists for: {product.name}")
        
        # Create sample scan logs (verification attempts)
        print("📊 Creating sample scan logs...")
        for product in created_products[:3]:  # Only for first 3 products
            certificate = db.query(Certificate).filter(
                Certificate.product_id == product.id
            ).first()
            
            if certificate:
                # Create multiple scan entries with different dates
                for j in range(random.randint(5, 15)):
                    scan_date = datetime.now() - timedelta(days=random.randint(1, 60))
                      # Check if scan log already exists for this date (avoid duplicates)
                    existing_scan = db.query(ScanLog).filter(
                        ScanLog.serial_number == certificate.serial_number,
                        ScanLog.scan_time.between(
                            scan_date.replace(hour=0, minute=0, second=0),
                            scan_date.replace(hour=23, minute=59, second=59)
                        )
                    ).first()
                    
                    if not existing_scan:
                        scan_log = ScanLog(
                            serial_number=certificate.serial_number,
                            ip_address=f"192.168.1.{random.randint(10, 250)}",
                            user_agent="Mozilla/5.0 (Mobile Device) Scanner App",
                            location=random.choice(["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ"]),
                            scan_time=scan_date
                        )
                        db.add(scan_log)
        
        db.commit()
        print("✅ Sample data creation completed!")
        
        # Print summary
        product_count = db.query(Product).filter(Product.customer_id == customer.id).count()
        cert_count = db.query(Certificate).filter(Certificate.customer_id == customer.id).count()
        scan_count = db.query(ScanLog).join(Certificate).filter(Certificate.customer_id == customer.id).count()
        
        print(f"\n📈 Summary for {customer.name}:")
        print(f"   Products: {product_count}")
        print(f"   Certificates: {cert_count}")
        print(f"   Scan Logs: {scan_count}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
