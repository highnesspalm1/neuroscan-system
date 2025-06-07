#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force Backend Schema Update
Attempts to force the cloud backend to update its database schema
"""

import requests
import json
import time
from datetime import datetime

# Cloud configuration
BACKEND_URL = "https://neuroscan-api.onrender.com"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

def get_auth_token():
    """Get authentication token"""
    print("🔐 Getting authentication token...")
    
    response = requests.post(
        f"{BACKEND_URL}/auth/token", 
        data=ADMIN_CREDENTIALS,
        timeout=30
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Authentication successful")
        return token_data["access_token"]
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None

def force_schema_recreation():
    """Force schema recreation by creating tables with all fields"""
    print("\n🔄 Attempting to force schema recreation...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Strategy 1: Try to create a product with all fields to force schema update
    print("\n📋 Strategy 1: Force schema update through product creation...")
    
    # Create test customer
    customer_data = {
        "name": "Force Schema Customer",
        "email": "forceschema@example.com"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin/customers", 
                               headers=headers, json=customer_data, timeout=30)
        if response.status_code == 200:
            customer = response.json()
            customer_id = customer["id"]
            print(f"✅ Test customer created: ID {customer_id}")
        else:
            print(f"❌ Customer creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Customer creation error: {e}")
        return False
    
    # Try to create product that might trigger schema update
    product_data = {
        "customer_id": customer_id,
        "name": "Schema Force Product",
        "sku": "FORCE-001",
        "description": "Product to force schema update",
        "category": "force",
        "price": "999.99"
    }
    
    print("🛍️ Creating product with all new fields...")
    try:
        response = requests.post(f"{BACKEND_URL}/admin/products",
                               headers=headers, json=product_data, timeout=30)
        
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Product created: ID {product['id']}")
            
            # Check if fields are present
            has_sku = 'sku' in product and product['sku'] is not None
            has_price = 'price' in product and product['price'] is not None
            has_category = 'category' in product and product['category'] is not None
            
            if has_sku and has_price and has_category:
                print("🎉 SUCCESS! Schema appears to be updated!")
                return True
            else:
                print(f"⚠️ Fields still missing: SKU={has_sku}, Price={has_price}, Category={has_category}")
        else:
            print(f"❌ Product creation failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Product creation error: {e}")
    
    # Strategy 2: Try to trigger backend restart through health check spam
    print("\n🔄 Strategy 2: Triggering backend activity...")
    
    for i in range(5):
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            print(f"   Health check {i+1}: {response.status_code}")
            time.sleep(2)
        except:
            pass
    
    return False

def test_web_frontend():
    """Test the web frontend to see if it's working properly"""
    print("\n🌐 Testing web frontend...")
    
    try:
        response = requests.get("https://neuroscan-system.vercel.app", timeout=30)
        if response.status_code == 200:
            print("✅ Web frontend is accessible")
            return True
        else:
            print(f"⚠️ Web frontend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web frontend error: {e}")
        return False

def run_final_verification():
    """Run final verification of the entire system"""
    print("\n🔍 Running final system verification...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test complete workflow
    print("\n1. Creating final test customer...")
    customer_data = {
        "name": "Final Test Customer",
        "email": "finaltest@example.com"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin/customers",
                               headers=headers, json=customer_data, timeout=30)
        if response.status_code == 200:
            customer = response.json()
            customer_id = customer["id"]
            print(f"✅ Customer created: {customer['name']} (ID: {customer_id})")
        else:
            print(f"❌ Customer creation failed")
            return False
    except Exception as e:
        print(f"❌ Customer creation error: {e}")
        return False
    
    print("\n2. Creating final test product...")
    product_data = {
        "customer_id": customer_id,
        "name": "Final Verification Product",
        "sku": "FINAL-VERIFY-001",
        "description": "Final product verification test",
        "category": "verification",
        "price": "199.99"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin/products",
                               headers=headers, json=product_data, timeout=30)
        
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Product created: {product['name']} (ID: {product['id']})")
            
            # Check all fields
            print(f"\n📋 Final field verification:")
            print(f"   Name: {product.get('name', 'MISSING')}")
            print(f"   SKU: {product.get('sku', 'MISSING')}")
            print(f"   Price: {product.get('price', 'MISSING')}")
            print(f"   Category: {product.get('category', 'MISSING')}")
            print(f"   Description: {product.get('description', 'MISSING')}")
            
            # Check success
            sku_ok = product.get('sku') == product_data['sku']
            price_ok = product.get('price') == product_data['price']
            category_ok = product.get('category') == product_data['category']
            
            if sku_ok and price_ok and category_ok:
                print("\n🎉 FINAL VERIFICATION SUCCESSFUL!")
                print("✅ All product fields are working correctly!")
                return True
            else:
                print(f"\n⚠️ Some fields not working:")
                print(f"   SKU: {'✅' if sku_ok else '❌'}")
                print(f"   Price: {'✅' if price_ok else '❌'}")
                print(f"   Category: {'✅' if category_ok else '❌'}")
                return False
        else:
            print(f"❌ Product creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Product creation error: {e}")
        return False

def main():
    print("🚀 NEUROSCAN SCHEMA FORCE UPDATE")
    print("="*60)
    
    # Test web frontend first
    frontend_ok = test_web_frontend()
    
    # Try to force schema update
    schema_ok = force_schema_recreation()
    
    if schema_ok:
        print("\n🎉 Schema update appears successful!")
    else:
        print("\n⚠️ Schema may still need manual update")
    
    # Run final verification
    final_ok = run_final_verification()
    
    print("\n" + "="*60)
    print("📊 FINAL STATUS SUMMARY")
    print("="*60)
    print(f"🌐 Web Frontend: {'✅ Working' if frontend_ok else '❌ Issues'}")
    print(f"🛠️ Schema Update: {'✅ Success' if schema_ok else '⚠️ Needed'}")
    print(f"🔍 Final Verification: {'✅ Passed' if final_ok else '❌ Failed'}")
    
    if final_ok:
        print("\n🎉 NEUROSCAN SYSTEM FULLY OPERATIONAL!")
        print("✅ Product creation with SKU and Price is working!")
        print("🌐 Ready for production use!")
    else:
        print("\n⚠️ Manual database migration still required")
        print("📄 Use cloud_database_migration.sql for manual update")
    
    print("="*60)

if __name__ == "__main__":
    main()
