#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test authentication system deployment
"""

import requests
import json
from datetime import datetime

def test_authentication_system():
    """Test the complete authentication system"""
    
    base_url = "https://neuroscan-api.onrender.com"
    
    print("🔐 NeuroScan Authentication System Test")
    print("=" * 50)
    
    try:
        # Test 1: Check if auth endpoints are available
        print("🧪 Testing auth endpoint availability...")
        auth_docs_response = requests.get(f"{base_url}/docs", timeout=30)
        if auth_docs_response.status_code == 200:
            print("   ✅ API documentation accessible")
        else:
            print("   ❌ API documentation not accessible")
        
        # Test 2: Test admin user creation endpoint
        print("\n🔧 Testing admin user creation...")
        create_admin_response = requests.post(f"{base_url}/auth/create-admin", timeout=30)
        
        if create_admin_response.status_code == 200:
            print("   ✅ Admin user created successfully")
        elif create_admin_response.status_code == 400:
            print("   ✅ Admin user already exists")
        else:
            print(f"   ❌ Admin creation failed: {create_admin_response.status_code}")
            print(f"   Response: {create_admin_response.text}")
        
        # Test 3: Test login with admin credentials
        print("\n🔑 Testing admin login...")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post(
            f"{base_url}/auth/login", 
            json=login_data,
            timeout=30
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("   ✅ Login successful!")
            print(f"   Token type: {login_result.get('token_type')}")
            print(f"   User: {login_result.get('user', {}).get('username')}")
            print(f"   Role: {login_result.get('user', {}).get('role')}")
            
            # Test 4: Test protected endpoint with token
            print("\n🛡️ Testing protected endpoint access...")
            token = login_result.get('access_token')
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            dashboard_response = requests.get(
                f"{base_url}/admin/dashboard",
                headers=headers,
                timeout=30
            )
            
            if dashboard_response.status_code == 200:
                print("   ✅ Protected endpoint accessible with token")
                dashboard_data = dashboard_response.json()
                print(f"   Total customers: {dashboard_data.get('total_customers', 0)}")
                print(f"   Total products: {dashboard_data.get('total_products', 0)}")
                print(f"   Total certificates: {dashboard_data.get('total_certificates', 0)}")
            else:
                print(f"   ❌ Protected endpoint failed: {dashboard_response.status_code}")
                print(f"   Response: {dashboard_response.text}")
            
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
        
        # Test 5: Test invalid login
        print("\n❌ Testing invalid login...")
        invalid_login_data = {
            "username": "admin",
            "password": "wrongpassword"
        }
        
        invalid_login_response = requests.post(
            f"{base_url}/auth/login",
            json=invalid_login_data,
            timeout=30
        )
        
        if invalid_login_response.status_code == 401:
            print("   ✅ Invalid login correctly rejected")
        else:
            print(f"   ❌ Invalid login handling failed: {invalid_login_response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎯 Authentication System Test Complete!")
        
    except requests.exceptions.Timeout:
        print("   ❌ Request timeout - backend might be sleeping")
        print("   Tip: Try again in a few minutes")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")


if __name__ == "__main__":
    test_authentication_system()
