#!/usr/bin/env python3
"""
Comprehensive Fixed Test Runner
Runs all fixed test cases that handle popups and dynamic content
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class FixedTestRunner:
    """Comprehensive runner for all fixed test cases"""
    
    def __init__(self):
        self.test_cases_dir = Path("test_cases")
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "test_files": [],
            "start_time": None,
            "end_time": None
        }
    
    def discover_fixed_tests(self):
        """Discover all fixed test files"""
        fixed_tests = []
        
        if not self.test_cases_dir.exists():
            print(f"❌ Test cases directory not found: {self.test_cases_dir}")
            return fixed_tests
        
        # Find all fixed test files
        for root, dirs, files in os.walk(self.test_cases_dir):
            for file in files:
                if file.startswith('fixed_') and file.endswith('.py'):
                    test_file = Path(root) / file
                    fixed_tests.append(test_file)
        
        return fixed_tests
    
    def run_single_fixed_test(self, test_file):
        """Run a single fixed test file"""
        print(f"\n🧪 Running Fixed Test: {test_file.name}")
        print("=" * 60)
        
        try:
            # Change to the directory containing the test file
            original_dir = os.getcwd()
            test_dir = test_file.parent
            os.chdir(test_dir)
            
            # Run the test with Python directly
            cmd = [sys.executable, test_file.name]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90  # 1.5 minutes timeout
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
                print("✅ Fixed test completed successfully!")
            else:
                print(f"❌ Fixed test failed: {result.stderr}")
            
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
    
    def run_all_fixed_tests(self):
        """Run all discovered fixed test files"""
        print("🚀 Comprehensive Fixed Test Runner")
        print("=" * 60)
        print(f"📁 Scanning directory: {self.test_cases_dir}")
        
        # Discover fixed test files
        fixed_tests = self.discover_fixed_tests()
        
        if not fixed_tests:
            print("❌ No fixed test files found!")
            print("💡 Run 'python3 simple_popup_handler.py' first to create fixed tests")
            return
        
        print(f"📋 Found {len(fixed_tests)} fixed test files:")
        for test_file in fixed_tests:
            print(f"   - {test_file.name}")
        
        # Start timing
        self.results["start_time"] = datetime.now()
        
        # Run each fixed test file
        for test_file in fixed_tests:
            self.results["total_tests"] += 1
            
            result = self.run_single_fixed_test(test_file)
            
            self.results["test_files"].append(result)
            
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
            
            # Small delay between tests
            time.sleep(2)
        
        # End timing
        self.results["end_time"] = datetime.now()
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
    
    def print_summary(self):
        """Print test execution summary"""
        print("\n" + "=" * 60)
        print("📊 FIXED TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        duration = self.results["end_time"] - self.results["start_time"]
        
        print(f"⏱️  Total Duration: {duration}")
        print(f"📁 Total Fixed Test Files: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        if self.results['total_tests'] > 0:
            print(f"📈 Success Rate: {(self.results['passed'] / self.results['total_tests'] * 100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.results["test_files"]:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status} - {result['name']}")
        
        print("\n🎯 Key Improvements:")
        print("   ✅ Handles popups and modals automatically")
        print("   ✅ Dismisses dialogs and overlays")
        print("   ✅ Better timeout handling")
        print("   ✅ No more infinite loops")
        print("   ✅ Ready-to-run test scripts")
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = f"fixed_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
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
    """Main function to run all fixed tests"""
    runner = FixedTestRunner()
    runner.run_all_fixed_tests()

if __name__ == "__main__":
    main() 