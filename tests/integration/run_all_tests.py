#!/usr/bin/env python3
"""
Integration test runner for AutoSomnia platform.

This script runs all integration tests in the correct order and provides
a comprehensive summary of results.
"""

import asyncio
import sys
import subprocess
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class IntegrationTestRunner:
    """Runner for all integration tests."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        self.start_time = time.time()
    
    def run_sync_test(self, test_file: str, description: str) -> bool:
        """Run a synchronous test file."""
        print(f"\n{'='*60}")
        print(f"🧪 Running: {description}")
        print(f"📁 File: {test_file}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.test_dir / test_file)],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout for integration tests
            )
            
            # Print the output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            self.results[test_file] = {
                'success': success,
                'description': description,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            if success:
                print(f"✅ {description} - PASSED")
            else:
                print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT (120s)")
            self.results[test_file] = {
                'success': False,
                'description': description,
                'error': 'Timeout after 120 seconds'
            }
            return False
        except Exception as e:
            print(f"💥 {description} - ERROR: {e}")
            self.results[test_file] = {
                'success': False,
                'description': description,
                'error': str(e)
            }
            return False
    
    async def run_async_test(self, test_file: str, description: str) -> bool:
        """Run an async test file."""
        print(f"\n{'='*60}")
        print(f"🧪 Running: {description}")
        print(f"📁 File: {test_file}")
        print(f"{'='*60}")
        
        try:
            # Import and run the async test
            if test_file == "test_account_balance.py":
                from test_account_balance import main as test_main
                result = await test_main()
                
                success = result == 0
                self.results[test_file] = {
                    'success': success,
                    'description': description,
                    'return_code': result
                }
                
                if success:
                    print(f"✅ {description} - PASSED")
                else:
                    print(f"❌ {description} - FAILED")
                
                return success
            
        except Exception as e:
            print(f"💥 {description} - ERROR: {e}")
            self.results[test_file] = {
                'success': False,
                'description': description,
                'error': str(e)
            }
            return False
    
    def print_summary(self):
        """Print a comprehensive test summary."""
        end_time = time.time()
        duration = end_time - self.start_time
        
        print(f"\n{'='*80}")
        print("📊 INTEGRATION TEST SUMMARY")
        print(f"{'='*80}")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"🧪 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n{'='*80}")
        print("📋 DETAILED RESULTS")
        print(f"{'='*80}")
        
        for test_file, result in self.results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} | {test_file:<30} | {result['description']}")
            
            if not result['success'] and 'error' in result:
                print(f"     └─ Error: {result['error']}")
        
        if failed_tests == 0:
            print(f"\n🎉 All integration tests passed! The AutoSomnia platform is ready.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please check the configuration and services.")
        
        return failed_tests == 0
    
    async def run_all_tests(self):
        """Run all integration tests in the correct order."""
        print("🚀 AutoSomnia Integration Test Suite")
        print(f"📅 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Test directory: {self.test_dir}")
        
        # Test 1: Simple configuration and validation test
        self.run_sync_test(
            "test_simple_balance.py",
            "Configuration Validation & Address Derivation"
        )
        
        # Test 2: Full blockchain integration test
        await self.run_async_test(
            "test_account_balance.py",
            "Blockchain Connection & Balance Retrieval"
        )
        
        # Test 3: Exchange integration test (simple)
        exchange_simple_success = self.run_sync_test(
            "test_exchange_simple.py",
            "Exchange Service & Quote API (Simple)"
        )
        
        # Test 4: Exchange integration test (comprehensive)
        exchange_full_success = self.run_sync_test(
            "test_exchange_integration.py", 
            "Exchange Service & Quote API (Comprehensive)"
        )
        
        # Test 5: API integration test (if API is running)
        api_test_success = self.run_sync_test(
            "test_user_deletion.py",
            "API Integration & User Management"
        )
        
        if not api_test_success:
            print("\n⚠️  Note: API integration test failed.")
            print("   This is expected if the FastAPI backend is not running.")
            print("   Start the backend with: python app/main.py")
        
        if not exchange_simple_success or not exchange_full_success:
            print("\n⚠️  Note: Exchange integration tests failed.")
            print("   This may be due to blockchain connectivity issues.")
            print("   Check your RPC_URL configuration and network connection.")
        
        # Print comprehensive summary
        return self.print_summary()


async def main():
    """Main function to run all integration tests."""
    runner = IntegrationTestRunner()
    
    try:
        success = await runner.run_all_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Test run interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        return 1


if __name__ == "__main__":
    # Run the test suite
    exit_code = asyncio.run(main())
    exit(exit_code)


# Usage examples:
"""
# Run all integration tests
python tests/integration/run_all_tests.py

# Run with verbose output
python -v tests/integration/run_all_tests.py

# Run in a specific environment
PRIVATE_KEY=0x... RPC_URL=https://... python tests/integration/run_all_tests.py
"""