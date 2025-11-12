#!/usr/bin/env python3
"""Quick test of sudo executor."""

import sys
import getpass

sys.path.insert(0, "/home/kevin/Projects/Llama-GPU")

from tools.execution.sudo_executor import SudoExecutor

def main():
    print("=== Sudo Executor Test ===\n")
    
    # Get password once
    password = getpass.getpass("Enter sudo password: ")
    
    # Create executor with password
    executor = SudoExecutor(password=password, cache_password=True)
    
    # Test 1: Verify access
    print("\n1️⃣  Testing sudo verification...")
    if executor.verify_sudo_access():
        print("✅ Sudo access verified!\n")
    else:
        print("❌ Sudo verification failed\n")
        return 1
    
    # Test 2: Simple command
    print("2️⃣  Testing simple sudo command (whoami)...")
    result = executor.execute("sudo whoami", confirm=False)
    print(f"   Result: {result.success}")
    print(f"   Output: {result.output.strip()}")
    print(f"   Exit code: {result.exit_code}\n")
    
    # Test 3: System command
    print("3️⃣  Testing system info command...")
    result = executor.execute("sudo systemctl --version | head -1", confirm=False)
    print(f"   Result: {result.success}")
    print(f"   Output: {result.output.strip()[:100]}")
    print(f"   Exit code: {result.exit_code}\n")
    
    print("=== All tests complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
