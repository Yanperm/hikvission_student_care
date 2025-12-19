# Configuration for Student Care System
# © 2025 SOFTUBON CO.,LTD.

import os

class Config:
    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'softubon-student-care-2025-secret-key'
    DEBUG = False
    
    # Database
    DATABASE_PATH = 'data/database.db'
    
    # Cloud Sync
    CLOUD_API_URL = 'http://43.210.87.220:8080'
    CLOUD_SYNC_ENABLED = True
    
    # File Upload
    UPLOAD_FOLDER = 'data/students'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Security
    SUPER_ADMIN_USERNAME = os.environ.get('SUPER_ADMIN_USER', 'admin@example.com')
    SUPER_ADMIN_PASSWORD = os.environ.get('SUPER_ADMIN_PASS', 'change-this-password')
    
    # Package Limits
    PACKAGE_LIMITS = {
        'starter': {
            'max_students': 100,
            'max_cameras': 2,
            'cloud_storage_gb': 10,
            'features': ['face_recognition', 'auto_checkin', 'manual_checkin', 'admin_dashboard', 'student_profile', 'cloud_sync']
        },
        'professional': {
            'max_students': 500,
            'max_cameras': 4,
            'cloud_storage_gb': 50,
            'features': ['face_recognition', 'auto_checkin', 'manual_checkin', 'admin_dashboard', 'student_profile', 'cloud_sync', 'parent_dashboard', 'reports', 'behavior_score', 'emotion_detection', 'mental_health', 'anti_bullying', 'notification', 'multi_user']
        },
        'business': {
            'max_students': 2000,
            'max_cameras': 999,
            'cloud_storage_gb': 200,
            'features': ['all']
        },
        'enterprise': {
            'max_students': 99999,
            'max_cameras': 999,
            'cloud_storage_gb': 999999,
            'features': ['all']
        }
    }

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

# Select configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
