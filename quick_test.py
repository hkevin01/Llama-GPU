import sys
import os
sys.path.insert(0, '/home/kevin/Projects/Llama-GPU')
os.makedirs('logs', exist_ok=True)

print("Testing plugin manager imports...")

try:
    from src.plugin_manager import PluginManager
    print("✓ PluginManager imported")
    
    pm = PluginManager()
    print("✓ PluginManager instantiated")
    
    result = pm.list_plugins()
    print(f"✓ list_plugins(): {result}")
    
    result = pm.scan_available_plugins()
    print(f"✓ scan_available_plugins(): {result}")
    
    print("✅ No runtime errors found!")
    
except Exception as e:
    print(f"❌ Runtime error: {e}")
    import traceback
    traceback.print_exc()
