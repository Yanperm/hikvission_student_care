# Database Manager for Production (RDS)
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class DatabaseRDS:
    def __init__(self):
        self.db_config = {
            'host': os.environ.get('DB_HOST', 'your-rds-endpoint.rds.amazonaws.com'),
            'database': os.environ.get('DB_NAME', 'studentcare'),
            'user': os.environ.get('DB_USER', 'admin'),
            'password': os.environ.get('DB_PASSWORD', 'your-password'),
            'port': os.environ.get('DB_PORT', '5432')
        }
        self.init_database()
    
    def get_connection(self):
        return psycopg2.connect(**self.db_config)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables (same structure as SQLite)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id SERIAL PRIMARY KEY,
                school_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                province VARCHAR(100),
                address TEXT,
                package VARCHAR(50) NOT NULL,
                max_students INTEGER,
                expire_date VARCHAR(50),
                status VARCHAR(20) DEFAULT 'active',
                features TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                school_id VARCHAR(50),
                class_info VARCHAR(100),
                created_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                class_name VARCHAR(100),
                school_id VARCHAR(50),
                image_path VARCHAR(500),
                parent_line_token VARCHAR(255),
                parent_phone VARCHAR(20),
                parent_email VARCHAR(100),
                created_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                student_name VARCHAR(255),
                school_id VARCHAR(50),
                camera_type VARCHAR(50),
                timestamp TIMESTAMP,
                status VARCHAR(20) DEFAULT 'present'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                student_name VARCHAR(255),
                school_id VARCHAR(50),
                behavior TEXT,
                severity VARCHAR(20),
                timestamp TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                school_id VARCHAR(50),
                student_id VARCHAR(50),
                type VARCHAR(50),
                title VARCHAR(255),
                message TEXT,
                timestamp TIMESTAMP,
                read INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()

# Use RDS in production
db = DatabaseRDS()
