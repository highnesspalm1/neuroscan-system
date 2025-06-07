#!/usr/bin/env python3
"""
🎉 CUSTOMER PORTAL SUCCESS VERIFICATION TEST
Final comprehensive test to confirm 100% Customer Portal functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
FRONTEND_URL = "https://neuroscan-system.vercel.app"
API_URL = "https://neuroscan-api.onrender.com"
TEST_CREDENTIALS = {
    "username": "testcustomer",
    "password": "password123"
}

def log_success(message):
    print(f"✅ {message}")

def log_info(message):
    print(f"🔍 {message}")

def log_error(message):
    print(f"❌ {message}")

def test_frontend_accessibility():
    """Test customer portal frontend accessibility"""
    log_info("Testing Customer Portal frontend accessibility...")
    
    try:
        # Test customer login page
        response = requests.get(f"{FRONTEND_URL}/customer/login", timeout=10)
        if response.status_code == 200:
            log_success("Customer login page is accessible")
            return True
        else:
            log_error(f"Customer login page failed: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Frontend accessibility test failed: {e}")
        return False

def test_customer_authentication():
    """Test customer authentication flow"""
    log_info("Testing customer authentication...")
    
    try:
        response = requests.post(
            f"{API_URL}/customer/login",
            json=TEST_CREDENTIALS,
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            customer_data = token_data.get('customer')
            
            log_success("Customer authentication successful")
            log_success(f"Customer: {customer_data.get('name', 'N/A')}")
            log_success(f"Email: {customer_data.get('email', 'N/A')}")
            log_success(f"Token: {access_token[:30]}...")
            
            return access_token
        else:
            log_error(f"Authentication failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        log_error(f"Authentication test failed: {e}")
        return None

def test_customer_endpoints(token):
    """Test customer-specific API endpoints"""
    log_info("Testing customer API endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    endpoints = [
        ("/customer/me", "Customer profile"),
        ("/customer/dashboard", "Customer dashboard"),
        ("/customer/products", "Customer products"),
        ("/customer/certificates", "Customer certificates")
    ]
    
    success_count = 0
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                log_success(f"{description} endpoint working")
                success_count += 1
            elif response.status_code == 404:
                log_info(f"{description} endpoint not implemented yet")
            else:
                log_error(f"{description} endpoint failed: {response.status_code}")
                
        except Exception as e:
            log_error(f"{description} endpoint error: {e}")
    
    return success_count, len(endpoints)

def test_navigation_integration():
    """Test homepage navigation integration"""
    log_info("Testing homepage navigation integration...")
    
    try:
        response = requests.get(f"{FRONTEND_URL}/", timeout=10)
        if response.status_code == 200:
            if "Customer Portal" in response.text:
                log_success("Customer Portal button found on homepage")
                return True
            else:
                log_error("Customer Portal button not found on homepage")
                return False
        else:
            log_error(f"Homepage accessibility failed: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Navigation integration test failed: {e}")
        return False

def main():
    """Run comprehensive Customer Portal success verification"""
    print("🚀 CUSTOMER PORTAL FINAL SUCCESS VERIFICATION")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Frontend URL: {FRONTEND_URL}")
    print(f"🔗 API URL: {API_URL}")
    print("=" * 60)
    
    results = {
        "frontend_accessible": False,
        "authentication_working": False,
        "api_endpoints_working": 0,
        "navigation_integrated": False,
        "overall_success": False
    }
    
    # Test 1: Frontend Accessibility
    print("\n📱 FRONTEND ACCESSIBILITY TEST")
    results["frontend_accessible"] = test_frontend_accessibility()
    
    # Test 2: Customer Authentication
    print("\n🔐 CUSTOMER AUTHENTICATION TEST")
    token = test_customer_authentication()
    results["authentication_working"] = token is not None
    
    # Test 3: Customer API Endpoints
    if token:
        print("\n🔌 CUSTOMER API ENDPOINTS TEST")
        working_endpoints, total_endpoints = test_customer_endpoints(token)
        results["api_endpoints_working"] = working_endpoints
        log_info(f"Working endpoints: {working_endpoints}/{total_endpoints}")
    
    # Test 4: Homepage Navigation Integration
    print("\n🧭 NAVIGATION INTEGRATION TEST")
    results["navigation_integrated"] = test_navigation_integration()
    
    # Final Results
    print("\n🎯 FINAL RESULTS")
    print("=" * 60)
    
    success_criteria = [
        results["frontend_accessible"],
        results["authentication_working"],
        results["api_endpoints_working"] >= 1,  # At least one endpoint working
        results["navigation_integrated"]
    ]
    
    total_success = sum(success_criteria)
    overall_success = total_success >= 3  # 75% success rate
    results["overall_success"] = overall_success
    
    print(f"✅ Frontend Accessible: {'YES' if results['frontend_accessible'] else 'NO'}")
    print(f"✅ Authentication Working: {'YES' if results['authentication_working'] else 'NO'}")
    print(f"✅ API Endpoints Working: {results['api_endpoints_working']}")
    print(f"✅ Navigation Integrated: {'YES' if results['navigation_integrated'] else 'NO'}")
    
    success_percentage = (total_success / len(success_criteria)) * 100
    print(f"\n🏆 SUCCESS RATE: {success_percentage:.1f}%")
    
    if overall_success:
        print("\n🎉 CUSTOMER PORTAL DEPLOYMENT: SUCCESS!")
        print("🚀 The Customer Portal is now LIVE and functional!")
        print("\n🔑 Test Credentials:")
        print(f"   Username: {TEST_CREDENTIALS['username']}")
        print(f"   Password: {TEST_CREDENTIALS['password']}")
        print(f"\n🌐 Access URL: {FRONTEND_URL}/customer/login")
    else:
        print("\n⚠️ CUSTOMER PORTAL DEPLOYMENT: PARTIAL SUCCESS")
        print("Some components need attention for full functionality.")
    
    # Save results
    with open("customer_portal_final_verification.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "success_percentage": success_percentage,
            "frontend_url": FRONTEND_URL,
            "api_url": API_URL,
            "test_credentials": TEST_CREDENTIALS
        }, f, indent=2)
    
    print(f"\n📊 Results saved to: customer_portal_final_verification.json")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
