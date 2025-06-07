"""
🎉 CUSTOMER PORTAL - FINAL VERIFICATION TEST
============================================
This script performs a comprehensive test of the Customer Portal
to verify all improvements are working correctly.
"""

import requests
import json
from datetime import datetime

print("🔥 CUSTOMER PORTAL - FINAL VERIFICATION")
print("=" * 50)
print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Configuration
API_BASE = "https://neuroscan-api.onrender.com"
FRONTEND_URL = "https://neuroscan-system.vercel.app"
TEST_CREDENTIALS = {
    "username": "testcustomer",
    "password": "password123"
}

def test_component(name, test_func):
    """Test a component and return result"""
    try:
        print(f"🧪 Testing {name}...")
        result = test_func()
        print(f"   ✅ {name}: PASS")
        return True
    except Exception as e:
        print(f"   ❌ {name}: FAIL - {str(e)}")
        return False

def test_api_health():
    """Test API health endpoint"""
    response = requests.get(f"{API_BASE}/health", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    return data

def test_customer_login():
    """Test customer login functionality"""
    response = requests.post(
        f"{API_BASE}/customer/login",
        data=TEST_CREDENTIALS,
        timeout=30  # Extended timeout for cold start
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["customer"]["username"] == "testcustomer"
    return data

def test_protected_endpoints():
    """Test protected customer endpoints"""
    # First login to get token
    login_response = requests.post(f"{API_BASE}/customer/login", data=TEST_CREDENTIALS)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test protected endpoints
    endpoints = ["/customer/me", "/customer/dashboard", "/customer/products", "/customer/certificates"]
    results = {}
    
    for endpoint in endpoints:
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
        results[endpoint] = response.status_code
        assert response.status_code == 200
    
    return results

def test_frontend_accessibility():
    """Test frontend accessibility"""
    response = requests.get(FRONTEND_URL, timeout=10)
    assert response.status_code == 200
    return response.status_code

def test_cors_configuration():
    """Test CORS configuration"""
    response = requests.options(f"{API_BASE}/customer/login")
    headers = dict(response.headers)
    assert "access-control-allow-origin" in headers
    assert FRONTEND_URL in headers["access-control-allow-origin"]
    return headers

# Run all tests
tests = [
    ("API Health Check", test_api_health),
    ("Customer Login", test_customer_login),
    ("Protected Endpoints", test_protected_endpoints),
    ("Frontend Accessibility", test_frontend_accessibility),
    ("CORS Configuration", test_cors_configuration)
]

results = {}
passed_tests = 0
total_tests = len(tests)

for test_name, test_func in tests:
    if test_component(test_name, test_func):
        passed_tests += 1
        results[test_name] = "PASS"
    else:
        results[test_name] = "FAIL"
    print()

# Final summary
print("📊 FINAL TEST RESULTS")
print("=" * 30)
for test_name, result in results.items():
    status_emoji = "✅" if result == "PASS" else "❌"
    print(f"{status_emoji} {test_name}: {result}")

print()
print(f"📈 SUCCESS RATE: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")

if passed_tests == total_tests:
    print("🎉 ALL TESTS PASSED! Customer Portal is fully operational!")
    print("🚀 Users can now:")
    print("   • Access https://neuroscan-system.vercel.app/customer/login")
    print("   • Login with testcustomer/password123") 
    print("   • Navigate through all customer portal features")
    print("   • Handle API cold starts gracefully with the wake-up button")
else:
    print("⚠️  Some tests failed. Please review the errors above.")

print("\n🏁 VERIFICATION COMPLETE")
