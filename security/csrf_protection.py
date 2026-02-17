from flask_wtf.csrf import CSRFProtect
from functools import wraps
from flask import request, jsonify
import secrets

csrf = CSRFProtect()

def generate_csrf_token():
    return secrets.token_hex(32)

def csrf_exempt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    decorated_function._csrf_exempt = True
    return decorated_function
