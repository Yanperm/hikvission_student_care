# Database Manager for Student Care System
# © 2025 SOFTUBON CO.,LTD.

import sqlite3
import json
from datetime import datetime

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
        
        # Schools table
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
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                school_id TEXT,
                class_info TEXT,
                created_at TEXT
            )
        ''')
        
        # Students table
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
        
        # Attendance table
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
        
        # Behavior table
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
        
        # Behavior scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                school_id TEXT,
                score INTEGER DEFAULT 100,
                month TEXT,
                updated_at TEXT
            )
        ''')
        
        # Parent-Student relation table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parent_student_relation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_username TEXT NOT NULL,
                student_id TEXT NOT NULL,
                relation TEXT,
                created_at TEXT
            )
        ''')
        
        # Cameras table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id TEXT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                type TEXT NOT NULL,
                ip TEXT NOT NULL,
                port TEXT DEFAULT '80',
                username TEXT,
                password TEXT,
                rtsp_url TEXT,
                status TEXT DEFAULT 'offline',
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Insert only super admin if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='super_admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, password, name, role, school_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('superadmin@softubon.com', 'Softubon@2025', 'Super Admin', 'super_admin', None, datetime.now().isoformat()))
        
        # Insert demo users for testing
        demo_users = [
            ('superadmin', 'admin123', 'Super Admin Demo', 'super_admin', None),
            ('admin', 'admin123', 'Admin Demo', 'admin', 'SCH001'),
            ('teacher1', 'teacher123', 'Teacher Demo', 'teacher', 'SCH001'),
            ('parent1', 'parent123', 'Parent Demo', 'parent', 'SCH001')
        ]
        
        for username, password, name, role, school_id in demo_users:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO users (username, password, name, role, school_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, password, name, role, school_id, datetime.now().isoformat()))
        
        # Insert demo school if not exists
        cursor.execute("SELECT COUNT(*) FROM schools WHERE school_id = 'SCH001'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO schools (school_id, name, province, address, package, max_students, 
                                   expire_date, status, features, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'SCH001',
                'โรงเรียนสาธิต',
                'กรุงเทพมหานคร',
                '123 ถนนสุขุมวิท',
                'premium',
                1000,
                '2025-12-31',
                'active',
                json.dumps(['face_recognition', 'behavior_detection', 'mental_health']),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    # School Management
    def add_school(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        school_id = f"SCH{str(cursor.execute('SELECT COUNT(*) FROM schools').fetchone()[0] + 1).zfill(3)}"
        
        cursor.execute('''
            INSERT INTO schools (school_id, name, province, address, package, max_students, 
                               expire_date, features, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            school_id,
            data['name'],
            data.get('province', ''),
            data.get('address', ''),
            data['package'],
            data['max_students'],
            data['expire_date'],
            json.dumps(data.get('features', [])),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return school_id
    
    def get_all_schools(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM schools ORDER BY created_at DESC')
        schools = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        for school in schools:
            school['features'] = json.loads(school['features']) if school['features'] else []
        
        return schools
    
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
    
    def update_school(self, school_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE schools 
            SET name = ?, province = ?, address = ?, package = ?, 
                max_students = ?, expire_date = ?, features = ?, 
                status = ?, updated_at = ?
            WHERE school_id = ?
        ''', (
            data['name'],
            data.get('province', ''),
            data.get('address', ''),
            data['package'],
            data['max_students'],
            data['expire_date'],
            json.dumps(data.get('features', [])),
            data.get('status', 'active'),
            datetime.now().isoformat(),
            school_id
        ))
        
        conn.commit()
        conn.close()
    
    def delete_school(self, school_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM schools WHERE school_id = ?', (school_id,))
        cursor.execute('DELETE FROM users WHERE school_id = ?', (school_id,))
        conn.commit()
        conn.close()
    
    # User Management
    def add_user(self, username, password, name, role, school_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, password, name, role, school_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password, name, role, school_id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_user(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM schools WHERE status = "active"')
        total_schools = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(max_students) FROM schools WHERE status = "active"')
        total_capacity = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT COUNT(*) FROM schools 
            WHERE status = "active" AND date(expire_date) <= date('now', '+30 days')
        ''')
        expiring_soon = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_schools': total_schools,
            'total_capacity': total_capacity,
            'expiring_soon': expiring_soon
        }
    
    # Student Management
    def add_student(self, student_id, name, class_name, school_id, image_path, parent_line_token=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (student_id, name, class_name, school_id, image_path, parent_line_token, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, name, class_name, school_id, image_path, parent_line_token, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def update_student_line_token(self, student_id, line_token):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET parent_line_token = ? WHERE student_id = ?', (line_token, student_id))
        conn.commit()
        conn.close()
    
    def get_student_line_token(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT parent_line_token FROM students WHERE student_id = ?', (student_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else None
    
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
    
    def delete_student(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
        conn.commit()
        conn.close()
    
    # Attendance
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
            cursor.execute('SELECT * FROM attendance WHERE school_id = ? ORDER BY timestamp DESC', (school_id,))
        else:
            cursor.execute('SELECT * FROM attendance ORDER BY timestamp DESC')
        attendance = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return attendance
    
    # Behavior
    def add_behavior(self, student_id, student_name, school_id, behavior, severity='normal'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO behavior (student_id, student_name, school_id, behavior, severity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_id, student_name, school_id, behavior, severity, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_behavior(self, school_id=None, student_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if student_id:
            cursor.execute('SELECT * FROM behavior WHERE student_id = ? ORDER BY timestamp DESC', (student_id,))
        elif school_id:
            cursor.execute('SELECT * FROM behavior WHERE school_id = ? ORDER BY timestamp DESC', (school_id,))
        else:
            cursor.execute('SELECT * FROM behavior ORDER BY timestamp DESC')
        behaviors = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return behaviors
    
    # Notifications
    def add_notification(self, school_id, student_id, type, title, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (school_id, student_id, type, title, message, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (school_id, student_id, type, title, message, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_notifications(self, school_id, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notifications WHERE school_id = ? ORDER BY timestamp DESC LIMIT ?', (school_id, limit))
        notifications = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return notifications
    
    def mark_notification_read(self, notification_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE notifications SET read = 1 WHERE id = ?', (notification_id,))
        conn.commit()
        conn.close()
    
    # Behavior Scores
    def update_behavior_score(self, student_id, school_id, score, month=None):
        if not month:
            month = datetime.now().strftime('%Y-%m')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM behavior_scores WHERE student_id = ? AND month = ?', (student_id, month))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE behavior_scores SET score = ?, updated_at = ?
                WHERE student_id = ? AND month = ?
            ''', (score, datetime.now().isoformat(), student_id, month))
        else:
            cursor.execute('''
                INSERT INTO behavior_scores (student_id, school_id, score, month, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, school_id, score, month, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_behavior_scores(self, school_id, month=None):
        if not month:
            month = datetime.now().strftime('%Y-%m')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM behavior_scores WHERE school_id = ? AND month = ?', (school_id, month))
        scores = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return scores
    
    # Parent-Student Relation
    def add_parent_student_relation(self, parent_username, student_id, relation='parent'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO parent_student_relation (parent_username, student_id, relation, created_at)
            VALUES (?, ?, ?, ?)
        ''', (parent_username, student_id, relation, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_parent_students(self, parent_username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.* FROM students s
            JOIN parent_student_relation psr ON s.student_id = psr.student_id
            WHERE psr.parent_username = ?
        ''', (parent_username,))
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return students
    
    # Camera Management
    def add_camera(self, school_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cameras (school_id, name, location, type, ip, port, username, password, rtsp_url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            school_id,
            data['name'],
            data['location'],
            data['type'],
            data['ip'],
            data.get('port', '80'),
            data.get('username'),
            data.get('password'),
            data.get('rtsp_url'),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        camera_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return camera_id
    
    def get_cameras(self, school_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if school_id:
            cursor.execute('SELECT * FROM cameras WHERE school_id = ? ORDER BY created_at DESC', (school_id,))
        else:
            cursor.execute('SELECT * FROM cameras ORDER BY created_at DESC')
        cameras = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cameras
    
    def get_camera(self, camera_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cameras WHERE id = ?', (camera_id,))
        camera = cursor.fetchone()
        conn.close()
        return dict(camera) if camera else None
    
    def update_camera(self, camera_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE cameras 
            SET name = ?, location = ?, type = ?, ip = ?, port = ?, 
                username = ?, password = ?, rtsp_url = ?, updated_at = ?
            WHERE id = ?
        ''', (
            data['name'],
            data['location'],
            data['type'],
            data['ip'],
            data.get('port', '80'),
            data.get('username'),
            data.get('password'),
            data.get('rtsp_url'),
            datetime.now().isoformat(),
            camera_id
        ))
        conn.commit()
        conn.close()
    
    def delete_camera(self, camera_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cameras WHERE id = ?', (camera_id,))
        conn.commit()
        conn.close()
    
    def update_camera_status(self, camera_id, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE cameras SET status = ?, updated_at = ? WHERE id = ?', 
                      (status, datetime.now().isoformat(), camera_id))
        conn.commit()
        conn.close()

# Initialize database
db = Database()
