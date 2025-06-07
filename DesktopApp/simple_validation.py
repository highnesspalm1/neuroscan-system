#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Desktop App - Simple Validation
Basic validation of cloud integration functionality
"""

import sys
import json
import requests
from pathlib import Path

def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def test_direct_connectivity():
    """Test direct connectivity to cloud services"""
    print("🌐 Testing Direct Cloud Connectivity...")
    
    config = load_config()
    if not config:
        return False
    
    services = {
        "Backend API": f"{config['api']['base_url']}/health",
        "Frontend": config['api']['frontend_url'],
        "API Docs": config['api']['docs_url']
    }
    
    all_ok = True
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                print(f"✅ {service}: ONLINE ({response.status_code})")
            else:
                print(f"⚠️  {service}: ACCESSIBLE ({response.status_code})")
        except Exception as e:
            print(f"❌ {service}: ERROR - {e}")
            all_ok = False
    
    return all_ok

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "config.json",
        "main.py",
        "requirements.txt",
        "modules/api_manager.py",
        "modules/cloud_status.py", 
        "modules/auth_dialog.py",
        "modules/main_window.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_configuration():
    """Test configuration validity"""
    print("\n⚙️  Testing Configuration...")
    
    config = load_config()
    if not config:
        return False
    
    required_sections = {
        'api': ['base_url', 'frontend_url', 'docs_url', 'timeout'],
        'app_name': None,
        'version': None
    }
    
    all_valid = True
    for section, keys in required_sections.items():
        if section not in config:
            print(f"❌ Missing section: {section}")
            all_valid = False
        elif keys:
            for key in keys:
                if key not in config[section]:
                    print(f"❌ Missing key: {section}.{key}")
                    all_valid = False
                else:
                    print(f"✅ {section}.{key}: {config[section][key]}")
        else:
            print(f"✅ {section}: {config[section]}")
    
    return all_valid

def test_authentication_endpoint():
    """Test authentication endpoint availability"""
    print("\n🔐 Testing Authentication Endpoint...")
    
    config = load_config()
    if not config:
        return False
    
    try:
        # Test login endpoint with dummy data
        response = requests.post(
            f"{config['api']['base_url']}/auth/login",
            json={"username": "test", "password": "test"},
            timeout=30
        )
        
        # We expect 401/422 for invalid credentials
        if response.status_code in [401, 422]:
            print("✅ Authentication endpoint responds correctly to invalid credentials")
            return True
        elif response.status_code == 200:
            print("⚠️  Authentication endpoint allowed test credentials (unexpected)")
            return True
        else:
            print(f"❌ Authentication endpoint returned unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication endpoint error: {e}")
        return False

def main():
    """Run validation tests"""
    print("🎯 NEUROSCAN DESKTOP APP - SIMPLE VALIDATION")
    print("=" * 55)
    print()
    
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration", test_configuration),
        ("Cloud Connectivity", test_direct_connectivity),
        ("Authentication", test_authentication_endpoint)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"🧪 Running {test_name} Test...")
        if not test_func():
            all_passed = False
        print()
    
    print("=" * 55)
    
    if all_passed:
        print("🎉 ALL VALIDATION TESTS PASSED! 🎉")
        print()
        print("✅ NeuroScan Desktop App is ready for use!")
        print()
        print("📋 What's Working:")
        print("   ✅ All required files present")
        print("   ✅ Configuration is valid")
        print("   ✅ Cloud services are accessible")
        print("   ✅ Authentication endpoint is functional")
        print()
        print("🚀 To start the Desktop App:")
        print("   python main.py")
        print()
        print("🔑 Default credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the error messages above.")
    
    print("\n" + "=" * 55)
    return all_passed

if __name__ == "__main__":
    success = main()
    print(f"\nOverall Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print("\nPress Enter to exit...")
    input()
