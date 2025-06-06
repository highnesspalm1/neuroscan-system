#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Frontend-Backend Integration Test
"""

import requests
import json

def test_integration():
    """Test frontend-backend integration"""
    
    print("🔗 Testing Frontend-Backend Integration...")
    print("=" * 50)
    
    # Test Backend Health
    try:
        backend_response = requests.get("https://neuroscan-api.onrender.com/health", timeout=10)
        print(f"✅ Backend Status: {backend_response.status_code}")
        
        if backend_response.status_code == 200:
            data = backend_response.json()
            print(f"   Database: {data.get('database')}")
            print(f"   Environment: {data.get('environment')}")
            print(f"   API Version: {data.get('api_version')}")
    except Exception as e:
        print(f"❌ Backend Error: {e}")
    
    print()
    
    # Test Frontend
    try:
        frontend_response = requests.get("https://neuroscan-system.vercel.app", timeout=10)
        print(f"Frontend Status: {frontend_response.status_code}")
        
        if frontend_response.status_code == 200:
            print("✅ Frontend: Accessible")
            
            # Check if it's a proper HTML response
            content = frontend_response.text
            if "<html" in content.lower():
                print("✅ Valid HTML response")
            else:
                print("⚠️  Non-HTML response")
                
        elif frontend_response.status_code == 404:
            print("❌ Frontend: 404 Not Found")
            print("   This could indicate Vercel deployment issues")
        else:
            print(f"⚠️  Frontend: HTTP {frontend_response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
    
    print()
    
    # Test CORS specifically for the production URLs
    try:
        cors_response = requests.get(
            "https://neuroscan-api.onrender.com/health",
            headers={"Origin": "https://neuroscan-system.vercel.app"},
            timeout=10
        )
        
        cors_header = cors_response.headers.get("Access-Control-Allow-Origin")
        if cors_header:
            print(f"✅ CORS: Working - {cors_header}")
        else:
            print("❌ CORS: No headers found")
            print("   Backend needs CORS configuration update")
            
    except Exception as e:
        print(f"❌ CORS Test Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Integration Test Complete")

if __name__ == "__main__":
    test_integration()
