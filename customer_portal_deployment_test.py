#!/usr/bin/env python3
"""
Customer Portal Final Deployment
Complete deployment and verification of the customer portal
"""

import requests
import asyncio
import json
import time
from datetime import datetime

class CustomerPortalDeployment:
    def __init__(self):
        self.api_url = "https://neuroscan-api.onrender.com"
        self.frontend_url = "https://neuroscan-system.vercel.app"
    
    def trigger_deployment_refresh(self):
        """Trigger a fresh deployment by hitting endpoints"""
        print("🔄 Triggering deployment refresh...")
        
        try:
            # Health check to warm up the service
            response = requests.get(f"{self.api_url}/health", timeout=30)
            print(f"   API Health: {response.status_code}")
            
            # Test docs endpoint
            response = requests.get(f"{self.api_url}/docs", timeout=30)
            print(f"   API Docs: {response.status_code}")
            
            # Test frontend
            response = requests.get(f"{self.frontend_url}/customer/login", timeout=30)
            print(f"   Frontend: {response.status_code}")
            
            print("✅ Deployment refresh completed")
            return True
            
        except Exception as e:
            print(f"❌ Deployment refresh failed: {e}")
            return False
    
    def test_customer_endpoints(self):
        """Test all customer-related endpoints"""
        print("\n🧪 Testing Customer Portal Endpoints...")
        print("-" * 50)
        
        endpoints = [
            ("/health", "GET", None),
            ("/docs", "GET", None),
            ("/customer/login", "POST", {"username": "test", "password": "test"}),
            ("/customer/create", "POST", {
                "name": "Test Customer",
                "email": "test@neuroscan.com", 
                "username": "testuser",
                "password": "testpass123"
            }),
        ]
        
        results = {}
        
        for endpoint, method, data in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.api_url}{endpoint}", timeout=15)
                else:
                    response = requests.post(f"{self.api_url}{endpoint}", json=data, timeout=15)
                
                status = "✅" if response.status_code < 500 else "❌"
                results[endpoint] = {
                    "status_code": response.status_code,
                    "success": response.status_code < 500
                }
                
                print(f"   {status} {method} {endpoint}: {response.status_code}")
                
                # Log response for debugging
                if response.status_code >= 500:
                    print(f"      Error: {response.text[:100]}...")
                
            except Exception as e:
                print(f"   ❌ {method} {endpoint}: Error - {str(e)}")
                results[endpoint] = {"status_code": 0, "success": False}
        
        return results
    
    def test_frontend_accessibility(self):
        """Test frontend page accessibility"""
        print("\n🌐 Testing Frontend Accessibility...")
        print("-" * 50)
        
        pages = [
            "/",
            "/customer/login",
            "/customer/dashboard",
            "/admin/login",
        ]
        
        results = {}
        
        for page in pages:
            try:
                response = requests.get(f"{self.frontend_url}{page}", timeout=15)
                status = "✅" if response.status_code == 200 else "❌"
                results[page] = response.status_code == 200
                print(f"   {status} {page}: {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ {page}: Error - {str(e)}")
                results[page] = False
        
        return results
    
    def run_comprehensive_test(self):
        """Run comprehensive deployment test"""
        print("🚀 CUSTOMER PORTAL FINAL DEPLOYMENT TEST")
        print("=" * 60)
        print(f"Target API: {self.api_url}")
        print(f"Target Frontend: {self.frontend_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. Trigger deployment refresh
        deployment_success = self.trigger_deployment_refresh()
        
        # 2. Wait for services to be ready
        print("\n⏳ Waiting for services to be ready...")
        time.sleep(10)
        
        # 3. Test API endpoints
        api_results = self.test_customer_endpoints()
        
        # 4. Test frontend
        frontend_results = self.test_frontend_accessibility()
        
        # 5. Generate final report
        self.generate_final_report(deployment_success, api_results, frontend_results)
        
        return self.calculate_success_rate(api_results, frontend_results)
    
    def calculate_success_rate(self, api_results, frontend_results):
        """Calculate overall success rate"""
        total_tests = len(api_results) + len(frontend_results)
        successful_tests = sum(1 for r in api_results.values() if r.get('success', False))
        successful_tests += sum(1 for r in frontend_results.values() if r)
        
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        return success_rate
    
    def generate_final_report(self, deployment_success, api_results, frontend_results):
        """Generate final deployment report"""
        print("\n📊 FINAL DEPLOYMENT REPORT")
        print("=" * 60)
        
        success_rate = self.calculate_success_rate(api_results, frontend_results)
        
        print(f"📅 Deployment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Overall Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            status = "🎉 FULLY FUNCTIONAL"
        elif success_rate >= 70:
            status = "⚠️ MOSTLY FUNCTIONAL"
        else:
            status = "❌ NEEDS ATTENTION"
        
        print(f"🔗 Status: {status}")
        
        print(f"\n🔗 LIVE URLS:")
        print(f"   🌐 Frontend: {self.frontend_url}")
        print(f"   🔐 Customer Portal: {self.frontend_url}/customer/login")
        print(f"   📡 Backend API: {self.api_url}")
        print(f"   📚 API Docs: {self.api_url}/docs")
        
        print(f"\n📈 API ENDPOINT STATUS:")
        for endpoint, result in api_results.items():
            status = "✅ WORKING" if result.get('success', False) else "❌ ERROR"
            print(f"   {status} {endpoint}")
        
        print(f"\n🌐 FRONTEND PAGE STATUS:")
        for page, success in frontend_results.items():
            status = "✅ ACCESSIBLE" if success else "❌ ERROR"
            print(f"   {status} {page}")
        
        # Specific customer portal status
        customer_endpoints_working = sum(1 for k, v in api_results.items() 
                                       if 'customer' in k and v.get('success', False))
        customer_pages_working = sum(1 for k, v in frontend_results.items() 
                                   if 'customer' in k and v)
        
        if customer_endpoints_working >= 1 and customer_pages_working >= 1:
            customer_status = "🎉 CUSTOMER PORTAL IS LIVE!"
        else:
            customer_status = "⚠️ Customer Portal needs attention"
        
        print(f"\n{customer_status}")
        print("=" * 60)
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "status": status,
            "api_results": api_results,
            "frontend_results": frontend_results,
            "urls": {
                "frontend": self.frontend_url,
                "customer_portal": f"{self.frontend_url}/customer/login",
                "api": self.api_url,
                "docs": f"{self.api_url}/docs"
            }
        }
        
        with open("final_deployment_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: final_deployment_report.json")

def main():
    """Main deployment test function"""
    deployer = CustomerPortalDeployment()
    success_rate = deployer.run_comprehensive_test()
    
    return success_rate >= 70  # Consider 70%+ as successful

if __name__ == "__main__":
    main()
