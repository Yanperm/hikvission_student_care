import sqlite3
import json
from datetime import datetime
from security.password_manager import password_manager

class Database:
    def __init__(self, db_path='data/database.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Schools table with indexes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                province TEXT,
                address TEXT,
                package TEXT NOT NULL,
                max_students INTEGER,
                expire_date TEXT,
                status TEXT DEFAULT 'active',
                features TEXT,
                reseller_id TEXT,
                line_channel_token TEXT,
                line_channel_secret TEXT,
                line_oa_id TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_school_id ON schools(school_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_school_status ON schools(status)')
        
        # Users table with indexes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                school_id TEXT,
                class_info TEXT,
                two_fa_secret TEXT,
                created_at TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_school ON users(school_id)')
        
        # Students table with indexes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                class_name TEXT,
                school_id TEXT,
                image_path TEXT,
                parent_line_token TEXT,
                parent_phone TEXT,
                parent_email TEXT,
                created_at TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_id ON students(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_school ON students(school_id)')
        
        # Attendance table with indexes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                student_name TEXT,
                school_id TEXT,
                camera_type TEXT,
                timestamp TEXT,
                status TEXT DEFAULT 'present'
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_timestamp ON attendance(timestamp)')
        
        # Behavior table with indexes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                student_name TEXT,
                school_id TEXT,
                behavior TEXT,
                severity TEXT,
                timestamp TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_behavior_student ON behavior(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_behavior_severity ON behavior(severity)')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id TEXT,
                student_id TEXT,
                type TEXT,
                title TEXT,
                message TEXT,
                timestamp TEXT,
                read INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_school ON notifications(school_id)')
        
        # Insert super admin with hashed password
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='super_admin'")
        if cursor.fetchone()[0] == 0:
            hashed_password = password_manager.hash_password('Softubon@2025')
            cursor.execute('''
                INSERT INTO users (username, password, name, role, school_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('superadmin@softubon.com', hashed_password, 'Super Admin', 'super_admin', None, datetime.now().isoformat()))
        
        # Insert demo users with hashed passwords
        demo_users = [
            ('superadmin', 'admin123', 'Super Admin Demo', 'super_admin', None),
            ('admin', 'admin123', 'Admin Demo', 'admin', 'SCH001'),
            ('teacher1', 'teacher123', 'Teacher Demo', 'teacher', 'SCH001'),
            ('parent1', 'parent123', 'Parent Demo', 'parent', 'SCH001')
        ]
        
        for username, password, name, role, school_id in demo_users:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] == 0:
                hashed_password = password_manager.hash_password(password)
                cursor.execute('''
                    INSERT INTO users (username, password, name, role, school_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, hashed_password, name, role, school_id, datetime.now().isoformat()))
        
        # Insert demo school
        cursor.execute("SELECT COUNT(*) FROM schools WHERE school_id = 'SCH001'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO schools (school_id, name, province, address, package, max_students, 
                                   expire_date, status, features, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'SCH001', 'โรงเรียนสาธิต', 'กรุงเทพมหานคร', '123 ถนนสุขุมวิท',
                'premium', 1000, '2025-12-31', 'active',
                json.dumps(['face_recognition', 'behavior_detection', 'mental_health']),
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def add_user(self, username, password, name, role, school_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_password = password_manager.hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password, name, role, school_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, hashed_password, name, role, school_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_user(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def get_students(self, school_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if school_id:
            cursor.execute('SELECT * FROM students WHERE school_id = ?', (school_id,))
        else:
            cursor.execute('SELECT * FROM students')
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return students
    
    def add_student(self, student_id, name, class_name, school_id, image_path, parent_line_token=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (student_id, name, class_name, school_id, image_path, parent_line_token, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, name, class_name, school_id, image_path, parent_line_token, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def update_student(self, student_id, name, class_name, school_id, image_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students 
            SET name = ?, class_name = ?, image_path = ?
            WHERE student_id = ? AND school_id = ?
        ''', (name, class_name, image_path, student_id, school_id))
        conn.commit()
        conn.close()
    
    def delete_student(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
        conn.commit()
        conn.close()
    
    def add_attendance(self, student_id, student_name, school_id, camera_type='general'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attendance (student_id, student_name, school_id, camera_type, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, student_name, school_id, camera_type, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_attendance(self, school_id=None, date=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if school_id:
            cursor.execute('SELECT * FROM attendance WHERE school_id = ? ORDER BY timestamp DESC LIMIT 1000', (school_id,))
        else:
            cursor.execute('SELECT * FROM attendance ORDER BY timestamp DESC LIMIT 1000')
        attendance = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return attendance
    
    def get_school(self, school_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM schools WHERE school_id = ?', (school_id,))
        school = cursor.fetchone()
        conn.close()
        if school:
            school = dict(school)
            school['features'] = json.loads(school['features']) if school['features'] else []
        return school
    
    def get_student_line_token(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT parent_line_token FROM students WHERE student_id = ?', (student_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else None
    
    def update_student_line_token(self, student_id, line_token):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET parent_line_token = ? WHERE student_id = ?', (line_token, student_id))
        conn.commit()
        conn.close()

db = Database()
