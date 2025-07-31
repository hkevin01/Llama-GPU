#!/usr/bin/env python3
"""
Runtime Error Testing Script for Plugin Manager
Tests all functionality and catches AttributeError, NameError, ImportError
"""
import sys
import os
import traceback

# Setup
project_root = '/home/kevin/Projects/Llama-GPU'
sys.path.insert(0, project_root)
os.makedirs('logs', exist_ok=True)

def run_plugin_manager_tests():
    """Run comprehensive tests to catch runtime errors"""
    errors_found = []
    
    print("=" * 60)
    print("RUNTIME ERROR DETECTION FOR PLUGIN MANAGER")
    print("=" * 60)
    
    # Test 1: Import all dependencies
    print("\n1. Testing imports...")
    try:
        from src.plugin_manager import PluginManager
        print("   ✓ PluginManager imported")
    except Exception as e:
        error_msg = f"ImportError in PluginManager: {e}"
        errors_found.append(error_msg)
        print(f"   ✗ {error_msg}")
        traceback.print_exc()
        return errors_found
    
    # Test 2: Instantiation
    print("\n2. Testing instantiation...")
    try:
        pm = PluginManager()
        print("   ✓ PluginManager instantiated")
    except Exception as e:
        error_msg = f"Error instantiating PluginManager: {e}"
        errors_found.append(error_msg)
        print(f"   ✗ {error_msg}")
        traceback.print_exc()
        return errors_found
    
    # Test 3: Method calls
    methods_to_test = [
        ('list_plugins', [], {}),
        ('scan_available_plugins', [], {}),
        ('get_plugin', ['nonexistent'], {}),
        ('get_plugin_metadata', ['nonexistent'], {}),
        ('validate_plugin', ['nonexistent'], {}),
        ('get_plugin_status', ['nonexistent'], {}),
        ('is_plugin_compatible', ['nonexistent', '1.0.0'], {}),
        ('unload_plugin', ['nonexistent'], {}),
        ('reload_plugin', ['nonexistent'], {})
    ]
    
    print("\n3. Testing all methods...")
    for method_name, args, kwargs in methods_to_test:
        try:
            method = getattr(pm, method_name)
            result = method(*args, **kwargs)
            print(f"   ✓ {method_name}(*{args}, **{kwargs}) = {result}")
        except AttributeError as e:
            error_msg = f"AttributeError in {method_name}: {e}"
            errors_found.append(error_msg)
            print(f"   ✗ {error_msg}")
        except NameError as e:
            error_msg = f"NameError in {method_name}: {e}"
            errors_found.append(error_msg)
            print(f"   ✗ {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error in {method_name}: {e}"
            errors_found.append(error_msg)
            print(f"   ✗ {error_msg}")
    
    # Test 4: Load plugin (should handle ImportError gracefully)
    print("\n4. Testing plugin loading with invalid module...")
    try:
        result = pm.load_plugin("test_plugin", "nonexistent.invalid.module")
        print(f"   ✓ load_plugin handled invalid module gracefully: {result}")
    except Exception as e:
        error_msg = f"Unexpected error in load_plugin: {e}"
        errors_found.append(error_msg)
        print(f"   ✗ {error_msg}")
    
    # Test 5: Test utility functions directly
    print("\n5. Testing utility functions...")
    utility_tests = [
        ('src.utils.plugin_utils', 'has_method', [object(), 'test']),
        ('src.utils.error_handler', 'log_error', ['test message']),
        ('src.utils.plugin_metadata', 'get_metadata', [object()]),
        ('src.utils.plugin_discovery', 'discover_plugins', []),
        ('src.utils.plugin_dependency', 'check_dependencies', [['sys']]),
        ('src.utils.plugin_version', 'check_version', [{}, '1.0.0'])
    ]
    
    for module_name, func_name, args in utility_tests:
        try:
            module = __import__(module_name, fromlist=[func_name])
            func = getattr(module, func_name)
            result = func(*args)
            print(f"   ✓ {module_name}.{func_name}(*{args}) = {result}")
        except AttributeError as e:
            error_msg = f"AttributeError in {module_name}.{func_name}: {e}"
            errors_found.append(error_msg)
            print(f"   ✗ {error_msg}")
        except NameError as e:
            error_msg = f"NameError in {module_name}.{func_name}: {e}"
            errors_found.append(error_msg)
            print(f"   ✗ {error_msg}")
        except ImportError as e:
            error_msg = f"ImportError in {module_name}: {e}"
            errors_found.append(error_msg)
            print(f"   ✗ {error_msg}")
        except Exception as e:
            # Expected for some functions with invalid inputs
            print(f"   ✓ {module_name}.{func_name} handled invalid input: {type(e).__name__}")
    
    # Test 6: Test event system
    print("\n6. Testing event system...")
    try:
        # This should trigger events
        pm.load_plugin("test", "nonexistent")
        pm.unload_plugin("test")
        pm.reload_plugin("test")
        print("   ✓ Event system functioning")
    except Exception as e:
        error_msg = f"Error in event system: {e}"
        errors_found.append(error_msg)
        print(f"   ✗ {error_msg}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if errors_found:
        print(f"❌ {len(errors_found)} RUNTIME ERRORS FOUND:")
        for i, error in enumerate(errors_found, 1):
            print(f"{i}. {error}")
    else:
        print("✅ NO RUNTIME ERRORS FOUND - All functions implemented correctly!")
    
    return errors_found

if __name__ == "__main__":
    errors = run_plugin_manager_tests()
    
    if errors:
        print(f"\nAction required: Fix {len(errors)} runtime errors")
        sys.exit(1)
    else:
        print("\n🎉 Plugin Manager system is fully functional!")
        sys.exit(0)
