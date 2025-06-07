#!/usr/bin/env python3
"""
Cloud Database Migration for Customer Authentication
Adds customer authentication fields to the cloud database
"""

import requests
import json
import time

# Cloud API configuration
CLOUD_API_URL = "https://neuroscan-api.onrender.com"
ADMIN_EMAIL = "admin@neuroscan.com"
ADMIN_PASSWORD = "admin123"

def authenticate():
    """Authenticate with cloud API to get admin token"""
    try:
        response = requests.post(f"{CLOUD_API_URL}/admin/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def execute_cloud_migration(token):
    """Execute customer authentication migration on cloud database"""
    headers = {"Authorization": f"Bearer {token}"}
    
    migration_sql = """
    -- Add customer authentication fields
    ALTER TABLE customers ADD COLUMN IF NOT EXISTS username VARCHAR(255) UNIQUE;
    ALTER TABLE customers ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);
    ALTER TABLE customers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
    ALTER TABLE customers ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_customers_username ON customers(username);
    CREATE INDEX IF NOT EXISTS idx_customers_active ON customers(is_active);
    
    -- Update existing customers to have default authentication
    UPDATE customers SET is_active = TRUE WHERE is_active IS NULL;
    
    -- Add sample admin customer for testing
    INSERT INTO customers (name, email, username, hashed_password, is_active, created_at) 
    VALUES (
        'Test Customer Company', 
        'test@customer.com', 
        'testcustomer',
        '$2b$12$LQv3c1yqBwlFW.zMjY8L6OeXWHmF3C1FG2FWJk3LG4CQ8Z5C1FG2F',  -- password123
        TRUE,
        NOW()
    ) 
    ON CONFLICT (email) DO UPDATE SET 
        username = EXCLUDED.username,
        hashed_password = EXCLUDED.hashed_password,
        is_active = EXCLUDED.is_active;
    """
    
    try:
        # Try to execute migration via database endpoint if available
        response = requests.post(f"{CLOUD_API_URL}/admin/database/migrate", 
                               headers=headers,
                               json={"sql": migration_sql})
        
        if response.status_code == 200:
            print("✅ Cloud database migration executed successfully")
            return True
        else:
            print(f"⚠ Migration endpoint response: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Migration execution error: {e}")
        return False

def test_customer_authentication():
    """Test if customer authentication is working"""
    try:
        response = requests.post(f"{CLOUD_API_URL}/customer/login", json={
            "username": "testcustomer",
            "password": "password123"
        })
        
        if response.status_code == 200:
            print("✅ Customer authentication test successful!")
            data = response.json()
            print(f"   Customer: {data.get('customer', {}).get('name')}")
            print(f"   Token: {data.get('access_token', '')[:20]}...")
            return True
        else:
            print(f"❌ Customer authentication test failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Customer authentication test error: {e}")
        return False

def main():
    print("🔐 NEUROSCAN CUSTOMER AUTHENTICATION MIGRATION")
    print("=" * 60)
    print("Purpose: Add customer authentication fields to cloud database")
    print("=" * 60)
    
    # Step 1: Authenticate
    print("\n🔑 Authenticating with cloud API...")
    token = authenticate()
    if not token:
        print("❌ Failed to authenticate. Please check admin credentials.")
        return
    
    print("✅ Authentication successful")
    
    # Step 2: Execute migration
    print("\n🛠️ Executing customer authentication migration...")
    migration_success = execute_cloud_migration(token)
    
    # Step 3: Wait for migration to complete
    if migration_success:
        print("\n⏳ Waiting for migration to complete...")
        time.sleep(10)
    
    # Step 4: Test customer authentication
    print("\n🧪 Testing customer authentication...")
    auth_success = test_customer_authentication()
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("📋 MIGRATION SUMMARY")
    print("=" * 60)
    
    if migration_success and auth_success:
        print("✅ Customer authentication migration completed successfully!")
        print("📱 Customer Portal is now available at:")
        print(f"   🌐 https://neuroscan-system.vercel.app/customer/login")
        print(f"   👤 Test credentials: testcustomer / password123")
    else:
        print("⚠ Migration may have encountered issues.")
        print("📋 Manual steps may be required:")
        print("1. Connect to cloud database directly")
        print("2. Execute the SQL commands manually")
        print("3. Restart the backend service")
    
    print("\n🔗 Next steps:")
    print("1. Test customer login via frontend")
    print("2. Verify all customer portal features")
    print("3. Create additional test customers as needed")

if __name__ == "__main__":
    main()
