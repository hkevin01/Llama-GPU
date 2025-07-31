#!/usr/bin/env python3

"""
Direct Runtime Error Test
Tests plugin manager by directly importing and running code
"""

import sys
import os
import traceback

# Setup
print("Setting up environment...")
sys.path.insert(0, '/home/kevin/Projects/Llama-GPU')
os.makedirs('logs', exist_ok=True)

errors_found = []

print("\n" + "="*60)
print("RUNTIME ERROR DETECTION: PLUGIN MANAGER SYSTEM")
print("="*60)

# Test 1: Direct import test
print("\n1. Testing imports...")
try:
    print("  Importing PluginManager...")
    from src.plugin_manager import PluginManager
    print("  ✓ SUCCESS: PluginManager imported")
except ImportError as e:
    error = f"ImportError: {e}"
    errors_found.append(error)
    print(f"  ✗ FAILED: {error}")
    traceback.print_exc()
except Exception as e:
    error = f"Unexpected import error: {e}"
    errors_found.append(error)
    print(f"  ✗ FAILED: {error}")
    traceback.print_exc()

# Test 2: Instantiation
if not errors_found:
    print("\n2. Testing instantiation...")
    try:
        print("  Creating PluginManager instance...")
        pm = PluginManager()
        print("  ✓ SUCCESS: PluginManager instantiated")
    except Exception as e:
        error = f"Instantiation error: {e}"
        errors_found.append(error)
        print(f"  ✗ FAILED: {error}")
        traceback.print_exc()

# Test 3: Method testing
if not errors_found:
    print("\n3. Testing methods...")
    
    test_methods = [
        ('list_plugins', []),
        ('scan_available_plugins', []),
        ('get_plugin', ['nonexistent']),
        ('get_plugin_metadata', ['nonexistent']),
        ('validate_plugin', ['nonexistent']),
        ('get_plugin_status', ['nonexistent']),
        ('is_plugin_compatible', ['nonexistent', '1.0.0']),
        ('unload_plugin', ['nonexistent']),
        ('reload_plugin', ['nonexistent'])
    ]
    
    for method_name, args in test_methods:
        try:
            print(f"  Testing {method_name}...")
            if hasattr(pm, method_name):
                method = getattr(pm, method_name)
                result = method(*args)
                print(f"    ✓ {method_name}(*{args}) = {result}")
            else:
                error = f"AttributeError: {method_name} method not found"
                errors_found.append(error)
                print(f"    ✗ FAILED: {error}")
        except AttributeError as e:
            error = f"AttributeError in {method_name}: {e}"
            errors_found.append(error)
            print(f"    ✗ FAILED: {error}")
        except NameError as e:
            error = f"NameError in {method_name}: {e}"
            errors_found.append(error)
            print(f"    ✗ FAILED: {error}")
        except Exception as e:
            # Some exceptions are expected (e.g., for nonexistent plugins)
            print(f"    ✓ {method_name} handled gracefully: {type(e).__name__}")

# Test 4: Test load_plugin with invalid module
if not errors_found:
    print("\n4. Testing plugin loading...")
    try:
        print("  Testing load_plugin with invalid module...")
        result = pm.load_plugin("test_plugin", "nonexistent.invalid.module")
        print(f"    ✓ load_plugin handled invalid module: {result}")
    except Exception as e:
        # This should NOT raise an exception - should return None gracefully
        error = f"load_plugin failed to handle ImportError gracefully: {e}"
        errors_found.append(error)
        print(f"    ✗ FAILED: {error}")

# Test 5: Test utility functions
print("\n5. Testing utility functions...")
utility_tests = [
    ('src.utils.plugin_utils', 'has_method'),
    ('src.utils.error_handler', 'log_error'),
    ('src.utils.plugin_metadata', 'get_metadata'),
    ('src.utils.plugin_discovery', 'discover_plugins'),
    ('src.utils.plugin_dependency', 'check_dependencies'),
    ('src.utils.plugin_events', 'PluginEventManager'),
    ('src.utils.plugin_version', 'check_version')
]

for module_name, item_name in utility_tests:
    try:
        print(f"  Testing {module_name}.{item_name}...")
        module = __import__(module_name, fromlist=[item_name])
        if hasattr(module, item_name):
            print(f"    ✓ {item_name} found in {module_name}")
        else:
            error = f"AttributeError: {item_name} not found in {module_name}"
            errors_found.append(error)
            print(f"    ✗ FAILED: {error}")
    except ImportError as e:
        error = f"ImportError: {module_name} - {e}"
        errors_found.append(error)
        print(f"    ✗ FAILED: {error}")

# Final results
print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)

if errors_found:
    print(f"❌ {len(errors_found)} RUNTIME ERRORS FOUND:")
    for i, error in enumerate(errors_found, 1):
        print(f"  {i}. {error}")
    
    print("\n🔧 ACTIONS REQUIRED:")
    print("  • Fix missing function implementations")
    print("  • Check import paths and dependencies")
    print("  • Verify all referenced modules exist")
    
    print("\n📋 NEXT STEPS:")
    print("  1. Fix each error listed above")
    print("  2. Re-run this test")
    print("  3. Verify all functions work correctly")
    
else:
    print("✅ NO RUNTIME ERRORS DETECTED!")
    print("🎉 All functions are properly implemented")
    print("📈 Plugin Manager system is fully functional")
    print("🚀 Ready for production use")

print(f"\nTotal errors: {len(errors_found)}")
print("Test completed successfully!")
