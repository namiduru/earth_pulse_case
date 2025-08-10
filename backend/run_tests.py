#!/usr/bin/env python3
"""
Test runner script for the FileDrive API backend.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Command not found: {command[0]}")
        print("Please install the required dependencies:")
        print("pip install -r requirements-test.txt")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run FileDrive API backend tests")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "coverage", "fast"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--file",
        help="Run tests from specific file"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("❌ Tests directory not found. Please run this script from the backend directory.")
        sys.exit(1)
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    if args.file:
        pytest_cmd.append(args.file)
    
    # Add markers based on test type
    if args.type == "unit":
        pytest_cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        pytest_cmd.extend(["-m", "integration"])
    elif args.type == "fast":
        pytest_cmd.extend(["-m", "not slow"])
    elif args.type == "coverage":
        pytest_cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    # Run the tests
    success = run_command(pytest_cmd, f"Running {args.type} tests")
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()


