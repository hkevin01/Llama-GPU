#!/usr/bin/env python3
"""
Comprehensive Runtime Error Test for Plugin Manager
"""
import sys
import os
import traceback

# Add project to Python path
project_root = '/home/kevin/Projects/Llama-GPU'
sys.path.insert(0, project_root)

# Create logs directory
os.makedirs('logs', exist_ok=True)

def test_all_imports():
    """Test all imports used by plugin_manager"""
    print("=== Testing all imports ===")
    
    modules = [
        ('importlib', None),
        ('logging', None),
        ('typing', 'Dict, Optional, Any, List'),
        ('src.utils.plugin_utils', 'has_method'),
        ('src.utils.error_handler', 'log_error'),
        ('src.utils.plugin_metadata', 'get_metadata'),
        ('src.utils.plugin_discovery', 'discover_plugins'),
        ('src.utils.plugin_dependency', 'check_dependencies'),
        ('src.utils.plugin_events', 'PluginEventManager'),
        ('src.utils.plugin_version', 'check_version'),
    ]
    
    for module_name, imports in modules:
        try:
            if imports:
                exec(f"from {module_name} import {imports}")
                print(f"✓ {module_name}: {imports}")
            else:
                exec(f"import {module_name}")
                print(f"✓ {module_name}")
        except Exception as e:
            print(f"✗ {module_name}: {e}")
            traceback.print_exc()

def test_plugin_manager_functionality():
    """Test PluginManager class and all its methods"""
    print("\n=== Testing PluginManager functionality ===")
    
    try:
        # Import and instantiate
        from src.plugin_manager import PluginManager
        pm = PluginManager()
        print("✓ PluginManager imported and instantiated")
        
        # Test list_plugins
        plugins = pm.list_plugins()
        print(f"✓ list_plugins(): {plugins}")
        
        # Test scan_available_plugins
        available = pm.scan_available_plugins()
        print(f"✓ scan_available_plugins(): {available}")
        
        # Test get_plugin with non-existent plugin
        result = pm.get_plugin("nonexistent")
        print(f"✓ get_plugin('nonexistent'): {result}")
        
        # Test unload_plugin with non-existent plugin
        result = pm.unload_plugin("nonexistent")
        print(f"✓ unload_plugin('nonexistent'): {result}")
        
        # Test reload_plugin with non-existent plugin
        result = pm.reload_plugin("nonexistent")
        print(f"✓ reload_plugin('nonexistent'): {result}")
        
        # Test get_plugin_metadata with non-existent plugin
        metadata = pm.get_plugin_metadata("nonexistent")
        print(f"✓ get_plugin_metadata('nonexistent'): {metadata}")
        
        # Test validate_plugin with non-existent plugin
        valid = pm.validate_plugin("nonexistent")
        print(f"✓ validate_plugin('nonexistent'): {valid}")
        
        # Test get_plugin_status with non-existent plugin
        status = pm.get_plugin_status("nonexistent")
        print(f"✓ get_plugin_status('nonexistent'): {status}")
        
        # Test is_plugin_compatible with non-existent plugin
        compatible = pm.is_plugin_compatible("nonexistent", "1.0.0")
        print(f"✓ is_plugin_compatible('nonexistent', '1.0.0'): {compatible}")
        
        # Test loading a plugin that doesn't exist
        plugin = pm.load_plugin("test_plugin", "nonexistent.module")
        print(f"✓ load_plugin('test_plugin', 'nonexistent.module'): {plugin}")
        
        return pm
        
    except Exception as e:
        print(f"✗ PluginManager test failed: {e}")
        traceback.print_exc()
        return None

def test_plugin_manager_edge_cases(pm):
    """Test edge cases and error handling"""
    if not pm:
        print("Skipping edge case tests - no PluginManager instance")
        return
        
    print("\n=== Testing edge cases ===")
    
    try:
        # Test empty string plugin name
        result = pm.get_plugin("")
        print(f"✓ get_plugin(''): {result}")
        
        # Test None plugin name (should handle gracefully)
        try:
            result = pm.get_plugin(None)
            print(f"✓ get_plugin(None): {result}")
        except Exception as e:
            print(f"✓ get_plugin(None) handled error: {e}")
        
        # Test very long plugin name
        long_name = "a" * 1000
        result = pm.get_plugin(long_name)
        print(f"✓ get_plugin(long_name): {result}")
        
        # Test special characters in plugin name
        special_name = "plugin!@#$%^&*()"
        result = pm.get_plugin(special_name)
        print(f"✓ get_plugin(special_chars): {result}")
        
    except Exception as e:
        print(f"✗ Edge case test failed: {e}")
        traceback.print_exc()

def test_concurrent_access(pm):
    """Test concurrent access to plugin manager"""
    if not pm:
        print("Skipping concurrent tests - no PluginManager instance")
        return
        
    print("\n=== Testing concurrent access ===")
    
    import threading
    import time
    
    def worker(worker_id):
        try:
            for i in range(5):
                plugins = pm.list_plugins()
                print(f"Worker {worker_id}: {len(plugins)} plugins")
                time.sleep(0.1)
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
    
    try:
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        print("✓ Concurrent access test completed")
        
    except Exception as e:
        print(f"✗ Concurrent access test failed: {e}")
        traceback.print_exc()

def main():
    """Main test function"""
    print("Starting comprehensive plugin manager tests...")
    
    # Test imports first
    test_all_imports()
    
    # Test basic functionality
    pm = test_plugin_manager_functionality()
    
    # Test edge cases
    test_plugin_manager_edge_cases(pm)
    
    # Test concurrent access
    test_concurrent_access(pm)
    
    print("\n=== Test Summary ===")
    print("All tests completed. Check output above for any failures.")

if __name__ == "__main__":
    main()
