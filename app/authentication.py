from flask import request, jsonify
from functools import wraps
from app.config import Config  # Import the Config class

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Retrieve token from the request headers
        token = request.headers.get('Authorization')

        # Check if token matches the static API token
        if not token or token != f"Bearer {Config.API_TOKEN}":
            return jsonify({'error': 'Unauthorized'}), 403

        return f(*args, **kwargs)
    return decorated_function
