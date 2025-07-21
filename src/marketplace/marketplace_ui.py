"""
Plugin Marketplace UI
Flask blueprint for plugin discovery, install, and update.
"""
from flask import Blueprint, request, jsonify
from src.plugin_marketplace import PluginMarketplace

marketplace_ui = Blueprint('marketplace_ui', __name__)
pm = PluginMarketplace()

@marketplace_ui.route('/marketplace/plugins', methods=['GET'])
def discover_plugins():
    return jsonify({'plugins': pm.discover_plugins()})

@marketplace_ui.route('/marketplace/plugins/install', methods=['POST'])
def install_plugin():
    data = request.get_json()
    name = data.get('name')
    result = pm.install_plugin(name)
    return jsonify({'installed': result})

@marketplace_ui.route('/marketplace/plugins/update', methods=['POST'])
def update_plugin():
    data = request.get_json()
    name = data.get('name')
    result = pm.update_plugin(name)
    return jsonify({'updated': result})
