#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Cloud Deployment Test Suite
Comprehensive testing of the deployed cloud system
"""

import requests
import json
import time
from datetime import datetime

# Cloud URLs
BACKEND_URL = "https://neuroscan-api.onrender.com"
FRONTEND_URL = "https://neuroscan-system.vercel.app"

class NeuroScanCloudTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.frontend_url = FRONTEND_URL
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{result['status']} {test_name}: {details}")
        
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy" and data.get("database") == "connected":
                    self.log_test("Backend Health Check", True, 
                                f"Database: {data.get('database_type', 'Unknown')}")
                    return True
                else:
                    self.log_test("Backend Health Check", False, 
                                f"Unhealthy response: {data}")
                    return False
            else:
                self.log_test("Backend Health Check", False, 
                            f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {e}")
            return False
            
    def test_api_documentation(self):
        """Test API documentation endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=10)
            if response.status_code == 200:
                self.log_test("API Documentation", True, "Swagger docs accessible")
                return True
            else:
                self.log_test("API Documentation", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Documentation", False, f"Error: {e}")
            return False
            
    def test_cors_headers(self):
        """Test CORS configuration"""
        try:
            response = requests.options(f"{self.backend_url}/health", 
                                      headers={"Origin": self.frontend_url},
                                      timeout=10)
            cors_headers = response.headers.get("Access-Control-Allow-Origin")
            if cors_headers:
                self.log_test("CORS Configuration", True, f"CORS headers present")
                return True
            else:
                self.log_test("CORS Configuration", False, "No CORS headers found")
                return False
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Error: {e}")
            return False
            
    def test_frontend_accessibility(self):
        """Test frontend accessibility"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_test("Frontend Accessibility", True, "Frontend loads successfully")
                return True
            else:
                self.log_test("Frontend Accessibility", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Accessibility", False, f"Error: {e}")
            return False
            
    def test_api_endpoints(self):
        """Test key API endpoints"""
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/docs", "API documentation"),
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log_test(f"API Endpoint {endpoint}", True, description)
                else:
                    self.log_test(f"API Endpoint {endpoint}", False, 
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"API Endpoint {endpoint}", False, f"Error: {e}")
                
    def test_database_connection(self):
        """Test database connection through health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                db_status = data.get("database")
                db_type = data.get("database_type", "Unknown")
                
                if db_status == "connected" and "PostgreSQL" in db_type:
                    self.log_test("PostgreSQL Database", True, 
                                f"Connected to {db_type}")
                    return True
                else:
                    self.log_test("PostgreSQL Database", False, 
                                f"Status: {db_status}, Type: {db_type}")
                    return False
            else:
                self.log_test("PostgreSQL Database", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("PostgreSQL Database", False, f"Error: {e}")
            return False
            
    def test_response_times(self):
        """Test response times"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200 and response_time < 5000:  # 5 seconds
                self.log_test("Response Time", True, 
                            f"{response_time:.0f}ms (Good performance)")
                return True
            else:
                self.log_test("Response Time", False, 
                            f"{response_time:.0f}ms (Slow response)")
                return False
        except Exception as e:
            self.log_test("Response Time", False, f"Error: {e}")
            return False
            
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting NeuroScan Cloud Deployment Tests...")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_backend_health,
            self.test_database_connection,
            self.test_api_documentation,
            self.test_cors_headers,
            self.test_frontend_accessibility,
            self.test_api_endpoints,
            self.test_response_times,
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
            time.sleep(1)  # Brief pause between tests
            
        print("\n" + "=" * 60)
        print(f"🎯 Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Your cloud deployment is working perfectly!")
            status = "SUCCESS"
        elif passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("⚠️  Most tests passed. Minor issues detected.")
            status = "MOSTLY_SUCCESS"
        else:
            print("❌ Several tests failed. Please check the issues.")
            status = "ISSUES_DETECTED"
            
        # Generate test report
        self.generate_test_report(status, passed_tests, total_tests)
        
        return status, passed_tests, total_tests
        
    def generate_test_report(self, status, passed, total):
        """Generate detailed test report"""
        report = {
            "test_timestamp": datetime.now().isoformat(),
            "backend_url": self.backend_url,
            "frontend_url": self.frontend_url,
            "overall_status": status,
            "tests_passed": passed,
            "tests_total": total,
            "success_rate": f"{(passed/total)*100:.1f}%",
            "test_results": self.test_results
        }
        
        # Save report to file
        with open("cloud_deployment_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📋 Detailed test report saved to: cloud_deployment_test_report.json")


if __name__ == "__main__":
    tester = NeuroScanCloudTester()
    status, passed, total = tester.run_all_tests()
    
    print(f"\n🏆 Final Status: {status}")
    print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
    
    if status == "SUCCESS":
        print("\n🚀 Your NeuroScan system is fully operational in the cloud!")
        print("🌐 URLs:")
        print(f"   Frontend: {FRONTEND_URL}")
        print(f"   Backend API: {BACKEND_URL}")
        print(f"   API Docs: {BACKEND_URL}/docs")
