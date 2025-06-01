#!/usr/bin/env python3
"""
Quick script to run just the rule-based performance test
"""
import subprocess
import sys

if __name__ == "__main__":
    print("Running Rule-Based Classification Performance Test...\n")

    try:
        result = subprocess.run(
            [sys.executable, "test_rule_based_performance.py"],
            cwd="/workspaces/fastapi-template",
        )

        if result.returncode == 0:
            print("\n✓ Performance test completed successfully!")
        else:
            print("\n✗ Performance test failed!")
            sys.exit(1)

    except Exception as e:
        print(f"Error running test: {e}")
        sys.exit(1)
