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
CUSTOMERS_URL = f"{BASE_URL}/admin/customers/"
PRODUCTS_URL = f"{BASE_URL}/admin/products/"

def get_auth_headers():
    """Get authentication headers by logging in"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return None
            
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("❌ No access token received")
            return None
            
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_product_creation_with_sku_price():
    print("🚀 Testing cloud product creation with SKU and Price fields...")
    
    # Get auth headers
    headers = get_auth_headers()
    if not headers:
        return False
    
    print("✅ Authentication successful")
    
    # Create a customer first
    print("\n📋 Creating test customer...")
    customer_data = {
        "name": "SKU Test Customer",
        "email": "skutest@example.com",
        "phone": "+1234567890",
        "address": "456 SKU Test Street"
    }
    
    customer_response = requests.post(CUSTOMERS_URL, json=customer_data, headers=headers)
    print(f"Customer creation status: {customer_response.status_code}")
    
    if customer_response.status_code in [200, 201]:
        customer = customer_response.json()
        customer_id = customer.get("id")
        print(f"✅ Customer created/found with ID: {customer_id}")
    else:
        # Try to get existing customers
        get_response = requests.get(CUSTOMERS_URL, headers=headers)
        if get_response.status_code == 200:
            customers = get_response.json()
            if customers:
                customer_id = customers[0].get("id")
                print(f"✅ Using existing customer with ID: {customer_id}")
            else:
                print("❌ No customers available")
                return False
        else:
            print("❌ Could not get customers")
            return False
    
    # Test product creation with ALL fields including SKU and Price
    print("\n🛍️ Creating product with SKU and Price...")
    product_data = {
        "customer_id": customer_id,
        "name": "SKU Price Test Product",
        "sku": "TEST-SKU-001",
        "description": "Product with SKU and Price fields",
        "category": "electronics",
        "price": "199.99"
    }
    
    print(f"Sending product data: {json.dumps(product_data, indent=2)}")
    
    product_response = requests.post(PRODUCTS_URL, json=product_data, headers=headers)
    print(f"Product creation status: {product_response.status_code}")
    print(f"Product response: {product_response.text}")
    
    if product_response.status_code in [200, 201]:
        product = product_response.json()
        print(f"✅ Product created with ID: {product.get('id')}")
        print(f"   📝 Name: {product.get('name')}")
        print(f"   🏷️ SKU: {product.get('sku', 'MISSING!')}")
        print(f"   💰 Price: {product.get('price', 'MISSING!')}")
        print(f"   📂 Category: {product.get('category', 'MISSING!')}")
        
        # Check if new fields are properly saved
        if product.get('sku') and product.get('price'):
            print("✅ SKU and Price fields are working correctly!")
            return True
        else:
            print("⚠️  WARNING: SKU or Price fields are missing!")
            print("⚠️  Backend schema may need updates")
            return False
    else:
        print(f"❌ Product creation failed: {product_response.text}")
        return False

def test_product_retrieval():
    print("\n📥 Testing product retrieval with new fields...")
    
    headers = get_auth_headers()
    if not headers:
        return False
    
    # Get all products
    response = requests.get(PRODUCTS_URL, headers=headers)
    print(f"Product retrieval status: {response.status_code}")
    
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Retrieved {len(products)} products")
        
        for i, product in enumerate(products, 1):
            print(f"   {i}. {product.get('name')} | SKU: {product.get('sku', 'None')} | Price: {product.get('price', 'None')}")
        
        return True
    else:
        print(f"❌ Product retrieval failed: {response.text}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 CLOUD SKU & PRICE FIELD TEST")
    print("=" * 70)
    
    # Test product creation with new fields
    creation_success = test_product_creation_with_sku_price()
    
    # Test product retrieval
    retrieval_success = test_product_retrieval()
    
    print("\n" + "=" * 70)
    if creation_success and retrieval_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ SKU and Price fields are working correctly in the cloud!")
        print("✅ Product creation and retrieval functionality verified")
    else:
        print("❌ Some tests failed")
        print("🔧 Backend schema updates may be needed")
        sys.exit(1)
    print("=" * 70)
