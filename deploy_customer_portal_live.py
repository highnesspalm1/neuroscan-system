#!/usr/bin/env python3
"""
NeuroScan Customer Portal - Live Deployment Script
Deploys commit 209a860: Complete Customer Portal Implementation
"""

import requests
import time
import json
import os
from datetime import datetime

# Configuration
CLOUD_API_URL = "https://neuroscan-api.onrender.com"
FRONTEND_URL = "https://neuroscan-system.vercel.app"
ADMIN_EMAIL = "admin@neuroscan.com"
ADMIN_PASSWORD = "admin123"

class NeuroScanDeployment:
    def __init__(self):
        self.deployment_log = []
        self.start_time = datetime.now()
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def wait_for_deployment(self, max_wait=600):
        """Wait for cloud deployment to complete"""
        self.log("🔄 Waiting for cloud deployment to complete...")
        
        for attempt in range(max_wait // 30):
            try:
                response = requests.get(f"{CLOUD_API_URL}/health", timeout=10)
                if response.status_code == 200:
                    self.log("✅ Backend deployment is online!", "SUCCESS")
                    return True
                else:
                    self.log(f"⏳ Backend starting... (attempt {attempt + 1})", "INFO")
            except Exception as e:
                self.log(f"⏳ Waiting for backend... (attempt {attempt + 1})", "INFO")
            
            time.sleep(30)
        
        self.log("❌ Backend deployment timeout", "ERROR")
        return False
    
    def test_admin_authentication(self):
        """Test admin authentication to ensure basic API is working"""
        self.log("🔐 Testing admin authentication...")
        
        try:
            response = requests.post(f"{CLOUD_API_URL}/admin/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                self.log("✅ Admin authentication successful", "SUCCESS")
                return token
            else:
                self.log(f"❌ Admin auth failed: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Admin auth error: {e}", "ERROR")
            return None
    
    def execute_database_migration(self, admin_token):
        """Execute database migration for customer authentication"""
        self.log("🛠️ Executing customer authentication database migration...")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        migration_sql = """
        -- Customer Authentication Migration
        ALTER TABLE customers ADD COLUMN IF NOT EXISTS username VARCHAR(255) UNIQUE;
        ALTER TABLE customers ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);
        ALTER TABLE customers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
        ALTER TABLE customers ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_customers_username ON customers(username);
        CREATE INDEX IF NOT EXISTS idx_customers_active ON customers(is_active);
        
        -- Update existing customers
        UPDATE customers SET is_active = TRUE WHERE is_active IS NULL;
        """
        
        try:
            # Try direct migration endpoint if available
            response = requests.post(f"{CLOUD_API_URL}/admin/database/migrate", 
                                   headers=headers,
                                   json={"sql": migration_sql}, 
                                   timeout=60)
            
            if response.status_code == 200:
                self.log("✅ Database migration executed successfully", "SUCCESS")
                return True
            else:
                self.log(f"⚠ Migration endpoint response: {response.status_code}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"❌ Migration error: {e}", "ERROR")
            return False
    
    def create_test_customer(self, admin_token):
        """Create test customer for portal testing"""
        self.log("👤 Creating test customer...")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        customer_data = {
            "name": "Test Customer Company",
            "email": "test@customer.com",
            "username": "testcustomer",
            "password": "password123"
        }
        
        try:
            response = requests.post(f"{CLOUD_API_URL}/admin/customers", 
                                   headers=headers,
                                   json=customer_data,
                                   timeout=30)
            
            if response.status_code in [200, 201]:
                self.log("✅ Test customer created successfully", "SUCCESS")
                return True
            elif response.status_code == 400 and "already exists" in response.text.lower():
                self.log("✅ Test customer already exists", "SUCCESS")
                return True
            else:
                self.log(f"⚠ Customer creation response: {response.status_code} - {response.text}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"❌ Customer creation error: {e}", "ERROR")
            return False
    
    def test_customer_authentication(self):
        """Test customer portal authentication"""
        self.log("🧪 Testing customer portal authentication...")
        
        try:
            response = requests.post(f"{CLOUD_API_URL}/customer/login", json={
                "username": "testcustomer",
                "password": "password123"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                customer_name = data.get("customer", {}).get("name", "Unknown")
                token = data.get("access_token", "")
                self.log(f"✅ Customer authentication successful: {customer_name}", "SUCCESS")
                return token
            else:
                self.log(f"❌ Customer auth failed: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Customer auth error: {e}", "ERROR")
            return None
    
    def test_customer_endpoints(self, customer_token):
        """Test all customer portal endpoints"""
        self.log("📊 Testing customer portal endpoints...")
        
        headers = {"Authorization": f"Bearer {customer_token}"}
        endpoints = [
            ("/customer/me", "Customer Info"),
            ("/customer/dashboard", "Dashboard"),
            ("/customer/products", "Products"),
            ("/customer/certificates", "Certificates"),
            ("/customer/scan-logs", "Scan Logs")
        ]
        
        successful_endpoints = []
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{CLOUD_API_URL}{endpoint}", 
                                      headers=headers, 
                                      timeout=20)
                
                if response.status_code == 200:
                    self.log(f"   ✅ {name}: Working", "SUCCESS")
                    successful_endpoints.append(name)
                else:
                    self.log(f"   ❌ {name}: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"   ❌ {name}: Error - {str(e)[:50]}", "ERROR")
        
        return successful_endpoints
    
    def test_frontend_deployment(self):
        """Test frontend deployment"""
        self.log("🌐 Testing frontend deployment...")
        
        try:
            # Test main frontend
            response = requests.get(FRONTEND_URL, timeout=15)
            if response.status_code == 200:
                self.log("✅ Frontend main page accessible", "SUCCESS")
            
            # Test customer login page
            response = requests.get(f"{FRONTEND_URL}/customer/login", timeout=15)
            if response.status_code == 200:
                self.log("✅ Customer login page accessible", "SUCCESS")
                return True
            else:
                self.log(f"⚠ Customer login page: {response.status_code}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"❌ Frontend test error: {e}", "ERROR")
            return False
    
    def generate_deployment_report(self, backend_success, frontend_success, customer_auth_success, working_endpoints):
        """Generate comprehensive deployment report"""
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            "deployment_info": {
                "commit": "640b087 (209a860: Customer Portal Implementation)",
                "timestamp": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "SUCCESS" if all([backend_success, frontend_success, customer_auth_success]) else "PARTIAL"
            },
            "backend_deployment": {
                "status": "SUCCESS" if backend_success else "FAILED",
                "url": CLOUD_API_URL,
                "health_check": backend_success
            },
            "frontend_deployment": {
                "status": "SUCCESS" if frontend_success else "FAILED", 
                "url": FRONTEND_URL,
                "customer_portal": f"{FRONTEND_URL}/customer/login"
            },
            "customer_portal": {
                "authentication": "SUCCESS" if customer_auth_success else "FAILED",
                "working_endpoints": working_endpoints,
                "total_endpoints": 5,
                "success_rate": f"{len(working_endpoints)}/5"
            },
            "test_credentials": {
                "username": "testcustomer",
                "password": "password123",
                "company": "Test Customer Company"
            },
            "deployment_log": self.deployment_log
        }
        
        # Save report
        with open("customer_portal_deployment_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_deployment_summary(self, report):
        """Print deployment summary"""
        print("\n" + "=" * 70)
        print("🚀 NEUROSCAN CUSTOMER PORTAL - LIVE DEPLOYMENT COMPLETE")
        print("=" * 70)
        
        status = report["deployment_info"]["status"]
        duration = report["deployment_info"]["duration_seconds"]
        
        print(f"📅 Deployment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Deployment Duration: {duration:.1f} seconds")
        print(f"📊 Overall Status: {'✅ SUCCESS' if status == 'SUCCESS' else '⚠ PARTIAL SUCCESS'}")
        
        print(f"\n🔗 LIVE URLS:")
        print(f"   🌐 Frontend: {FRONTEND_URL}")
        print(f"   🔐 Customer Portal: {FRONTEND_URL}/customer/login")
        print(f"   📡 Backend API: {CLOUD_API_URL}")
        print(f"   📚 API Docs: {CLOUD_API_URL}/docs")
        
        print(f"\n🧪 TEST CREDENTIALS:")
        print(f"   👤 Username: testcustomer")
        print(f"   🔑 Password: password123")
        
        print(f"\n📈 CUSTOMER PORTAL STATUS:")
        auth_status = report["customer_portal"]["authentication"]
        endpoint_success = report["customer_portal"]["success_rate"]
        print(f"   🔐 Authentication: {'✅ Working' if auth_status == 'SUCCESS' else '❌ Failed'}")
        print(f"   📊 Endpoints: {endpoint_success} working")
        
        if report["customer_portal"]["working_endpoints"]:
            print(f"   ✅ Working Features:")
            for endpoint in report["customer_portal"]["working_endpoints"]:
                print(f"      • {endpoint}")
        
        print(f"\n🎯 NEXT STEPS:")
        if status == "SUCCESS":
            print(f"   1. ✅ Customer Portal is LIVE and ready for use")
            print(f"   2. 🧪 Test all features via web interface")
            print(f"   3. 👥 Create additional customer accounts as needed")
            print(f"   4. 📱 Validate mobile responsiveness")
        else:
            print(f"   1. ⚠ Review deployment logs for any issues")
            print(f"   2. 🔄 Manual database migration may be needed")
            print(f"   3. 🧪 Test individual components")
        
        print("\n" + "=" * 70)

def main():
    deployer = NeuroScanDeployment()
    
    print("🚀 NEUROSCAN CUSTOMER PORTAL - LIVE DEPLOYMENT")
    print("=" * 60)
    print("Deploying commit 209a860: Complete Customer Portal Implementation")
    print("=" * 60)
    
    # Step 1: Wait for deployment
    backend_success = deployer.wait_for_deployment()
    
    # Step 2: Test admin authentication  
    admin_token = None
    if backend_success:
        admin_token = deployer.test_admin_authentication()
    
    # Step 3: Execute database migration
    migration_success = False
    if admin_token:
        migration_success = deployer.execute_database_migration(admin_token)
        
        # Create test customer
        deployer.create_test_customer(admin_token)
    
    # Step 4: Test customer authentication
    customer_token = deployer.test_customer_authentication()
    customer_auth_success = customer_token is not None
    
    # Step 5: Test customer endpoints
    working_endpoints = []
    if customer_token:
        working_endpoints = deployer.test_customer_endpoints(customer_token)
    
    # Step 6: Test frontend
    frontend_success = deployer.test_frontend_deployment()
    
    # Step 7: Generate report
    report = deployer.generate_deployment_report(
        backend_success, 
        frontend_success, 
        customer_auth_success, 
        working_endpoints
    )
    
    # Step 8: Print summary
    deployer.print_deployment_summary(report)
    
    return report["deployment_info"]["status"] == "SUCCESS"

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
