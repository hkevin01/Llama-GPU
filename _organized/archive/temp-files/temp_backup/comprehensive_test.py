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

def test_utility_functions():
    """Test individual utility functions"""
    print("\n=== Testing utility functions ===")
    
    try:
        # Test plugin_utils
        from src.utils.plugin_utils import has_method
        
        class TestObj:
            def test_method(self):
                pass
        
        obj = TestObj()
        result = has_method(obj, 'test_method')
        print(f"✓ has_method(obj, 'test_method'): {result}")
        
        result = has_method(obj, 'nonexistent_method')
        print(f"✓ has_method(obj, 'nonexistent_method'): {result}")
        
        # Test error_handler
        from src.utils.error_handler import log_error
        log_error("Test error message")
        print("✓ log_error() executed")
        
        # Test plugin_metadata
        from src.utils.plugin_metadata import get_metadata
        
        class MockPlugin:
            metadata = {'name': 'test', 'version': '1.0.0'}
        
        plugin = MockPlugin()
        metadata = get_metadata(plugin)
        print(f"✓ get_metadata(plugin): {metadata}")
        
        metadata = get_metadata(object())  # Object without metadata
        print(f"✓ get_metadata(no_metadata_obj): {metadata}")
        
        # Test plugin_dependency
        from src.utils.plugin_dependency import check_dependencies
        
        result = check_dependencies(['sys', 'os'])  # Should exist
        print(f"✓ check_dependencies(['sys', 'os']): {result}")
        
        result = check_dependencies(['nonexistent_module'])  # Should not exist
        print(f"✓ check_dependencies(['nonexistent_module']): {result}")
        
        # Test plugin_events
        from src.utils.plugin_events import PluginEventManager
        
        events = PluginEventManager()
        
        def test_hook(*args, **kwargs):
            print(f"   Hook called with args={args}, kwargs={kwargs}")
        
        events.register_hook('pre_load', test_hook)
        events.dispatch('pre_load', name='test', path='test.py')
        print("✓ PluginEventManager: register_hook and dispatch")
        
        # Test plugin_version
        from src.utils.plugin_version import check_version
        
        metadata = {'version': '1.0.0'}
        result = check_version(metadata, '1.0.0')
        print(f"✓ check_version(metadata, '1.0.0'): {result}")
        
        result = check_version(metadata, '2.0.0')
        print(f"✓ check_version(metadata, '2.0.0'): {result}")
        
        result = check_version({}, '1.0.0')  # Empty metadata
        print(f"✓ check_version({{}}, '1.0.0'): {result}")
        
    except Exception as e:
        print(f"✗ Utility function test failed: {e}")
        traceback.print_exc()

def test_edge_cases():
    """Test edge cases that might cause runtime errors"""
    print("\n=== Testing edge cases ===")
    
    try:
        from src.plugin_manager import PluginManager
        pm = PluginManager()
        
        # Test with None values
        result = pm.get_plugin(None)
        print(f"✓ get_plugin(None): {result}")
        
        # Test with empty string
        result = pm.get_plugin("")
        print(f"✓ get_plugin(''): {result}")
        
        # Test loading with invalid paths
        result = pm.load_plugin("test", "")
        print(f"✓ load_plugin('test', ''): {result}")
        
        result = pm.load_plugin("test", None)
        print(f"✗ load_plugin('test', None): Should fail!")
        
    except TypeError as e:
        print(f"✓ load_plugin('test', None): Correctly failed with TypeError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error in edge case testing: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting comprehensive runtime error test...")
    
    test_all_imports()
    pm = test_plugin_manager_functionality()
    test_utility_functions()
    test_edge_cases()
    
    print("\n=== Test Summary ===")
    print("All tests completed. Check above for any ✗ marks indicating errors.")
