"""
Web Dashboard Module
Basic Flask dashboard for monitoring and model management.
"""

from flask import Flask, render_template, request
import logging
from src.utils.role_manager import RoleManager

app = Flask(__name__)
logging.basicConfig(filename='logs/dashboard.log', level=logging.INFO)
role_manager = RoleManager()

@app.route('/')
def index():
    logging.info('Dashboard accessed')
    return '<h1>Llama-GPU Dashboard</h1><p>Status: Running</p>'

@app.route('/models')
def models():
    logging.info('Model list accessed')
    # Simulate model list
    return '<h2>Available Models</h2><ul><li>llama-base</li><li>llama-quant</li></ul>'

@app.route('/deploy', methods=['POST'])
def deploy():
    model = request.form.get('model')
    logging.info(f'Deploy requested for model: {model}')
    return f'<p>Deployment started for model: {model}</p>'

@app.route('/plugins')
def list_plugins():
    from src.plugin_manager import PluginManager
    pm = PluginManager()
    return {'plugins': list(pm.plugins.keys())}

@app.route('/benchmark', methods=['POST'])
def run_benchmark():
    from src.benchmark_utils import benchmark_model
    # Dummy model and input for demonstration
    def dummy_model(x): return x * 2
    avg, times = benchmark_model(dummy_model, 5, runs=3)
    return {'average_time': avg, 'times': times}

@app.route('/manage', methods=['POST'])
def manage():
    data = request.get_json()
    username = data.get('username')
    action = data.get('action')
    if not role_manager.has_permission(username, action):
        return {'error': 'authorization failed'}, 403
    # ...existing management logic...
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(debug=True)
