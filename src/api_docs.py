"""
API Documentation Module
Serves OpenAPI/Swagger docs for the project API.
"""

import logging
from flask import Flask, jsonify, request

logging.basicConfig(filename='logs/api_docs.log', level=logging.INFO)
app = Flask(__name__)

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Llama-GPU API",
        "version": "1.0.0"
    },
    "paths": {
        "/predict": {
            "post": {
                "summary": "Run inference on input data",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "object", "properties": {"input": {"type": "string"}}}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Inference result",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        },
        "/health": {
            "get": {
                "summary": "Health check",
                "responses": {
                    "200": {
                        "description": "Service is up and running",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        }
    }
}

@app.route('/openapi.json')
def get_openapi_spec():
    logging.info('Returned OpenAPI spec')
    return jsonify(OPENAPI_SPEC)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_text = data.get('input', '')
    # Example: Use a dummy model for demonstration
    result = {"output": input_text[::-1]}  # Reverse string as mock inference
    logging.info('Prediction requested: %s, result: %s', input_text, result)
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=5001)
