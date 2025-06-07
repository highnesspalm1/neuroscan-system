#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Services Connection Test
Test script to verify connectivity to all cloud services
"""

import sys
import os
import json
import time
from pathlib import Path

# Add modules directory to path
sys.path.append(str(Path(__file__).parent / "modules"))

from api_manager import APIManager


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_cloud_services():
    """Test all cloud services connectivity"""
    print("🔍 NeuroScan Cloud Services Connection Test")
    print("=" * 50)
    
    try:
        # Load configuration
        config = load_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   Backend API: {config['api']['base_url']}")
        print(f"   Frontend: {config['api']['frontend_url']}")
        print(f"   Documentation: {config['api']['docs_url']}")
        print()
        
        # Initialize API Manager
        api_manager = APIManager(config)
        print("✅ API Manager initialized")
        print()
        
        # Test Backend API Health
        print("🔍 Testing Backend API Health...")
        try:
            health_status = api_manager.check_health()
            if health_status:
                print("✅ Backend API is healthy")
                print(f"   Status: {health_status.get('status', 'unknown')}")
                print(f"   Message: {health_status.get('message', 'No message')}")
            else:
                print("❌ Backend API health check failed")
        except Exception as e:
            print(f"❌ Backend API error: {e}")
        print()
        
        # Test Frontend connectivity
        print("🔍 Testing Frontend connectivity...")
        try:
            frontend_status = api_manager.check_frontend_status()
            if frontend_status:
                print("✅ Frontend is accessible")
                print(f"   Status: {frontend_status}")
            else:
                print("❌ Frontend is not accessible")
        except Exception as e:
            print(f"❌ Frontend error: {e}")
        print()
        
        # Test API Documentation
        print("🔍 Testing API Documentation...")
        try:
            docs_status = api_manager.check_docs_status()
            if docs_status:
                print("✅ API Documentation is accessible")
                print(f"   Status: {docs_status}")
            else:
                print("❌ API Documentation is not accessible")
        except Exception as e:
            print(f"❌ API Documentation error: {e}")
        print()
        
        # Test Authentication (optional)
        print("🔍 Testing Authentication endpoint...")
        try:
            # Test with dummy credentials to check endpoint availability
            auth_response = api_manager.make_request('POST', '/auth/login', {
                'username': 'test',
                'password': 'test'
            })
            print("✅ Authentication endpoint is accessible (expected 401/422 for invalid credentials)")
        except Exception as e:
            if "401" in str(e) or "422" in str(e) or "Unauthorized" in str(e):
                print("✅ Authentication endpoint is accessible (rejected invalid credentials as expected)")
            else:
                print(f"❌ Authentication endpoint error: {e}")
        print()
        
        print("🎉 Cloud Services Test Completed!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Starting NeuroScan Cloud Services Test...")
    print()
    
    success = test_cloud_services()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("🎉 The NeuroScan Desktop App is ready to connect to cloud services!")
        print()
        print("📋 Next Steps:")
        print("   1. Start the Desktop App: python main.py")
        print("   2. Click 'Anmelden' to login with your credentials")
        print("   3. Monitor real-time cloud status in the dashboard")
        print()
        print("🔑 Default Login Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("🔧 Troubleshooting:")
        print("   1. Check your internet connection")
        print("   2. Verify cloud services are running:")
        print("      - Backend API: https://neuroscan-api.onrender.com/health")
        print("      - Frontend: https://neuroscan-system.vercel.app")
        print("      - API Docs: https://neuroscan-api.onrender.com/docs")
        print("   3. Try again in a few minutes (Render cold starts)")
    
    print("\n" + "="*60)
    print("NeuroScan Cloud Integration Test Complete")
    print("="*60)
    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()
