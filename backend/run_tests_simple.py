#!/usr/bin/env python3
"""
Simple test runner that sets up the environment properly.
"""

import os
import sys
import subprocess

def main():
    """Run tests with proper environment setup."""
    # Set environment variables for testing
    os.environ["TESTING"] = "true"
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test"
    os.environ["MINIO_ENDPOINT"] = "localhost:9000"
    os.environ["MINIO_ACCESS_KEY"] = "test"
    os.environ["MINIO_SECRET_KEY_VALUE"] = "test"
    
    # Run pytest with specific options
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--maxfail=5",
        "--disable-warnings",
        "--timeout=30"
    ]
    
    # Add test files if specified
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    else:
        cmd.append("tests/")
    
    print("Running tests with command:", " ".join(cmd))
    print("Environment variables set for testing")
    
    try:
        result = subprocess.run(cmd, cwd=".", timeout=60)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("Tests timed out after 60 seconds")
        return 1
    except KeyboardInterrupt:
        print("Tests interrupted by user")
        return 1

if __name__ == "__main__":
    exit(main())


