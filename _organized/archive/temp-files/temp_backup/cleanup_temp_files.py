#!/usr/bin/env python3
"""Temporary test files cleanup script"""
import shutil
import os

# Files to move to backup
temp_files = [
    'comprehensive_test.py',
    'direct_test.py', 
    'final_runtime_test.py',
    'quick_test.py',
    'simple_test.py',
    'test_runtime_errors.py',
    'test_runtime_errors_final.py',
    'test_project_completion.py',
    'run_tests.py',
    'RUNTIME_ERROR_ANALYSIS.md',
    'RUNTIME_TESTING_COMPLETE.md', 
    'DOCUMENTATION_VERIFICATION_TODO.md',
    'FINAL_VERIFICATION_REPORT.md',
    'debug_output.txt'
]

backup_dir = 'temp_backup'
moved_files = []

for file in temp_files:
    if os.path.exists(file):
        try:
            shutil.move(file, f'{backup_dir}/{file}')
            moved_files.append(file)
            print(f"Moved {file} to {backup_dir}/")
        except Exception as e:
            print(f"Error moving {file}: {e}")

print(f"\nMoved {len(moved_files)} temporary files to backup")
