#!/usr/bin/env python3
"""
Comprehensive Test Runner for QA_AI Test Cases
Runs all test cases in the test_cases directory
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class TestRunner:
    """Comprehensive test runner for all generated test cases"""
    
    def __init__(self):
        self.test_cases_dir = Path("test_cases")
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_files": [],
            "start_time": None,
            "end_time": None
        }
    
    def discover_test_files(self):
        """Discover all test files in the test_cases directory"""
        test_files = []
        
        if not self.test_cases_dir.exists():
            print(f"❌ Test cases directory not found: {self.test_cases_dir}")
            return test_files
        
        # Find all Python test files
        for root, dirs, files in os.walk(self.test_cases_dir):
            for file in files:
                if file.endswith('.py') and file.startswith('test_'):
                    test_file = Path(root) / file
                    test_files.append(test_file)
        
        return test_files
    
    def run_single_test_file(self, test_file):
        """Run a single test file and return results"""
        print(f"\n🧪 Running: {test_file.name}")
        print("=" * 60)
        
        try:
            # Change to the directory containing the test file
            original_dir = os.getcwd()
            test_dir = test_file.parent
            os.chdir(test_dir)
            
            # Run the test with pytest
            cmd = [
                sys.executable, "-m", "pytest", 
                test_file.name, 
                "-v", 
                "--tb=short"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout per test file
            )
            
            # Parse results
            test_result = {
                "file": str(test_file),
                "name": test_file.name,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            # Count test results from output
            lines = result.stdout.split('\n')
            passed = 0
            failed = 0
            
            for line in lines:
                if 'PASSED' in line:
                    passed += 1
                elif 'FAILED' in line or 'ERROR' in line:
                    failed += 1
            
            test_result["passed"] = passed
            test_result["failed"] = failed
            
            # Print results
            if result.returncode == 0:
                print(f"✅ PASSED: {passed} tests passed, {failed} failed")
            else:
                print(f"❌ FAILED: {passed} tests passed, {failed} failed")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}...")
            
            # Change back to original directory
            os.chdir(original_dir)
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ TIMEOUT: Test file took too long to run")
            return {
                "file": str(test_file),
                "name": test_file.name,
                "return_code": -1,
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return {
                "file": str(test_file),
                "name": test_file.name,
                "return_code": -1,
                "success": False,
                "error": str(e)
            }
    
    def run_working_test(self, test_file):
        """Run the working test file specifically"""
        print(f"\n🎯 Running Working Test: {test_file.name}")
        print("=" * 60)
        
        try:
            # Change to the directory containing the test file
            original_dir = os.getcwd()
            test_dir = test_file.parent
            os.chdir(test_dir)
            
            # Run the test directly with Python
            cmd = [sys.executable, test_file.name]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            test_result = {
                "file": str(test_file),
                "name": test_file.name,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            if result.returncode == 0:
                print("✅ Working test completed successfully!")
            else:
                print(f"❌ Working test failed: {result.stderr}")
            
            # Change back to original directory
            os.chdir(original_dir)
            
            return test_result
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return {
                "file": str(test_file),
                "name": test_file.name,
                "return_code": -1,
                "success": False,
                "error": str(e)
            }
    
    def run_all_tests(self):
        """Run all discovered test files"""
        print("🚀 QA_AI Test Runner")
        print("=" * 60)
        print(f"📁 Scanning directory: {self.test_cases_dir}")
        
        # Discover test files
        test_files = self.discover_test_files()
        
        if not test_files:
            print("❌ No test files found!")
            return
        
        print(f"📋 Found {len(test_files)} test files:")
        for test_file in test_files:
            print(f"   - {test_file.name}")
        
        # Start timing
        self.results["start_time"] = datetime.now()
        
        # Run each test file
        for test_file in test_files:
            self.results["total_tests"] += 1
            
            # Check if it's a working test file
            if "working" in test_file.name.lower():
                result = self.run_working_test(test_file)
            else:
                result = self.run_single_test_file(test_file)
            
            self.results["test_files"].append(result)
            
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
            
            # Small delay between tests
            time.sleep(1)
        
        # End timing
        self.results["end_time"] = datetime.now()
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
    
    def print_summary(self):
        """Print test execution summary"""
        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        duration = self.results["end_time"] - self.results["start_time"]
        
        print(f"⏱️  Total Duration: {duration}")
        print(f"📁 Total Test Files: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / self.results['total_tests'] * 100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.results["test_files"]:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status} - {result['name']}")
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects to strings for JSON serialization
        results_copy = self.results.copy()
        if results_copy["start_time"]:
            results_copy["start_time"] = results_copy["start_time"].isoformat()
        if results_copy["end_time"]:
            results_copy["end_time"] = results_copy["end_time"].isoformat()
        
        with open(results_file, 'w') as f:
            json.dump(results_copy, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")

def main():
    """Main function to run all tests"""
    runner = TestRunner()
    runner.run_all_tests()

if __name__ == "__main__":
    main() 