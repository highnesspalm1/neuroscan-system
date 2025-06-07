#!/usr/bin/env python3
"""
Test Cloud API Endpoints Availability
"""

import requests
import json

CLOUD_API_URL = "https://neuroscan-api.onrender.com"

def test_endpoint(endpoint, method="GET", data=None):
    """Test if an endpoint is available"""
    try:
        url = f"{CLOUD_API_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"  {method} {endpoint}: {response.status_code}")
        
        if response.status_code not in [404, 405]:
            return True
        return False
        
    except Exception as e:
        print(f"  {method} {endpoint}: ERROR - {e}")
        return False

def main():
    print("🔍 TESTING CLOUD API ENDPOINTS")
    print("=" * 50)
    
    endpoints_to_test = [
        # Basic endpoints
        ("/health", "GET"),
        ("/docs", "GET"),
        
        # Admin endpoints
        ("/admin/login", "POST"),
        ("/admin/dashboard", "GET"),
        
        # Customer endpoints (what we're looking for)
        ("/customer/login", "POST"),
        ("/customer/me", "GET"),
        ("/customer/dashboard", "GET"),
        
        # Verification endpoint
        ("/verify", "GET"),
        ("/api/v1/verify", "GET"),
    ]
    
    available_endpoints = []
    
    for endpoint, method in endpoints_to_test:
        if test_endpoint(endpoint, method, {"test": "data"}):
            available_endpoints.append(f"{method} {endpoint}")
    
    print("\n✅ Available endpoints:")
    for endpoint in available_endpoints:
        print(f"  • {endpoint}")
    
    print(f"\n📊 Total available: {len(available_endpoints)}/{len(endpoints_to_test)}")
    
    # Test specific customer login
    print("\n🧪 Testing customer login specifically...")
    try:
        response = requests.post(f"{CLOUD_API_URL}/customer/login", 
                               json={"username": "test", "password": "test"},
                               timeout=10)
        print(f"Customer login response: {response.status_code}")
        if response.status_code != 404:
            print(f"Response body: {response.text[:200]}...")
    except Exception as e:
        print(f"Customer login test error: {e}")

if __name__ == "__main__":
    main()
