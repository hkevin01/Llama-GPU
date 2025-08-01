"""
Plugin Marketplace Web UI
Provides a simple Flask-based UI for plugin discovery, install, and update.
"""

import logging
from flask import Flask, render_template_string, request, redirect, url_for
from src.plugin_marketplace import PluginMarketplace
from src.utils.config_manager import ConfigManager
from src.utils.role_manager import RoleManager

logging.basicConfig(filename='logs/plugin_marketplace_ui.log', level=logging.INFO)
app = Flask(__name__)
marketplace = PluginMarketplace()
ui_config = ConfigManager().load_yaml('config/plugin_marketplace_config.yaml')
role_manager = RoleManager()

TEMPLATE = """
<html>
<head><title>Plugin Marketplace</title></head>
<body>
<h1>Available Plugins</h1>
<ul>
{% for plugin in plugins %}
  <li>{{ plugin }} <a href="/install/{{ plugin }}">Install</a> <a href="/update/{{ plugin }}">Update</a> <a href="/remove/{{ plugin }}">Remove</a></li>
{% endfor %}
</ul>
</body>
</html>
"""

@app.route('/')
def index():
    plugins = marketplace.discover_plugins()
    return render_template_string(TEMPLATE, plugins=plugins)

@app.route('/install/<plugin>', methods=['POST'])
def install(plugin):
    username = request.form.get('username')
    if not role_manager.has_permission(username, 'manage_plugins'):
        return {'error': 'authorization failed'}, 403
    marketplace.install_plugin(plugin)
    return redirect(url_for('index'))

@app.route('/update/<plugin>')
def update(plugin):
    marketplace.update_plugin(plugin)
    return redirect(url_for('index'))

@app.route('/remove/<plugin>')
def remove(plugin):
    if plugin in marketplace.installed_plugins:
        marketplace.installed_plugins.remove(plugin)
        logging.info('Removed plugin: %s', plugin)
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(port=5004)
