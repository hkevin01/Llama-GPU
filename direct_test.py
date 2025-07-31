#!/usr/bin/env python3
"""Direct import test to catch errors"""
import sys
import os

# Add project root to path
project_root = '/home/kevin/Projects/Llama-GPU'
sys.path.insert(0, project_root)

# Test imports one by one
print("Testing imports...")

try:
    print("1. Testing plugin_utils...")
    from src.utils.plugin_utils import has_method
    print("   ✓ has_method imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("2. Testing error_handler...")
    from src.utils.error_handler import log_error
    print("   ✓ log_error imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("3. Testing plugin_metadata...")
    from src.utils.plugin_metadata import get_metadata
    print("   ✓ get_metadata imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("4. Testing plugin_discovery...")
    from src.utils.plugin_discovery import discover_plugins
    print("   ✓ discover_plugins imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("5. Testing plugin_dependency...")
    from src.utils.plugin_dependency import check_dependencies
    print("   ✓ check_dependencies imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("6. Testing plugin_events...")
    from src.utils.plugin_events import PluginEventManager
    print("   ✓ PluginEventManager imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("7. Testing plugin_version...")
    from src.utils.plugin_version import check_version
    print("   ✓ check_version imported")
except Exception as e:
    print(f"   ✗ Error: {e}")

try:
    print("8. Testing plugin_manager...")
    from src.plugin_manager import PluginManager
    print("   ✓ PluginManager imported")
    
    # Test instantiation
    pm = PluginManager()
    print("   ✓ PluginManager instantiated")
    
    # Test basic methods
    plugins = pm.list_plugins()
    print(f"   ✓ list_plugins(): {plugins}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test complete!")
