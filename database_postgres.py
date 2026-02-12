"""
PostgreSQL Database Module
รองรับ PostgreSQL (Local/RDS)
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

class DatabasePostgres:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 5432))
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'student_care')
        self.init_database()
    
    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            cursor_factory=RealDictCursor
        )
    
    def init_database(self):
        """สร้างตารางถ้ายังไม่มี"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                class_name VARCHAR(50),
                school_id VARCHAR(50),
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                student_name VARCHAR(200),
                school_id VARCHAR(50),
                camera_type VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Behavior table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior (
                id SERIAL PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                student_name VARCHAR(200),
                school_id VARCHAR(50),
                behavior TEXT,
                severity VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL,
                name VARCHAR(200),
                role VARCHAR(50),
                school_id VARCHAR(50),
                class_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Schools table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id SERIAL PRIMARY KEY,
                school_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                address TEXT,
                phone VARCHAR(50),
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                school_id VARCHAR(50),
                student_id VARCHAR(50),
                type VARCHAR(50),
                title TEXT,
                message TEXT,
                read BOOLEAN DEFAULT FALSE,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        self.create_default_users()
    
    def create_default_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()['count']
        
        if count == 0:
            # Super Admin
            cursor.execute('''
                INSERT INTO users (username, password, name, role, school_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('superadmin', 'admin123', 'Super Admin', 'super_admin', None))
            
            # School
            cursor.execute('''
                INSERT INTO schools (school_id, name, address)
                VALUES (%s, %s, %s)
            ''', ('SCH001', 'โรงเรียนทดสอบ', 'กรุงเทพฯ'))
            
            # Admin
            cursor.execute('''
                INSERT INTO users (username, password, name, role, school_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('admin', 'admin123', 'Admin', 'admin', 'SCH001'))
            
            # Teacher
            cursor.execute('''
                INSERT INTO users (username, password, name, role, school_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('teacher1', 'teacher123', 'Teacher 1', 'teacher', 'SCH001'))
            
            # Parent
            cursor.execute('''
                INSERT INTO users (username, password, name, role, school_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('parent1', 'parent123', 'Parent 1', 'parent', 'SCH001'))
            
            conn.commit()
            print("✅ สร้างผู้ใช้เริ่มต้น: superadmin/admin123, admin/admin123, teacher1/teacher123, parent1/parent123")
        
        conn.close()
    
    def get_students(self, school_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE school_id = %s ORDER BY name', (school_id,))
        students = cursor.fetchall()
        conn.close()
        return students
    
    def add_student(self, student_id, name, class_name, school_id, image_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (student_id, name, class_name, school_id, image_path)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (student_id) DO UPDATE SET
                name = EXCLUDED.name,
                class_name = EXCLUDED.class_name,
                image_path = EXCLUDED.image_path
        ''', (student_id, name, class_name, school_id, image_path))
        conn.commit()
        conn.close()
    
    def update_student(self, student_id, name, class_name, school_id, image_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students SET name = %s, class_name = %s, image_path = %s
            WHERE student_id = %s AND school_id = %s
        ''', (name, class_name, image_path, student_id, school_id))
        conn.commit()
        conn.close()
    
    def delete_student(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students WHERE student_id = %s', (student_id,))
        conn.commit()
        conn.close()
    
    def get_attendance(self, school_id, date=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if date:
            cursor.execute('SELECT * FROM attendance WHERE school_id = %s AND DATE(timestamp) = %s ORDER BY timestamp DESC', (school_id, date))
        else:
            cursor.execute('SELECT * FROM attendance WHERE school_id = %s ORDER BY timestamp DESC', (school_id,))
        attendance = cursor.fetchall()
        conn.close()
        return attendance
    
    def add_attendance(self, student_id, student_name, school_id, camera_type='general'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attendance (student_id, student_name, school_id, camera_type)
            VALUES (%s, %s, %s, %s)
        ''', (student_id, student_name, school_id, camera_type))
        conn.commit()
        conn.close()
    
    def get_behavior(self, school_id, student_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if student_id:
            cursor.execute('SELECT * FROM behavior WHERE school_id = %s AND student_id = %s ORDER BY timestamp DESC', (school_id, student_id))
        else:
            cursor.execute('SELECT * FROM behavior WHERE school_id = %s ORDER BY timestamp DESC', (school_id,))
        behaviors = cursor.fetchall()
        conn.close()
        return behaviors
    
    def add_behavior(self, student_id, student_name, school_id, behavior, severity='normal'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO behavior (student_id, student_name, school_id, behavior, severity)
            VALUES (%s, %s, %s, %s, %s)
        ''', (student_id, student_name, school_id, behavior, severity))
        conn.commit()
        conn.close()
    
    def get_user(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def add_user(self, username, password, name, role, school_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, name, role, school_id)
            VALUES (%s, %s, %s, %s, %s)
        ''', (username, password, name, role, school_id))
        conn.commit()
        conn.close()
    
    def get_school(self, school_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM schools WHERE school_id = %s', (school_id,))
        school = cursor.fetchone()
        conn.close()
        return school
    
    def get_all_schools(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM schools ORDER BY name')
        schools = cursor.fetchall()
        conn.close()
        return schools
    
    def add_school(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        school_id = data.get('school_id', f"SCH{datetime.now().strftime('%Y%m%d%H%M%S')}")
        cursor.execute('''
            INSERT INTO schools (school_id, name, address, phone)
            VALUES (%s, %s, %s, %s)
        ''', (school_id, data['name'], data.get('address', ''), data.get('phone', '')))
        conn.commit()
        conn.close()
        return school_id
    
    def get_notifications(self, school_id, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notifications WHERE school_id = %s ORDER BY timestamp DESC LIMIT %s', (school_id, limit))
        notifications = cursor.fetchall()
        conn.close()
        return notifications
    
    def add_notification(self, school_id, student_id, type, title, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (school_id, student_id, type, title, message)
            VALUES (%s, %s, %s, %s, %s)
        ''', (school_id, student_id, type, title, message))
        conn.commit()
        conn.close()
    
    def get_stats(self):
        return {}
    
    def get_parent_students(self, parent_username):
        return []
    
    def update_school(self, school_id, data):
        pass
    
    def delete_school(self, school_id):
        pass
    
    def get_cameras(self, school_id):
        return []
    
    def add_camera(self, school_id, data):
        return 1
    
    def get_camera(self, camera_id):
        return None
    
    def update_camera(self, camera_id, data):
        pass
    
    def delete_camera(self, camera_id):
        pass
    
    def update_behavior_score(self, student_id, school_id, score, month):
        pass
    
    def get_behavior_scores(self, school_id, month):
        return []
    
    def mark_notification_read(self, notification_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE notifications SET read = TRUE WHERE id = %s', (notification_id,))
        conn.commit()
        conn.close()
    
    def get_student_line_token(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT parent_line_token FROM students WHERE student_id = %s', (student_id,))
        result = cursor.fetchone()
        conn.close()
        return result['parent_line_token'] if result and result.get('parent_line_token') else None
    
    def update_student_line_token(self, student_id, line_token):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET parent_line_token = %s WHERE student_id = %s', (line_token, student_id))
        conn.commit()
        conn.close()
    
    def get_all_resellers(self):
        return []
    
    def add_reseller(self, data):
        return 1
    
    def get_reseller(self, reseller_id):
        return None
    
    def update_reseller(self, reseller_id, data):
        pass
    
    def delete_reseller(self, reseller_id):
        pass
    
    def get_reseller_schools(self, reseller_id):
        return []
    
    def calculate_reseller_commission(self, reseller_id):
        return 0
    
    def get_all_payments(self):
        return []
    
    def add_payment(self, data):
        return 1
    
    def get_revenue(self, period):
        return 0
    
    def get_pending_payments(self):
        return 0
    
    def get_system_settings(self):
        return {}
    
    def update_system_settings(self, data):
        pass

db = DatabasePostgres()
