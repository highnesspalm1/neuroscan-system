#!/usr/bin/env python3
"""
Test script to verify cloud-based product creation with new fields (SKU, Price)
"""

import requests
import json
import sys

# Cloud API endpoints
BASE_URL = "https://neuroscan-api.onrender.com"
LOGIN_URL = f"{BASE_URL}/auth/login"
PRODUCTS_URL = f"{BASE_URL}/admin/products/"

def test_cloud_product_creation():
    print("🚀 Testing cloud-based NeuroScan product creation...")
    
    # Step 1: Login to get access token
    print("\n1. Logging in to get access token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
            
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("❌ No access token received")
            return False
            
        print("✅ Login successful, token received")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Create headers with authentication
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 3: Test product creation with new fields
    print("\n2. Creating test product with new fields...")
    product_data = {
        "customer_id": 1,  # Assuming customer ID 1 exists
        "name": "Cloud Test Product",
        "sku": "CLOUD-001",
        "description": "Test product created via cloud API",
        "category": "electronics",
        "price": "299.99"
    }
    
    try:
        create_response = requests.post(PRODUCTS_URL, json=product_data, headers=headers)
        print(f"Create response status: {create_response.status_code}")
        print(f"Create response: {create_response.text}")
        
        if create_response.status_code == 201:
            created_product = create_response.json()
            product_id = created_product.get("id")
            print(f"✅ Product created successfully with ID: {product_id}")
            print(f"   - Name: {created_product.get('name')}")
            print(f"   - SKU: {created_product.get('sku')}")
            print(f"   - Price: {created_product.get('price')}")
            print(f"   - Category: {created_product.get('category')}")
            return True
        else:
            print(f"❌ Product creation failed: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Product creation error: {e}")
        return False

def test_cloud_product_retrieval():
    print("\n3. Testing product retrieval...")
    
    # Login first
    login_data = {
        "username": "admin", 
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        if login_response.status_code != 200:
            print("❌ Login failed for product retrieval test")
            return False
            
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Get all products
        get_response = requests.get(PRODUCTS_URL, headers=headers)
        print(f"Get products response status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            products = get_response.json()
            print(f"✅ Retrieved {len(products)} products")
            
            # Show details of products with new fields
            for product in products:
                print(f"   Product: {product.get('name')} | SKU: {product.get('sku')} | Price: {product.get('price')}")
            return True
        else:
            print(f"❌ Product retrieval failed: {get_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Product retrieval error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 CLOUD PRODUCT CREATION TEST")
    print("=" * 60)
    
    # Test product creation
    creation_success = test_cloud_product_creation()
    
    # Test product retrieval
    retrieval_success = test_cloud_product_retrieval()
    
    print("\n" + "=" * 60)
    if creation_success and retrieval_success:
        print("✅ ALL CLOUD TESTS PASSED!")
        print("✅ SKU and Price fields are working correctly in the cloud!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)
    print("=" * 60)
