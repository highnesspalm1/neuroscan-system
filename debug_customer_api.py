#!/usr/bin/env python3
"""
Debug frontend API configuration and test customer login directly
"""

import requests
import json
import time

def test_api_endpoints():
    """Test API endpoints that the frontend uses"""
    
    print("🔍 DEBUGGING CUSTOMER PORTAL API ISSUES")
    print("=" * 60)
    
    base_url = "https://neuroscan-api.onrender.com"
    
    # Test 1: Health check
    print("\n1️⃣ Testing API Health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=15)
        print(f"   ✅ Health: {response.status_code}")
        if response.status_code == 200:
            print(f"   📄 Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Customer login endpoint  
    print("\n2️⃣ Testing Customer Login...")
    login_data = {
        "username": "testcustomer", 
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/customer/login",
            json=login_data,
            timeout=20,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   📊 Status: {response.status_code}")
        print(f"   📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login successful!")
            print(f"   🔑 Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   👤 Customer: {data.get('customer', {}).get('name', 'N/A')}")
            
            # Test authenticated endpoint
            print("\n3️⃣ Testing Authenticated Endpoint...")
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            me_response = requests.get(f"{base_url}/customer/me", headers=headers, timeout=15)
            print(f"   📊 /customer/me: {me_response.status_code}")
            
            return True
        else:
            print(f"   ❌ Login failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login request failed: {e}")
        return False

def test_frontend_api_config():
    """Test what the frontend might be trying to access"""
    print("\n4️⃣ Testing Frontend API Configuration...")
    
    # Test if frontend might be hitting localhost
    local_urls = [
        "http://localhost:8000/health",
        "http://127.0.0.1:8000/health"
    ]
    
    for url in local_urls:
        try:
            response = requests.get(url, timeout=2)
            print(f"   ⚠️ {url}: {response.status_code} (Frontend might be hitting this!)")
        except:
            print(f"   ✅ {url}: Not accessible (good)")

def check_cors_headers():
    """Check CORS headers on the API"""
    print("\n5️⃣ Checking CORS Headers...")
    
    try:
        response = requests.options(
            "https://neuroscan-api.onrender.com/customer/login",
            headers={
                "Origin": "https://neuroscan-system.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        print(f"   📊 OPTIONS Status: {response.status_code}")
        print(f"   🔗 CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"      {header}: {value}")
                
    except Exception as e:
        print(f"   ❌ CORS check failed: {e}")

if __name__ == "__main__":
    success = test_api_endpoints()
    test_frontend_api_config()
    check_cors_headers()
    
    if success:
        print("\n✅ API is working correctly!")
        print("🔍 Issue is likely in frontend configuration or network.")
        print("\n💡 Possible solutions:")
        print("   1. Check browser console for errors")
        print("   2. Verify API URL in production build")
        print("   3. Check if Vercel environment variables are set")
        print("   4. Try hard refresh (Ctrl+F5) to clear cache")
    else:
        print("\n❌ API has issues that need to be resolved.")
