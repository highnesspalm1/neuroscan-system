#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Manager for NeuroScan Desktop Application
Handles communication with cloud services and status monitoring
"""

import requests
import json
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QTimer, QThread
from PySide6.QtWidgets import QWidget


class CloudStatusChecker(QThread):
    """Background thread for checking cloud service status"""
    
    status_updated = Signal(str, str, str)  # service_name, status, message
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        self.running = True
        
    def run(self):
        """Check all services in background"""
        while self.running:
            self.check_all_services()
            self.msleep(30000)  # Check every 30 seconds
            
    def stop(self):
        """Stop the background checking"""
        self.running = False
        self.quit()
        self.wait()
        
    def check_all_services(self):
        """Check status of all cloud services"""
        services = {
            "Backend API": self.config["api"]["base_url"],
            "Frontend": self.config["api"]["frontend_url"],
            "API Docs": self.config["api"]["docs_url"]
        }
        
        for service_name, url in services.items():
            status, message = self.check_service(service_name, url)
            self.status_updated.emit(service_name, status, message)
    
    def check_service(self, service_name: str, url: str) -> Tuple[str, str]:
        """Check individual service status"""
        try:
            if service_name == "Backend API":
                # Check backend health endpoint
                response = requests.get(f"{url}/health", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        return "online", f"✅ {service_name} is healthy"
                    else:
                        return "warning", f"⚠️ {service_name} status: {data.get('status', 'unknown')}"
                else:
                    return "error", f"❌ {service_name} returned status {response.status_code}"
                    
            elif service_name == "Frontend":
                # Check frontend availability
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    return "online", f"✅ {service_name} is accessible"
                else:
                    return "error", f"❌ {service_name} returned status {response.status_code}"
                    
            elif service_name == "API Docs":
                # Check API documentation
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    return "online", f"✅ {service_name} is accessible"
                else:
                    return "error", f"❌ {service_name} returned status {response.status_code}"
                    
        except requests.exceptions.Timeout:
            return "error", f"❌ {service_name} timeout (server may be starting up)"
        except requests.exceptions.ConnectionError:
            return "error", f"❌ {service_name} connection failed"
        except requests.exceptions.RequestException as e:
            return "error", f"❌ {service_name} error: {str(e)}"
        except Exception as e:
            return "error", f"❌ {service_name} unexpected error: {str(e)}"
            
        return "unknown", f"❓ {service_name} status unknown"


class APIManager(QObject):
    """Manager for API communication and authentication"""
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        self.base_url = config["api"]["base_url"]
        self.timeout = config["api"]["timeout"]
        self.token = None
        self.session = requests.Session()
        
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Login to the API and get authentication token"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                return True, "Login successful"
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("detail", f"Login failed with status {response.status_code}")
                return False, error_msg
                
        except requests.exceptions.Timeout:
            return False, "Login timeout - server may be starting up (try again in 1-2 minutes)"
        except requests.exceptions.ConnectionError:
            return False, "Connection failed - check your internet connection"
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def get_current_user(self) -> Tuple[bool, Optional[Dict]]:
        """Get current user information"""
        if not self.token:
            return False, None
            
        try:
            response = self.session.get(
                f"{self.base_url}/auth/me",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, None
                
        except Exception as e:
            return False, None
    
    def create_customer(self, customer_data: Dict) -> Tuple[bool, Optional[Dict], str]:
        """Create a new customer"""
        try:
            response = self.session.post(
                f"{self.base_url}/admin/customers",
                json=customer_data,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                return True, response.json(), "Customer created successfully"
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("detail", f"Failed with status {response.status_code}")
                return False, None, error_msg
                
        except Exception as e:
            return False, None, f"Error creating customer: {str(e)}"
    
    def get_customers(self) -> Tuple[bool, List[Dict], str]:
        """Get all customers"""
        try:
            response = self.session.get(
                f"{self.base_url}/admin/customers",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json(), "Success"
            else:
                return False, [], f"Failed with status {response.status_code}"
                
        except Exception as e:
            return False, [], f"Error fetching customers: {str(e)}"
    
    def create_certificate(self, certificate_data: Dict) -> Tuple[bool, Optional[Dict], str]:
        """Create a new certificate"""
        try:
            response = self.session.post(
                f"{self.base_url}/admin/certificates",
                json=certificate_data,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                return True, response.json(), "Certificate created successfully"
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("detail", f"Failed with status {response.status_code}")
                return False, None, error_msg
                
        except Exception as e:
            return False, None, f"Error creating certificate: {str(e)}"
    
    def get_certificates(self) -> Tuple[bool, List[Dict], str]:
        """Get all certificates"""
        try:
            response = self.session.get(
                f"{self.base_url}/admin/certificates",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json(), "Success"
            else:
                return False, [], f"Failed with status {response.status_code}"
                
        except Exception as e:
            return False, [], f"Error fetching certificates: {str(e)}"
    
    def logout(self):
        """Logout and clear authentication"""
        self.token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.token is not None
    
    def check_health(self) -> Optional[Dict]:
        """Check backend API health"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception:
            return None
    
    def check_frontend_status(self) -> bool:
        """Check frontend availability"""
        try:
            frontend_url = self.config["api"]["frontend_url"]
            response = requests.get(frontend_url, timeout=30)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_docs_status(self) -> bool:
        """Check API documentation availability"""
        try:
            docs_url = self.config["api"]["docs_url"]
            response = requests.get(docs_url, timeout=30)
            return response.status_code == 200
        except Exception:
            return False
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a generic API request"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = self.session.get(url, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=self.timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": 200 <= response.status_code < 300
            }
            
        except Exception as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "success": False
            }
