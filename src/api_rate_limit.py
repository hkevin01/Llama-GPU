"""
API Rate Limiting and Validation
Implements rate limiting and request validation for API endpoints.
"""

import logging
from flask import Flask, request, jsonify
from functools import wraps
import time

logging.basicConfig(filename='logs/api_rate_limit.log', level=logging.INFO)
app = Flask(__name__)

RATE_LIMIT = 5  # requests per minute
user_access = {}

def rate_limited(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = request.remote_addr
        now = time.time()
        access = user_access.get(user, [])
        access = [t for t in access if now - t < 60]
        if len(access) >= RATE_LIMIT:
            logging.warning('Rate limit exceeded for user: %s', user)
            return jsonify({'error': 'rate limit exceeded'}), 429
        access.append(now)
        user_access[user] = access
        return f(*args, **kwargs)
    return decorated

@app.route('/validate', methods=['POST'])
@rate_limited
def validate():
    data = request.get_json()
    if not data or 'input' not in data:
        logging.error('Invalid request: %s', data)
        return jsonify({'error': 'invalid request'}), 400
    return jsonify({'status': 'valid', 'input': data['input']})

if __name__ == '__main__':
    app.run(port=5003)
