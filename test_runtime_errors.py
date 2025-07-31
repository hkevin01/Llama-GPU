#!/usr/bin/env python3
"""
Runtime Error Detection Script
Tests the plugin manager and related modules to catch AttributeError, NameError, ImportError
"""

import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_plugin_manager_imports():
    """Test importing plugin_manager and all its dependencies"""
    try:
        print("Testing plugin_manager imports...")
        from plugin_manager import PluginManager
        print("✓ PluginManager imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing PluginManager: {e}")
        traceback.print_exc()
        return False

def test_plugin_manager_instantiation():
    """Test creating PluginManager instance"""
    try:
        print("\nTesting PluginManager instantiation...")
        from plugin_manager import PluginManager
        pm = PluginManager()
        print("✓ PluginManager instantiated successfully")
        return pm
    except Exception as e:
        print(f"✗ Error instantiating PluginManager: {e}")
        traceback.print_exc()
        return None

def test_plugin_manager_methods(pm):
    """Test all PluginManager methods"""
    if not pm:
        return False
    
    try:
        print("\nTesting PluginManager methods...")
        
        # Test list_plugins
        plugins = pm.list_plugins()
        print(f"✓ list_plugins(): {plugins}")
        
        # Test scan_available_plugins
        available = pm.scan_available_plugins()
        print(f"✓ scan_available_plugins(): {available}")
        
        # Test get_plugin (non-existent)
        plugin = pm.get_plugin("nonexistent")
        print(f"✓ get_plugin('nonexistent'): {plugin}")
        
        # Test validate_plugin (non-existent)
        valid = pm.validate_plugin("nonexistent")
        print(f"✓ validate_plugin('nonexistent'): {valid}")
        
        # Test get_plugin_status (non-existent)
        status = pm.get_plugin_status("nonexistent")
        print(f"✓ get_plugin_status('nonexistent'): {status}")
        
        # Test get_plugin_metadata (non-existent)
        metadata = pm.get_plugin_metadata("nonexistent")
        print(f"✓ get_plugin_metadata('nonexistent'): {metadata}")
        
        # Test is_plugin_compatible (non-existent)
        compatible = pm.is_plugin_compatible("nonexistent", "1.0.0")
        print(f"✓ is_plugin_compatible('nonexistent', '1.0.0'): {compatible}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing PluginManager methods: {e}")
        traceback.print_exc()
        return False

def test_individual_imports():
    """Test importing individual utility modules"""
    modules_to_test = [
        'src.utils.plugin_utils',
        'src.utils.error_handler',
        'src.utils.plugin_metadata',
        'src.utils.plugin_discovery',
        'src.utils.plugin_dependency',
        'src.utils.plugin_events',
        'src.utils.plugin_version'
    ]
    
    print("\nTesting individual utility imports...")
    results = {}
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
            results[module] = True
        except Exception as e:
            print(f"✗ Error importing {module}: {e}")
            traceback.print_exc()
            results[module] = False
    
    return results

if __name__ == "__main__":
    print("=== Runtime Error Detection Test ===")
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Test individual imports first
    import_results = test_individual_imports()
    
    # Test plugin manager
    if test_plugin_manager_imports():
        pm = test_plugin_manager_instantiation()
        test_plugin_manager_methods(pm)
    
    print("\n=== Test Complete ===")
