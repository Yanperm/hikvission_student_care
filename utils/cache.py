from functools import wraps
from flask import request
import hashlib
import time

class SimpleCache:
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, time.time())
    
    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        self.cache.clear()

cache = SimpleCache(ttl=300)

def cached(ttl=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{f.__name__}:{request.path}:{request.args.to_dict()}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        return decorated_function
    return decorator
