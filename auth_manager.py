import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session
import secrets

class AuthManager:
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.users = {
            'admin': {
                'password': self.hash_password('admin123'),
                'role': 'admin',
                'name': 'System Administrator'
            },
            'teacher': {
                'password': self.hash_password('teacher123'),
                'role': 'teacher',
                'name': 'Teacher User'
            }
        }
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, username, password):
        if username in self.users:
            return self.users[username]['password'] == self.hash_password(password)
        return False
    
    def generate_token(self, username):
        payload = {
            'username': username,
            'role': self.users[username]['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def require_auth(self, required_role=None):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                from flask import redirect, url_for
                
                token = request.headers.get('Authorization')
                if token and token.startswith('Bearer '):
                    token = token[7:]
                else:
                    token = session.get('token')
                
                if not token:
                    if request.is_json:
                        return jsonify({'error': 'Authentication required'}), 401
                    return redirect(url_for('login'))
                
                payload = self.verify_token(token)
                if not payload:
                    if request.is_json:
                        return jsonify({'error': 'Invalid or expired token'}), 401
                    return redirect(url_for('login'))
                
                if required_role and payload['role'] != required_role and payload['role'] != 'admin':
                    if request.is_json:
                        return jsonify({'error': 'Insufficient permissions'}), 403
                    return redirect(url_for('login'))
                
                request.user = payload
                return f(*args, **kwargs)
            return decorated_function
        return decorator

auth_manager = AuthManager()