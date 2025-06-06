#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroScan Test Runner
Comprehensive test execution script with reporting
"""

import subprocess
import sys
import os
from pathlib import Path
import time
import json


class TestRunner:
    """Advanced test runner with reporting and analysis"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        
    def setup_test_environment(self):
        """Setup test environment and dependencies"""
        print("🔧 Setting up test environment...")
        
        # Install test dependencies
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.project_root / "tests" / "requirements.txt")
            ], check=True, capture_output=True)
            print("✅ Test dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install test dependencies: {e}")
            return False
            
        return True
    
    def run_unit_tests(self):
        """Run unit tests"""
        print("\n🧪 Running unit tests...")
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/test_api.py",
                "-v",
                "--tb=short",
                "--cov=app",
                "--cov-report=html:htmlcov_unit",
                "--cov-report=term-missing",
                "--junit-xml=test-results-unit.xml"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            execution_time = time.time() - start_time
            
            self.test_results["unit_tests"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "execution_time": execution_time,
                "return_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            print(f"✅ Unit tests completed in {execution_time:.2f}s")
            if result.returncode != 0:
                print(f"❌ Unit tests failed with return code {result.returncode}")
                print("Error output:", result.stderr[-500:])  # Last 500 chars
                
        except Exception as e:
            print(f"❌ Failed to run unit tests: {e}")
            self.test_results["unit_tests"] = {"status": "error", "error": str(e)}
    
    def run_security_tests(self):
        """Run security and privacy tests"""
        print("\n🛡️ Running security tests...")
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/test_security.py",
                "-v",
                "--tb=short",
                "--cov=app.core",
                "--cov-report=html:htmlcov_security",
                "--cov-report=term-missing",
                "--junit-xml=test-results-security.xml"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            execution_time = time.time() - start_time
            
            self.test_results["security_tests"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "execution_time": execution_time,
                "return_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            print(f"✅ Security tests completed in {execution_time:.2f}s")
            if result.returncode != 0:
                print(f"❌ Security tests failed with return code {result.returncode}")
                print("Error output:", result.stderr[-500:])
                
        except Exception as e:
            print(f"❌ Failed to run security tests: {e}")
            self.test_results["security_tests"] = {"status": "error", "error": str(e)}
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("\n🔗 Running integration tests...")
        start_time = time.time()
        
        try:
            # Run all tests together for integration
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--cov=app",
                "--cov-report=html:htmlcov_integration",
                "--cov-report=term-missing",
                "--junit-xml=test-results-integration.xml",
                "-m", "not slow"  # Skip slow tests for now
            ], cwd=self.project_root, capture_output=True, text=True)
            
            execution_time = time.time() - start_time
            
            self.test_results["integration_tests"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "execution_time": execution_time,
                "return_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            print(f"✅ Integration tests completed in {execution_time:.2f}s")
            if result.returncode != 0:
                print(f"❌ Integration tests failed with return code {result.returncode}")
                print("Error output:", result.stderr[-500:])
                
        except Exception as e:
            print(f"❌ Failed to run integration tests: {e}")
            self.test_results["integration_tests"] = {"status": "error", "error": str(e)}
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("\n⚡ Running performance tests...")
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "-m", "performance",
                "--junit-xml=test-results-performance.xml"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            execution_time = time.time() - start_time
            
            self.test_results["performance_tests"] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "execution_time": execution_time,
                "return_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            print(f"✅ Performance tests completed in {execution_time:.2f}s")
            if result.returncode != 0:
                print(f"❌ Performance tests failed with return code {result.returncode}")
                
        except Exception as e:
            print(f"❌ Failed to run performance tests: {e}")
            self.test_results["performance_tests"] = {"status": "error", "error": str(e)}
    
    def analyze_coverage(self):
        """Analyze test coverage"""
        print("\n📊 Analyzing test coverage...")
        
        try:
            # Generate coverage report
            result = subprocess.run([
                sys.executable, "-m", "coverage", "report", "--show-missing"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Coverage Report:")
                print(result.stdout)
                
                # Extract coverage percentage
                lines = result.stdout.split('\n')
                total_line = [line for line in lines if 'TOTAL' in line]
                if total_line:
                    coverage_percent = total_line[0].split()[-1]
                    self.test_results["coverage"] = coverage_percent
                    print(f"📈 Total Coverage: {coverage_percent}")
            else:
                print("❌ Failed to generate coverage report")
                
        except Exception as e:
            print(f"❌ Failed to analyze coverage: {e}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📋 Generating test report...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_test_suites": len(self.test_results),
                "passed_suites": len([r for r in self.test_results.values() 
                                    if r.get("status") == "passed"]),
                "failed_suites": len([r for r in self.test_results.values() 
                                    if r.get("status") == "failed"]),
                "total_execution_time": sum([r.get("execution_time", 0) 
                                           for r in self.test_results.values()])
            },
            "details": self.test_results
        }
        
        # Save report
        report_file = self.project_root / "test-report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("🏆 TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"Total Test Suites: {report['summary']['total_test_suites']}")
        print(f"Passed: {report['summary']['passed_suites']}")
        print(f"Failed: {report['summary']['failed_suites']}")
        print(f"Total Execution Time: {report['summary']['total_execution_time']:.2f}s")
        
        if report['summary']['failed_suites'] == 0:
            print("🎉 All tests passed!")
        else:
            print("⚠️ Some tests failed. Check the detailed report.")
        
        return report
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting NeuroScan Test Suite")
        print("="*60)
        
        # Setup
        if not self.setup_test_environment():
            return False
        
        # Run test suites
        self.run_unit_tests()
        self.run_security_tests()
        self.run_integration_tests()
        self.run_performance_tests()
        
        # Analysis
        self.analyze_coverage()
        
        # Report
        report = self.generate_test_report()
        
        return report['summary']['failed_suites'] == 0


def main():
    """Main test runner entry point"""
    runner = TestRunner()
    
    # Check if specific test type is requested
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "unit":
            runner.setup_test_environment()
            runner.run_unit_tests()
        elif test_type == "security":
            runner.setup_test_environment()
            runner.run_security_tests()
        elif test_type == "integration":
            runner.setup_test_environment()
            runner.run_integration_tests()
        elif test_type == "performance":
            runner.setup_test_environment()
            runner.run_performance_tests()
        elif test_type == "coverage":
            runner.analyze_coverage()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available types: unit, security, integration, performance, coverage")
            return False
    else:
        # Run all tests
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    
    return True


if __name__ == "__main__":
    main()
