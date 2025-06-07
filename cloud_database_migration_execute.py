#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Script for Cloud Backend
Adds SKU, Category, Price, and Updated_at columns to products table
"""

import requests
import json
import sys
from datetime import datetime

# Cloud backend configuration
BACKEND_URL = "https://neuroscan-api.onrender.com"
ADMIN_CREDENTIALS = {
    "username": "admin", 
    "password": "admin123"
}

def get_auth_token():
    """Get authentication token from cloud backend"""
    print("🔐 Authenticating with cloud backend...")
    
    try:
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
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def create_migration_endpoint(token):
    """Create a database migration through the backend API"""
    print("\n🛠️ Initiating database schema migration...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, let's try to call a migration endpoint if it exists
    migration_data = {
        "migration_type": "add_product_fields",
        "fields": ["sku", "category", "price", "updated_at"],
        "table": "products"
    }
    
    # Try to call migration endpoint
    try:
        response = requests.post(
            f"{BACKEND_URL}/admin/migrate", 
            headers=headers,
            json=migration_data,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Migration endpoint executed successfully")
            return True
        elif response.status_code == 404:
            print("⚠️ Migration endpoint not found, will use alternative method")
            return False
        else:
            print(f"❌ Migration endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ Migration endpoint error: {e}")
        return False

def trigger_schema_recreation(token):
    """Trigger schema recreation by calling a database init endpoint"""
    print("\n🔄 Attempting to trigger schema recreation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to call database initialization endpoint
    try:
        response = requests.post(
            f"{BACKEND_URL}/admin/init-db",
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Database initialization triggered successfully")
            return True
        elif response.status_code == 404:
            print("⚠️ Database init endpoint not found")
            return False
        else:
            print(f"❌ Database initialization failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ Database init error: {e}")
        return False

def create_migration_sql_file():
    """Create SQL migration file that can be manually executed"""
    print("\n📝 Creating SQL migration file...")
    
    sql_migration = """-- Database Migration: Add new fields to products table
-- Date: {date}
-- Purpose: Add SKU, Category, Price, and Updated_at fields

-- Add new columns to products table
ALTER TABLE products ADD COLUMN IF NOT EXISTS sku VARCHAR(255);
ALTER TABLE products ADD COLUMN IF NOT EXISTS category VARCHAR(255);
ALTER TABLE products ADD COLUMN IF NOT EXISTS price VARCHAR(50);
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Update existing products with default updated_at
UPDATE products SET updated_at = created_at WHERE updated_at IS NULL;

-- Verification query
SELECT 
    column_name, 
    data_type, 
    is_nullable 
FROM information_schema.columns 
WHERE table_name = 'products' 
ORDER BY ordinal_position;
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        with open("cloud_database_migration.sql", "w", encoding="utf-8") as f:
            f.write(sql_migration)
        print("✅ SQL migration file created: cloud_database_migration.sql")
        return True
    except Exception as e:
        print(f"❌ Failed to create SQL file: {e}")
        return False

def verify_migration(token):
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration success...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test customer
    customer_data = {
        "name": "Migration Test Customer",
        "email": "migrationtest@example.com"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/admin/customers",
            headers=headers,
            json=customer_data,
            timeout=30
        )
        
        if response.status_code == 200:
            customer = response.json()
            customer_id = customer["id"]
            print(f"✅ Test customer created: ID {customer_id}")
        else:
            print(f"❌ Failed to create test customer: {response.status_code}")
            return False
        
        # Test product creation with new fields
        product_data = {
            "customer_id": customer_id,
            "name": "Migration Verification Product",
            "sku": "MIGRATE-VERIFY-001",
            "description": "Product to verify migration success",
            "category": "verification",
            "price": "123.45"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/admin/products",
            headers=headers,
            json=product_data,
            timeout=30
        )
        
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Test product created: ID {product['id']}")
            
            # Check if new fields are present
            sku_present = 'sku' in product and product['sku'] == product_data['sku']
            price_present = 'price' in product and product['price'] == product_data['price']
            category_present = 'category' in product and product['category'] == product_data['category']
            
            print(f"📋 Field verification:")
            print(f"   SKU: {sku_present} ({product.get('sku', 'MISSING')})")
            print(f"   Price: {price_present} ({product.get('price', 'MISSING')})")
            print(f"   Category: {category_present} ({product.get('category', 'MISSING')})")
            
            if sku_present and price_present and category_present:
                print("🎉 Migration verification SUCCESSFUL!")
                return True
            else:
                print("⚠️ Migration verification FAILED - fields not saved")
                return False
        else:
            print(f"❌ Failed to create test product: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def show_manual_instructions():
    """Show manual migration instructions"""
    print("\n" + "="*70)
    print("📋 MANUAL DATABASE MIGRATION INSTRUCTIONS")
    print("="*70)
    print("\nIf the automatic migration failed, follow these steps:")
    print("\n1. 🔗 Connect to your cloud database (PostgreSQL/SQLite)")
    print("   - For Render.com: Use the database connection string from dashboard")
    print("   - For Railway/Heroku: Use their database CLI tools")
    print("\n2. 📝 Execute the following SQL commands:")
    print("\n   ALTER TABLE products ADD COLUMN IF NOT EXISTS sku VARCHAR(255);")
    print("   ALTER TABLE products ADD COLUMN IF NOT EXISTS category VARCHAR(255);")
    print("   ALTER TABLE products ADD COLUMN IF NOT EXISTS price VARCHAR(50);")
    print("   ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;")
    print("\n   -- Create indexes for performance")
    print("   CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);")
    print("   CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);")
    print("\n   -- Update existing records")
    print("   UPDATE products SET updated_at = created_at WHERE updated_at IS NULL;")
    print("\n3. 🔄 Restart your backend service")
    print("   - This ensures the application picks up the new schema")
    print("\n4. ✅ Run the verification test again")
    print("\n📄 A complete SQL file has been saved as: cloud_database_migration.sql")
    print("="*70)

def main():
    """Main migration function"""
    print("🛠️ NEUROSCAN CLOUD DATABASE MIGRATION")
    print("="*60)
    print("Purpose: Add SKU, Category, Price, and Updated_at fields to products table")
    print("="*60)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Migration failed - cannot authenticate")
        sys.exit(1)
    
    # Try automatic migration methods
    migration_success = False
    
    # Method 1: Try migration endpoint
    if create_migration_endpoint(token):
        migration_success = True
    
    # Method 2: Try database initialization endpoint
    if not migration_success and trigger_schema_recreation(token):
        migration_success = True
    
    # Always create SQL file for manual execution
    create_migration_sql_file()
    
    # Verify migration
    if migration_success:
        print("\n⏳ Waiting for migration to complete...")
        import time
        time.sleep(5)  # Give the database time to update
        
        if verify_migration(token):
            print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("✅ All new fields are working correctly in the cloud backend.")
        else:
            print("\n⚠️ Automatic migration may have failed.")
            show_manual_instructions()
    else:
        print("\n⚠️ Automatic migration endpoints not available.")
        show_manual_instructions()
    
    print("\n" + "="*60)
    print("🔚 MIGRATION PROCESS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
