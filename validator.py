import re
from flask import request
import bleach

class InputValidator:
    @staticmethod
    def validate_student_id(student_id):
        if not student_id or len(student_id) < 3 or len(student_id) > 20:
            return False, "Student ID must be 3-20 characters"
        if not re.match(r'^[a-zA-Z0-9_-]+$', student_id):
            return False, "Student ID can only contain letters, numbers, underscore, and dash"
        return True, ""
    
    @staticmethod
    def validate_name(name):
        if not name or len(name) < 2 or len(name) > 100:
            return False, "Name must be 2-100 characters"
        # Allow letters, spaces, and common name characters
        if not re.match(r'^[a-zA-Z\u0e00-\u0e7f\s\'-\.]+$', name):
            return False, "Name contains invalid characters"
        return True, ""
    
    @staticmethod
    def sanitize_input(text):
        if not text:
            return ""
        # Remove HTML tags and dangerous characters
        return bleach.clean(text.strip(), tags=[], strip=True)
    
    @staticmethod
    def validate_image_data(image_data):
        if not image_data:
            return False, "Image data is required"
        if not image_data.startswith('data:image/'):
            return False, "Invalid image format"
        if len(image_data) > 5 * 1024 * 1024:  # 5MB limit
            return False, "Image size too large (max 5MB)"
        return True, ""
    
    @staticmethod
    def rate_limit_check(ip_address, max_requests=100, window_minutes=60):
        # Simple in-memory rate limiting (in production, use Redis)
        from collections import defaultdict
        import time
        
        if not hasattr(InputValidator, '_rate_limits'):
            InputValidator._rate_limits = defaultdict(list)
        
        now = time.time()
        window_start = now - (window_minutes * 60)
        
        # Clean old requests
        InputValidator._rate_limits[ip_address] = [
            req_time for req_time in InputValidator._rate_limits[ip_address] 
            if req_time > window_start
        ]
        
        # Check limit
        if len(InputValidator._rate_limits[ip_address]) >= max_requests:
            return False, "Rate limit exceeded"
        
        # Add current request
        InputValidator._rate_limits[ip_address].append(now)
        return True, ""

validator = InputValidator()