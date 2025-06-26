#!/usr/bin/env python3
"""
Test runner for all Incidenter tests

Runs all test files in the tests directory with proper error handling
and categorization of test types.
"""

import os
import sys
import subprocess
from pathlib import Path
import socket


def run_test(test_file):
    """Run a single test file and return the result"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_file}")
    print(f"{'='*60}")

    try:
        # Change to parent directory to run tests from project root
        parent_dir = Path(__file__).parent.parent
        result = subprocess.run(
            [sys.executable, f"tests/{test_file}"],
            cwd=parent_dir,
            capture_output=False,  # Show output in real-time
            text=True,
        )

        if result.returncode == 0:
            print(f"✅ {test_file} passed")
            return True
        else:
            print(f"❌ {test_file} failed with return code {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Incidenter Test Suite")
    print("Running all tests in the tests directory")

    # Find all test files
    tests_dir = Path(__file__).parent
    test_files = [
        f
        for f in os.listdir(tests_dir)
        if f.startswith("test_") and f.endswith(".py") and f != "run_all_tests.py"
    ]

    # Separate tests that require special setup
    web_tests = ["test_web_interface.py"]
    standard_tests = [f for f in test_files if f not in web_tests]

    if not test_files:
        print("❌ No test files found")
        return 1

    print(f"Found {len(test_files)} test files:")
    print(f"  Standard tests: {len(standard_tests)}")
    print(f"  Web tests (require server): {len(web_tests)}")

    for test_file in test_files:
        print(f"  - {test_file}")

    # Run standard tests first
    passed = 0
    failed = 0

    print(f"\n{'='*60}")
    print("🧪 Running Standard Tests")
    print(f"{'='*60}")

    for test_file in standard_tests:
        if run_test(test_file):
            passed += 1
        else:
            failed += 1

    # Web tests require special handling
    if web_tests:
        print(f"\n{'='*60}")
        print("🌐 Web Interface Tests")
        print(f"{'='*60}")
        print("⚠️  Web tests require the Flask server to be running on port 5003")
        print("💡 Start server: python server/app.py")
        print("🔍 Checking for Flask server...")

        # Check if the server is running on port 5003
        def is_port_open(host, port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2)  # Increased timeout for better reliability
                    result = sock.connect_ex((host, port))
                    return result == 0
            except Exception:
                return False

        if is_port_open("127.0.0.1", 5003):
            print("✅ Flask server detected on port 5003. Running web tests...")
            for test_file in web_tests:
                if run_test(test_file):
                    passed += 1
                else:
                    failed += 1
        else:
            print("❌ Flask server not detected on port 5003")
            print("💡 To run web tests:")
            print("   1. Open a new terminal")
            print("   2. Run: cd /path/to/incidenter && python server/app.py")
            print("   3. Wait for 'Running on http://127.0.0.1:5003'")
            print("   4. Re-run this test suite")
            print("⏭️  Skipping web tests for now...")

            # Count skipped tests
            skipped = len(web_tests)
            print(f"📋 Skipped {skipped} web test(s)")

            # Optionally, you could ask the user if they want to wait
            print(
                "\n🤔 Would you like to wait 10 seconds for the server to start? (Ctrl+C to skip)"
            )
            try:
                import time

                for i in range(10, 0, -1):
                    print(f"⏰ Waiting {i} seconds...", end="\r")
                    time.sleep(1)
                print("🔍 Checking again...                    ")

                if is_port_open("127.0.0.1", 5003):
                    print("✅ Flask server now detected! Running web tests...")
                    for test_file in web_tests:
                        if run_test(test_file):
                            passed += 1
                        else:
                            failed += 1
                else:
                    print("❌ Still no server detected. Skipping web tests.")
            except KeyboardInterrupt:
                print("\n⏭️  Skipping wait. Web tests not run.")

    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📋 Total:  {passed + failed}")

    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
