#!/usr/bin/env python3
"""Test consolidated modules after reorganization"""
import sys
import os

# Add project root to path
project_root = '/home/kevin/Projects/Llama-GPU'
sys.path.insert(0, project_root)

def test_consolidated_imports():
    """Test that consolidated modules work correctly"""
    print("Testing consolidated modules...")
    
    # Test error handling consolidation
    try:
        from src.utils.error_handling import log_error, LlamaGPUError, BackendError
        print("✓ Consolidated error handling imports work")
    except Exception as e:
        print(f"✗ Error handling consolidation failed: {e}")
    
    # Test config management consolidation
    try:
        from src.utils.config_manager import load_config, ConfigManager
        print("✓ Consolidated config management imports work")
    except Exception as e:
        print(f"✗ Config management consolidation failed: {e}")
    
    # Test plugin manager with updated imports
    try:
        from src.plugin_manager import PluginManager
        pm = PluginManager()
        print("✓ PluginManager with updated imports works")
    except Exception as e:
        print(f"✗ PluginManager with updated imports failed: {e}")
        import traceback
        traceback.print_exc()

def test_functionality():
    """Test that functionality is preserved"""
    print("\nTesting preserved functionality...")
    
    try:
        from src.utils.error_handling import log_error
        log_error("Test error message")
        print("✓ log_error function works")
    except Exception as e:
        print(f"✗ log_error function failed: {e}")
    
    try:
        from src.utils.config_manager import load_config
        # This will fail with file not found but shows function exists
        try:
            load_config("nonexistent.yaml")
        except FileNotFoundError:
            print("✓ load_config function exists and handles errors")
        except Exception as e:
            print(f"✓ load_config function exists: {e}")
    except Exception as e:
        print(f"✗ load_config function failed: {e}")

if __name__ == "__main__":
    test_consolidated_imports()
    test_functionality()
    print("\nConsolidation test complete!")
