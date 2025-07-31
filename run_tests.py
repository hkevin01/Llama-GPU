#!/usr/bin/env python3
import subprocess
import sys
import os

# Change to project directory
os.chdir('/home/kevin/Projects/Llama-GPU')

# Run the test script
result = subprocess.run([sys.executable, 'test_runtime_errors.py'], 
                       capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")
