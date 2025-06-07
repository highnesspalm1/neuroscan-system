#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced NeuroScan Cloud System Tests
Comprehensive testing with frontend validation
"""

import requests
import json
import time
from datetime import datetime

# Cloud URLs
BACKEND_URL = "https://neuroscan-api.onrender.com"
FRONTEND_URL = "https://neuroscan-system.vercel.app"

def test_backend_advanced():
    """Test backend with detailed analysis"""
    print("🔧 Testing Backend API...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{BACKEND_URL}/health", timeout=15)
        print(f"   Health Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Environment: {data.get('environment')}")
            print(f"   API Version: {data.get('api_version')}")
            
        # Test API docs
        docs_response = requests.get(f"{BACKEND_URL}/docs", timeout=15)
        print(f"   API Docs: {docs_response.status_code}")
        
        # Test root endpoint
        root_response = requests.get(f"{BACKEND_URL}/", timeout=15)
        print(f"   Root Endpoint: {root_response.status_code}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ Backend Error: {e}")
        return False

def test_frontend_advanced():
    """Test frontend with detailed analysis"""
    print("🌐 Testing Frontend Application...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=15)
        print(f"   Frontend Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            # Check for common Vue.js indicators
            if "vue" in content.lower() or "vite" in content.lower():
                print("   ✅ Vue.js application detected")
            else:
                print("   ⚠️  Vue.js indicators not found")
                
            print(f"   Content Length: {len(content)} bytes")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ Frontend Error: {e}")
        return False

def test_cors_advanced():
    """Test CORS with multiple origins"""
    print("🔗 Testing CORS Configuration...")
    
    test_origins = [
        "https://neuroscan-system.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    cors_working = False
    
    for origin in test_origins:
        try:
            response = requests.get(
                f"{BACKEND_URL}/health",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Content-Type"
                },
                timeout=10
            )
            
            cors_header = response.headers.get("Access-Control-Allow-Origin")
            if cors_header:
                print(f"   ✅ CORS working for: {origin}")
                cors_working = True
            else:
                print(f"   ⚠️  CORS not configured for: {origin}")
                
        except Exception as e:
            print(f"   ❌ CORS test failed for {origin}: {e}")
    
    return cors_working

def run_enhanced_tests():
    """Run comprehensive enhanced tests"""
    print("🧪 NeuroScan Enhanced Cloud System Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test Backend
    if test_backend_advanced():
        tests_passed += 1
        print("   ✅ Backend: PASS")
    else:
        print("   ❌ Backend: FAIL")
    
    print()
    
    # Test Frontend  
    if test_frontend_advanced():
        tests_passed += 1
        print("   ✅ Frontend: PASS")
    else:
        print("   ❌ Frontend: FAIL")
    
    print()
    
    # Test CORS
    if test_cors_advanced():
        tests_passed += 1
        print("   ✅ CORS: PASS")
    else:
        print("   ❌ CORS: FAIL")
    
    print("\n" + "=" * 50)
    print(f"🎯 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
    elif tests_passed >= 2:
        print("⚠️  System mostly working - minor issues")
    else:
        print("❌ Major issues detected")
    
    return tests_passed, total_tests

if __name__ == "__main__":
    run_enhanced_tests()
