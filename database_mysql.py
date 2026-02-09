"""
MySQL Database Manager
รองรับ MySQL/MariaDB สำหรับ Production
"""

import mysql.connector
from mysql.connector import pooling
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class MySQLDatabase:
    def __init__(self):
        # Connection Pool
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="student_care_pool",
            pool_size=10,
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'student_care'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        self.init_database()
    
    def get_connection(self):
        return self.pool.get_connection()
    
    def init_database(self):
        """สร้างตารางทั้งหมด"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Schools Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                school_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                address TEXT,
                phone VARCHAR(20),
                email VARCHAR(100),
                status ENUM('active', 'inactive') DEFAULT 'active',
                expire_date DATE,
                max_students INT DEFAULT 1000,
                reseller_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_status (status),
                INDEX idx_reseller (reseller_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                role ENUM('super_admin', 'reseller', 'admin', 'teacher', 'parent') NOT NULL,
                school_id VARCHAR(50),
                class_info VARCHAR(100),
                two_fa_secret VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_school (school_id),
                INDEX idx_role (role),
                FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Students Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                class_name VARCHAR(100),
                school_id VARCHAR(50) NOT NULL,
                image_path VARCHAR(500),
                parent_line_token VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_student_id (student_id),
                INDEX idx_school (school_id),
                INDEX idx_class (class_name),
                FULLTEXT idx_name (name),
                FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Attendance Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                student_name VARCHAR(255) NOT NULL,
                school_id VARCHAR(50) NOT NULL,
                camera_type VARCHAR(50) DEFAULT 'general',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_student (student_id),
                INDEX idx_school (school_id),
                INDEX idx_date (timestamp),
                INDEX idx_camera (camera_type),
                FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Behavior Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                student_name VARCHAR(255) NOT NULL,
                school_id VARCHAR(50) NOT NULL,
                behavior TEXT NOT NULL,
                severity ENUM('normal', 'info', 'warning', 'danger') DEFAULT 'normal',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_student (student_id),
                INDEX idx_school (school_id),
                INDEX idx_severity (severity),
                INDEX idx_date (timestamp),
                FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Notifications Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                school_id VARCHAR(50) NOT NULL,
                student_id VARCHAR(50),
                type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                `read` BOOLEAN DEFAULT FALSE,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_school (school_id),
                INDEX idx_student (student_id),
                INDEX idx_read (`read`),
                INDEX idx_date (timestamp),
                FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Resellers Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resellers (
                reseller_id VARCHAR(50) PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                max_schools INT DEFAULT 10,
                schools_used INT DEFAULT 0,
                commission_rate DECIMAL(5,2) DEFAULT 10.00,
                status ENUM('active', 'inactive') DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Payments Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                school_id VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                payment_date DATE NOT NULL,
                payment_method VARCHAR(50),
                status ENUM('pending', 'paid', 'cancelled') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_school (school_id),
                INDEX idx_status (status),
                INDEX idx_date (payment_date),
                FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Audit Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action VARCHAR(100) NOT NULL,
                details TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user_id),
                INDEX idx_action (action),
                INDEX idx_date (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ MySQL Database initialized")
    
    # ฟังก์ชันเดิมทั้งหมด (แปลงจาก SQLite เป็น MySQL)
    
    def add_student(self, student_id, name, class_name, school_id, image_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (student_id, name, class_name, school_id, image_path)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                name = VALUES(name),
                class_name = VALUES(class_name),
                image_path = VALUES(image_path),
                updated_at = CURRENT_TIMESTAMP
        ''', (student_id, name, class_name, school_id, image_path))
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_students(self, school_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM students WHERE school_id = %s ORDER BY name', (school_id,))
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return students
    
    def delete_student(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students WHERE student_id = %s', (student_id,))
        conn.commit()
        cursor.close()
        conn.close()
    
    def add_attendance(self, student_id, student_name, school_id, camera_type='general'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attendance (student_id, student_name, school_id, camera_type)
            VALUES (%s, %s, %s, %s)
        ''', (student_id, student_name, school_id, camera_type))
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_attendance(self, school_id, date=None):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        if date:
            cursor.execute('''
                SELECT * FROM attendance 
                WHERE school_id = %s AND DATE(timestamp) = %s 
                ORDER BY timestamp DESC
            ''', (school_id, date))
        else:
            cursor.execute('''
                SELECT * FROM attendance 
                WHERE school_id = %s 
                ORDER BY timestamp DESC LIMIT 1000
            ''', (school_id,))
        attendance = cursor.fetchall()
        cursor.close()
        conn.close()
        return attendance
    
    def add_user(self, username, password, name, role, school_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        # TODO: Hash password with bcrypt
        cursor.execute('''
            INSERT INTO users (username, password, name, role, school_id)
            VALUES (%s, %s, %s, %s, %s)
        ''', (username, password, name, role, school_id))
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_user(self, username):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user

# สร้าง instance
db = MySQLDatabase()
