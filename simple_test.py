#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/home/kevin/Projects/Llama-GPU')
os.makedirs('logs', exist_ok=True)

# Test the plugin manager step by step
print("Testing plugin manager imports and functionality...")

try:
    print("1. Importing PluginManager...")
    from src.plugin_manager import PluginManager
    print("   ✓ Success")
    
    print("2. Creating PluginManager instance...")
    pm = PluginManager()
    print("   ✓ Success")
    
    print("3. Testing list_plugins()...")
    plugins = pm.list_plugins()
    print(f"   ✓ Result: {plugins}")
    
    print("4. Testing scan_available_plugins()...")
    available = pm.scan_available_plugins()
    print(f"   ✓ Result: {available}")
    
    print("5. Testing get_plugin() with non-existent plugin...")
    plugin = pm.get_plugin("nonexistent")
    print(f"   ✓ Result: {plugin}")
    
    print("6. Testing get_plugin_metadata() with non-existent plugin...")
    metadata = pm.get_plugin_metadata("nonexistent")
    print(f"   ✓ Result: {metadata}")
    
    print("7. Testing validate_plugin() with non-existent plugin...")
    valid = pm.validate_plugin("nonexistent")
    print(f"   ✓ Result: {valid}")
    
    print("8. Testing get_plugin_status() with non-existent plugin...")
    status = pm.get_plugin_status("nonexistent")
    print(f"   ✓ Result: {status}")
    
    print("9. Testing is_plugin_compatible() with non-existent plugin...")
    compatible = pm.is_plugin_compatible("nonexistent", "1.0.0")
    print(f"   ✓ Result: {compatible}")
    
    print("10. Testing load_plugin() with invalid module...")
    result = pm.load_plugin("test", "invalid.module.path")
    print(f"   ✓ Result: {result}")
    
    print("11. Testing unload_plugin() with non-existent plugin...")
    result = pm.unload_plugin("nonexistent")
    print(f"   ✓ Result: {result}")
    
    print("12. Testing reload_plugin() with non-existent plugin...")
    result = pm.reload_plugin("nonexistent")
    print(f"   ✓ Result: {result}")
    
    print("\nAll tests passed! No runtime errors detected.")
    
except Exception as e:
    print(f"\n✗ Error detected: {e}")
    import traceback
    traceback.print_exc()
