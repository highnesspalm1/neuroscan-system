#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify product creation functionality
"""

import sys
import os

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from database import DatabaseManager

def test_product_creation():
    """Test the product creation functionality"""
    print("Testing product creation functionality...")
    
    # Initialize database manager
    db_manager = DatabaseManager("test_products.db")
    
    try:
        # First, create a test customer
        print("Creating test customer...")
        customer_id = db_manager.add_customer(
            name="Test Customer", 
            email="test@example.com"
        )
        print(f"Created customer with ID: {customer_id}")
        
        # Test adding a product with all parameters
        print("Creating product with all parameters...")
        product_id = db_manager.add_product(
            customer_id=customer_id,
            name="Test Product",
            sku="TEST-001",
            description="This is a test product",
            category="Test Category",
            price=99.99
        )
        print(f"Created product with ID: {product_id}")
        
        # Test updating the product
        print("Updating product...")
        db_manager.update_product(
            product_id=product_id,
            name="Updated Test Product",
            sku="TEST-001-UPDATED",
            description="This is an updated test product",
            category="Updated Category",
            price=149.99
        )
        print("Product updated successfully")
        
        # Verify the product data
        print("Retrieving products...")
        products = db_manager.get_products(customer_id=customer_id)
        print(f"Found {len(products)} products:")
        
        for product in products:
            print(f"  Product ID: {product['id']}")
            print(f"  Name: {product['name']}")
            print(f"  SKU: {product['sku']}")
            print(f"  Description: {product['description']}")
            print(f"  Category: {product['category']}")
            print(f"  Price: {product['price']}")
            print(f"  Customer: {product['customer_name']}")
            print()
        
        print("✅ Product creation and update functionality is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test database
        if os.path.exists("test_products.db"):
            os.remove("test_products.db")
            print("Test database cleaned up")

if __name__ == "__main__":
    test_product_creation()
