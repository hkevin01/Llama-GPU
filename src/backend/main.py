"""
Main Backend Entry Point
Handles model loading, inference, and API integration.
"""

import logging
from src.structured_logger import StructuredLogger
from src.model_compat import load_onnx_model, load_tf_model
from src.auth_manager import AuthManager
from flask import Flask, request, jsonify
from typing import Any
from src.utils.data_preprocessing import preprocess_input
from src.utils.role_manager import RoleManager

logger = StructuredLogger('backend', 'logs/backend.log')
app = Flask(__name__)
auth = AuthManager()
role_manager = RoleManager()

MODEL = None

@app.route('/load_model', methods=['POST'])
def load_model():
    data = request.get_json()
    model_type = data.get('type')
    path = data.get('path')
    try:
        if model_type == 'onnx':
            global MODEL
            MODEL = load_onnx_model(path)
            logger.info('ONNX model loaded', {'path': path})
        elif model_type == 'tf':
            MODEL = load_tf_model(path)
            logger.info('TensorFlow model loaded', {'path': path})
        else:
            logger.error('Unsupported model type', {'type': model_type})
            return jsonify({'error': 'unsupported model type'}), 400
        return jsonify({'status': 'model loaded', 'type': model_type})
    except Exception as e:
        logger.error('Model loading failed', {'error': str(e)})
        return jsonify({'error': 'model loading failed'}), 500

@app.route('/infer', methods=['POST'])
def infer():
    data = request.get_json()
    input_data = data.get('input')
    username = data.get('username')
    password = data.get('password')
    if not auth.authenticate(username, password):
        logger.error('Authentication failed', {'username': username})
        return jsonify({'error': 'authentication failed'}), 401
    if not role_manager.has_permission(username, 'infer'):
        logger.error('Authorization failed', {'username': username})
        return jsonify({'error': 'authorization failed'}), 403
    if MODEL is None:
        logger.error('No model loaded')
        return jsonify({'error': 'no model loaded'}), 400
    try:
        processed = preprocess_input(input_data)
        output = processed[::-1]  # Reverse string as mock
        logger.info('Inference successful', {'input': input_data, 'processed': processed, 'output': output})
        return jsonify({'output': output})
    except Exception as e:
        logger.error('Inference failed', {'error': str(e)})
        return jsonify({'error': 'inference failed'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=5000)
