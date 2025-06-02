#!/usr/bin/env python3
"""
Run all tests and show comprehensive results
"""
import subprocess
import sys


def run_pytest_tests():
    """Run the existing pytest suite"""
    print("=== Running Existing Pytest Suite ===\n")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", ".", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd="/workspaces/fastapi-template/tests",
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"Exit code: {result.returncode}")
        return result.returncode == 0

    except Exception as e:
        print(f"Error running pytest: {e}")
        return False


def run_performance_test():
    """Run the rule-based performance test"""
    print("\n" + "=" * 60)
    print("=== Running Rule-Based Performance Test ===\n")

    try:
        result = subprocess.run(
            [sys.executable, "test_rule_based_performance.py"],
            cwd="/workspaces/fastapi-template",
        )

        return result.returncode == 0

    except Exception as e:
        print(f"Error running performance test: {e}")
        return False


if __name__ == "__main__":
    print("Running comprehensive test suite...\n")

    # Run pytest tests first
    pytest_success = run_pytest_tests()

    # Run performance tests
    performance_success = run_performance_test()

    print("\n" + "=" * 60)
    print("=== FINAL SUMMARY ===")
    print(f"Pytest Tests: {'✓ PASSED' if pytest_success else '✗ FAILED'}")
    print(f"Performance Test: {'✓ PASSED' if performance_success else '✗ FAILED'}")

    if pytest_success and performance_success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n⚠️  Some tests failed. Check output above for details.")
        sys.exit(1)
