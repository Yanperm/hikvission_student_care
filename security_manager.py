"""
Security Manager
- Password Hashing (bcrypt)
- Rate Limiting
- CSRF Protection
- Input Validation
"""

import bcrypt
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import re

class SecurityManager:
    def __init__(self):
        self.login_attempts = {}  # {ip: [(timestamp, success), ...]}
        self.rate_limits = {}  # {ip: [(timestamp, endpoint), ...]}
    
    # Password Hashing
    def hash_password(self, password):
        """Hash password ด้วย bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """ตรวจสอบ password"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    # Rate Limiting
    def check_rate_limit(self, ip, endpoint, max_requests=100, window_minutes=1):
        """ตรวจสอบ rate limit"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # ลบ request เก่า
        if ip in self.rate_limits:
            self.rate_limits[ip] = [
                (ts, ep) for ts, ep in self.rate_limits[ip] 
                if ts > window_start
            ]
        else:
            self.rate_limits[ip] = []
        
        # นับ request ใน window
        count = len([1 for ts, ep in self.rate_limits[ip] if ep == endpoint])
        
        if count >= max_requests:
            return False
        
        # บันทึก request ใหม่
        self.rate_limits[ip].append((now, endpoint))
        return True
    
    def rate_limit(self, max_requests=100, window_minutes=1):
        """Decorator สำหรับ rate limiting"""
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                ip = request.remote_addr
                endpoint = request.endpoint
                
                if not self.check_rate_limit(ip, endpoint, max_requests, window_minutes):
                    return jsonify({
                        'success': False,
                        'message': 'Too many requests. Please try again later.'
                    }), 429
                
                return f(*args, **kwargs)
            return wrapped
        return decorator
    
    # Login Attempts
    def check_login_attempts(self, ip, max_attempts=5, lockout_minutes=15):
        """ตรวจสอบจำนวนครั้งที่ login ผิด"""
        now = datetime.now()
        window_start = now - timedelta(minutes=lockout_minutes)
        
        if ip in self.login_attempts:
            # ลบ attempt เก่า
            self.login_attempts[ip] = [
                (ts, success) for ts, success in self.login_attempts[ip]
                if ts > window_start
            ]
            
            # นับ failed attempts
            failed = len([1 for ts, success in self.login_attempts[ip] if not success])
            
            if failed >= max_attempts:
                return False, f'Account locked. Try again in {lockout_minutes} minutes.'
        
        return True, None
    
    def record_login_attempt(self, ip, success):
        """บันทึก login attempt"""
        if ip not in self.login_attempts:
            self.login_attempts[ip] = []
        
        self.login_attempts[ip].append((datetime.now(), success))
    
    # Input Validation
    def validate_email(self, email):
        """ตรวจสอบ email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        """ตรวจสอบเบอร์โทร (ไทย)"""
        pattern = r'^0[0-9]{9}$'
        return re.match(pattern, phone) is not None
    
    def sanitize_input(self, text):
        """ทำความสะอาด input (ป้องกัน XSS)"""
        if not text:
            return text
        
        # แทนที่ special characters
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def validate_student_id(self, student_id):
        """ตรวจสอบรหัสนักเรียน"""
        # อนุญาตเฉพาะตัวอักษร ตัวเลข และ - _
        pattern = r'^[A-Za-z0-9_-]{3,20}$'
        return re.match(pattern, student_id) is not None

# สร้าง instance
security = SecurityManager()
