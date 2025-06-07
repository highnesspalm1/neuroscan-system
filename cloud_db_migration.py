#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Database Migration Script
Checks and updates the cloud backend database schema
"""

import requests
import json
from datetime import datetime

# Cloud backend configuration
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
        data=ADMIN_CREDENTIALS
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Authentication successful")
        return token_data["access_token"]
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def check_database_schema(token):
    """Check current database schema by examining a product"""
    print("\n📋 Checking current database schema...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get existing products to check schema
    response = requests.get(f"{BACKEND_URL}/admin/products", headers=headers)
    
    if response.status_code == 200:
        products = response.json()
        if products:
            product = products[0]
            print(f"✅ Retrieved {len(products)} products")
            print(f"📝 Sample product fields: {list(product.keys())}")
            
            # Check for new fields
            has_sku = 'sku' in product
            has_price = 'price' in product
            has_category = 'category' in product
            has_updated_at = 'updated_at' in product
            
            print(f"🏷️ SKU field present: {has_sku}")
            print(f"💰 Price field present: {has_price}")
            print(f"📂 Category field present: {has_category}")
            print(f"🕒 Updated_at field present: {has_updated_at}")
            
            return {
                'has_products': True,
                'has_sku': has_sku,
                'has_price': has_price,
                'has_category': has_category,
                'has_updated_at': has_updated_at,
                'sample_product': product
            }
        else:
            print("⚠️ No products found to check schema")
            return {'has_products': False}
    else:
        print(f"❌ Failed to retrieve products: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_schema_migration(token):
    """Test if the backend properly handles new fields"""
    print("\n🧪 Testing schema migration...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test customer first
    print("👤 Creating test customer...")
    customer_data = {
        "name": "Schema Test Customer",
        "email": "schematest@example.com"
    }
    
    response = requests.post(f"{BACKEND_URL}/admin/customers", 
                           headers=headers, 
                           json=customer_data)
    
    if response.status_code == 200:
        customer = response.json()
        customer_id = customer["id"]
        print(f"✅ Customer created with ID: {customer_id}")
    else:
        print(f"❌ Customer creation failed: {response.status_code}")
        return False
    
    # Test product creation with all new fields
    print("🛍️ Creating product with all new fields...")
    product_data = {
        "customer_id": customer_id,
        "name": "Schema Migration Test Product",
        "sku": "SCHEMA-TEST-001",
        "description": "Testing schema migration for new fields",
        "category": "testing",
        "price": "99.99"
    }
    
    print(f"📤 Sending product data: {json.dumps(product_data, indent=2)}")
    
    response = requests.post(f"{BACKEND_URL}/admin/products",
                           headers=headers,
                           json=product_data)
    
    print(f"📥 Response status: {response.status_code}")
    
    if response.status_code == 200:
        product = response.json()
        print(f"✅ Product created with ID: {product['id']}")
        print(f"📝 Product response: {json.dumps(product, indent=2)}")
        
        # Check if new fields are present
        sku_saved = product.get('sku') == product_data['sku']
        price_saved = product.get('price') == product_data['price']
        category_saved = product.get('category') == product_data['category']
        
        print(f"\n🔍 Field verification:")
        print(f"   SKU saved correctly: {sku_saved} ({product.get('sku', 'MISSING')})")
        print(f"   Price saved correctly: {price_saved} ({product.get('price', 'MISSING')})")
        print(f"   Category saved correctly: {category_saved} ({product.get('category', 'MISSING')})")
        
        if sku_saved and price_saved and category_saved:
            print("✅ All new fields are working correctly!")
            return True
        else:
            print("⚠️ Some fields are not being saved correctly")
            return False
    else:
        print(f"❌ Product creation failed: {response.status_code}")
        print(f"Error response: {response.text}")
        return False

def main():
    """Main migration check function"""
    print("=" * 60)
    print("🛠️ CLOUD DATABASE SCHEMA MIGRATION CHECK")
    print("=" * 60)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Migration check failed - cannot authenticate")
        exit(1)
    
    # Check current database schema
    schema_info = check_database_schema(token)
    if not schema_info:
        print("❌ Migration check failed - cannot check schema")
        exit(1)
    
    # Test schema migration
    migration_success = test_schema_migration(token)
    
    print("\n" + "=" * 60)
    if migration_success:
        print("✅ DATABASE SCHEMA MIGRATION SUCCESSFUL")
        print("🎉 All new fields (SKU, Price, Category) are working correctly!")
    else:
        print("❌ DATABASE SCHEMA MIGRATION NEEDED")
        print("🔧 Backend database needs to be updated with new columns")
        print("\n📋 REQUIRED ACTIONS:")
        print("   1. Connect to the cloud database")
        print("   2. Add missing columns to products table:")
        print("      - ALTER TABLE products ADD COLUMN sku VARCHAR;")
        print("      - ALTER TABLE products ADD COLUMN category VARCHAR;") 
        print("      - ALTER TABLE products ADD COLUMN price VARCHAR;")
        print("      - ALTER TABLE products ADD COLUMN updated_at TIMESTAMP;")
        print("   3. Restart the backend service if needed")
    print("=" * 60)

if __name__ == "__main__":
    main()
