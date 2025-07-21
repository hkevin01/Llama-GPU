"""
Plugin Loader CLI Utility
Allows command-line management of plugins (load, unload, list, validate).
"""
import argparse
from src.plugin_manager import PluginManager
from src.utils.plugin_discovery import discover_plugins

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plugin Loader CLI')
    parser.add_argument('action', choices=['list', 'load', 'unload', 'validate', 'metadata'])
    parser.add_argument('--name', type=str, help='Plugin name')
    parser.add_argument('--path', type=str, help='Plugin import path')
    args = parser.parse_args()

    pm = PluginManager()

    if args.action == 'list':
        print('Available plugins:', discover_plugins())
        print('Loaded plugins:', pm.list_plugins())
    elif args.action == 'load' and args.name and args.path:
        result = pm.load_plugin(args.name, args.path)
        print('Loaded:', bool(result))
    elif args.action == 'unload' and args.name:
        print('Unloaded:', pm.unload_plugin(args.name))
    elif args.action == 'validate' and args.name:
        print('Valid:', pm.validate_plugin(args.name))
    elif args.action == 'metadata' and args.name:
        print('Metadata:', pm.get_plugin_metadata(args.name))
    else:
        print('Invalid arguments. See --help.')

