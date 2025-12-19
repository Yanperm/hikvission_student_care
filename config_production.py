# Production Configuration
import os

class ProductionConfig:
    # Database - Use RDS
    DB_TYPE = os.environ.get('DB_TYPE', 'postgresql')  # or 'mysql'
    DB_HOST = os.environ.get('DB_HOST', 'studentcare.xxxxx.ap-southeast-7.rds.amazonaws.com')
    DB_NAME = os.environ.get('DB_NAME', 'studentcare')
    DB_USER = os.environ.get('DB_USER', 'admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    
    # S3 for file storage
    S3_BUCKET = os.environ.get('S3_BUCKET', 'studentcare-files')
    S3_REGION = os.environ.get('S3_REGION', 'ap-southeast-7')
    
    # Redis for session/cache
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://studentcare.xxxxx.cache.amazonaws.com:6379')
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    
    # Flask
    DEBUG = False
    TESTING = False
