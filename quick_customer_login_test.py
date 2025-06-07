#!/usr/bin/env python3
"""
Quick test of customer authentication
"""

import requests
import json

API_URL = "https://neuroscan-api.onrender.com"

def test_customer_login():
    """Test customer login functionality"""
    print("🔐 Testing Customer Login...")
    
    try:        # Test health first
        print("Testing health endpoint...")
        health_response = requests.get(f"{API_URL}/health", timeout=10)
        print(f"✅ Health check: {health_response.status_code}")
        
        # Test customer login
        login_data = {
            "username": "testcustomer",
            "password": "password123"
        }
        
        print("🧪 Attempting customer login...")
        response = requests.post(
            f"{API_URL}/customer/login",
            json=login_data,
            timeout=15
        )
        
        print(f"📊 Login Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"🔑 Access token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"👤 Customer: {data.get('customer', {}).get('name', 'N/A')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            if response.text:
                try:
                    error_data = response.json()
                    print(f"📄 Error details: {error_data}")
                except:
                    print(f"📄 Raw error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_customer_login()
