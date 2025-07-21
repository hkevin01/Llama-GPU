"""
Dashboard Plugin Management UI
Flask blueprint for managing plugins via dashboard.
"""
from flask import Blueprint, request, jsonify
from src.plugin_manager import PluginManager

plugin_ui = Blueprint('plugin_ui', __name__)
pm = PluginManager()

@plugin_ui.route('/dashboard/plugins', methods=['GET'])
def list_plugins():
    return jsonify({'plugins': pm.list_plugins()})

@plugin_ui.route('/dashboard/plugins/load', methods=['POST'])
def load_plugin():
    data = request.get_json()
    name = data.get('name')
    path = data.get('path')
    result = pm.load_plugin(name, path)
    return jsonify({'loaded': bool(result)})

@plugin_ui.route('/dashboard/plugins/unload', methods=['POST'])
def unload_plugin():
    data = request.get_json()
    name = data.get('name')
    result = pm.unload_plugin(name)
    return jsonify({'unloaded': result})
