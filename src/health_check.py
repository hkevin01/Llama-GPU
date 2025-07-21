"""
Health Check Endpoint
Provides a simple Flask endpoint for service health monitoring.
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=5050)
