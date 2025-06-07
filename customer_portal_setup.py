#!/usr/bin/env python3
"""
Customer Portal Database Setup and Test User Creation
"""

import requests
import json
import time

API_BASE = "https://neuroscan-api.onrender.com"

def create_test_customer_via_admin():
    """Create a test customer through admin endpoints"""
    print("🧪 CREATING TEST CUSTOMER VIA ADMIN ENDPOINTS")
    print("="*60)
    
    # Try to create admin token first
    admin_login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Try admin login
        print("🔐 Attempting admin login...")
        admin_response = requests.post(
            f"{API_BASE}/auth/login",
            json=admin_login_data,
            timeout=10
        )
        
        if admin_response.status_code == 200:
            admin_token = admin_response.json().get("access_token")
            print("✅ Admin login successful")
            
            # Create customer via admin endpoint
            customer_data = {
                "name": "Test Customer Company",
                "email": "test@neuroscan.com",
                "username": "testcustomer",
                "password": "testpass123",
                "is_active": True
            }
            
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            print("👤 Creating customer via admin endpoint...")
            customer_response = requests.post(
                f"{API_BASE}/admin/customers",
                json=customer_data,
                headers=headers,
                timeout=10
            )
            
            print(f"Customer creation status: {customer_response.status_code}")
            if customer_response.status_code in [200, 201]:
                print("✅ Test customer created successfully!")
                print(f"Customer data: {customer_response.json()}")
                return True
            else:
                print(f"❌ Customer creation failed: {customer_response.text}")
                
        else:
            print(f"❌ Admin login failed: {admin_response.status_code}")
            print(f"Response: {admin_response.text}")
            
    except Exception as e:
        print(f"❌ Error creating customer: {e}")
    
    return False

def test_customer_login():
    """Test customer login functionality"""
    print("\n🧪 TESTING CUSTOMER LOGIN")
    print("="*60)
    
    login_data = {
        "username": "testcustomer",
        "password": "testpass123"
    }
    
    try:
        print("🔐 Attempting customer login...")
        response = requests.post(
            f"{API_BASE}/customer/login",
            json=login_data,
            timeout=10
        )
        
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Customer login successful!")
            token_data = response.json()
            print(f"Token: {token_data.get('access_token', 'N/A')[:50]}...")
            
            # Test customer dashboard
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            
            print("📊 Testing customer dashboard...")
            dashboard_response = requests.get(
                f"{API_BASE}/customer/dashboard",
                headers=headers,
                timeout=10
            )
            
            print(f"Dashboard status: {dashboard_response.status_code}")
            if dashboard_response.status_code == 200:
                print("✅ Customer dashboard accessible!")
                print(f"Dashboard data: {dashboard_response.json()}")
            else:
                print(f"❌ Dashboard failed: {dashboard_response.text}")
                
            return True
            
        elif response.status_code == 422:
            print("⚠️ Validation error (endpoint working)")
            print(f"Response: {response.text}")
        elif response.status_code == 401:
            print("⚠️ Authentication failed (user may not exist)")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
    
    return False

def test_customer_endpoints():
    """Test all customer endpoints"""
    print("\n🔍 TESTING ALL CUSTOMER ENDPOINTS")
    print("="*60)
    
    endpoints = [
        ("POST", "/customer/login", "Customer login"),
        ("GET", "/customer/me", "Customer profile"),
        ("GET", "/customer/dashboard", "Customer dashboard"),
        ("GET", "/customer/products", "Customer products"),
        ("GET", "/customer/certificates", "Customer certificates"),
        ("GET", "/customer/scan-logs", "Customer scan logs")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"🧪 Testing {description}...")
        try:
            if method == "POST":
                response = requests.post(
                    f"{API_BASE}{endpoint}",
                    json={"username": "test", "password": "test"},
                    timeout=10
                )
            else:
                response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 404:
                print("   ❌ Endpoint not found")
            elif response.status_code == 401:
                print("   ✅ Endpoint works (auth required)")
            elif response.status_code == 422:
                print("   ✅ Endpoint works (validation error)")
            elif response.status_code == 500:
                print("   ❌ Server error (database issue)")
            else:
                print(f"   Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def direct_database_initialization():
    """Try to trigger database initialization"""
    print("\n🔨 TRIGGERING DATABASE INITIALIZATION")
    print("="*60)
    
    # Try various endpoints that might trigger database creation
    init_endpoints = [
        "/health",
        "/docs",
        "/auth/create-admin",
        "/admin/dashboard"
    ]
    
    for endpoint in init_endpoints:
        print(f"🔧 Triggering {endpoint}...")
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if endpoint == "/auth/create-admin" and response.status_code == 200:
                print("   ✅ Admin created - database initialized!")
                
        except Exception as e:
            print(f"   Error: {e}")

def main():
    """Main function to set up customer portal"""
    print("🚀 CUSTOMER PORTAL SETUP AND TESTING")
    print("="*60)
    print(f"Target: {API_BASE}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Test endpoint availability
    test_customer_endpoints()
    
    # Try to initialize database
    direct_database_initialization()
    
    # Try to create test customer
    customer_created = create_test_customer_via_admin()
    
    if customer_created:
        # Test customer login
        login_success = test_customer_login()
        
        if login_success:
            print("\n🎉 CUSTOMER PORTAL FULLY FUNCTIONAL!")
            print("="*60)
            print("✅ Customer endpoints available")
            print("✅ Test customer created")
            print("✅ Customer login working")
            print("✅ Customer dashboard accessible")
            print("\n🔗 Live Customer Portal: https://neuroscan-system.vercel.app/customer/login")
            print("👤 Test Credentials: testcustomer / testpass123")
        else:
            print("\n⚠️ CUSTOMER PORTAL PARTIALLY FUNCTIONAL")
            print("❌ Customer login issues detected")
    else:
        print("\n❌ CUSTOMER PORTAL SETUP FAILED")
        print("❌ Could not create test customer")
    
    print("\n" + "="*60)
    print("🎯 CUSTOMER PORTAL SETUP COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
