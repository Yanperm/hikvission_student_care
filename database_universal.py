import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

try:
    from security.password_manager import password_manager
except:
    from werkzeug.security import generate_password_hash, check_password_hash
    class PasswordManager:
        @staticmethod
        def hash_password(password):
            return generate_password_hash(password, method='pbkdf2:sha256')
        @staticmethod
        def verify_password(password, password_hash):
            return check_password_hash(password_hash, password)
    password_manager = PasswordManager()

USE_POSTGRES = os.environ.get('USE_POSTGRES', 'false').lower() == 'true'

class Database:
    def __init__(self):
        self.db_type = 'postgresql' if USE_POSTGRES else 'sqlite'
        self.pool = None
        
        if self.db_type == 'postgresql':
            import psycopg2
            from psycopg2 import pool
            from psycopg2.extras import RealDictCursor
            self.psycopg2 = psycopg2
            self.RealDictCursor = RealDictCursor
            
            self.pool = pool.ThreadedConnectionPool(
                10, 100,
                host=os.environ.get('DB_HOST'),
                database=os.environ.get('DB_NAME', 'postgres'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                port=os.environ.get('DB_PORT', '5432'),
                connect_timeout=10
            )
        else:
            import sqlite3
            self.sqlite3 = sqlite3
            self.db_path = 'data/database.db'
        
        self.init_database()
    
    def get_connection(self):
        if self.db_type == 'postgresql':
            return self.pool.getconn()
        else:
            conn = self.sqlite3.connect(self.db_path)
            conn.row_factory = self.sqlite3.Row
            return conn
    
    def close_connection(self, conn):
        if self.db_type == 'postgresql':
            self.pool.putconn(conn)
        else:
            conn.close()
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.db_type == 'postgresql':
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
                    reseller_id VARCHAR(50),
                    line_channel_token TEXT,
                    line_channel_secret TEXT,
                    line_oa_id VARCHAR(100),
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
                    two_fa_secret VARCHAR(100),
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
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_students_school ON students(school_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id)')
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='super_admin'")
            if cursor.fetchone()[0] == 0:
                hashed = password_manager.hash_password('admin123')
                cursor.execute('''
                    INSERT INTO users (username, password, name, role, school_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', ('superadmin', hashed, 'Super Admin', 'super_admin', None, datetime.now()))
            
            cursor.execute("SELECT COUNT(*) FROM schools WHERE school_id = 'SCH001'")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO schools (school_id, name, province, package, max_students, 
                                       expire_date, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', ('SCH001', 'โรงเรียนสาธิต', 'กรุงเทพมหานคร', 'premium', 1000,
                      '2025-12-31', 'active', datetime.now(), datetime.now()))
        else:
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
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_students_school ON students(school_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id)')
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='super_admin'")
            if cursor.fetchone()[0] == 0:
                hashed = password_manager.hash_password('admin123')
                cursor.execute('''
                    INSERT INTO users (username, password, name, role, school_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ('superadmin', hashed, 'Super Admin', 'super_admin', None, datetime.now().isoformat()))
            
            cursor.execute("SELECT COUNT(*) FROM schools WHERE school_id = 'SCH001'")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO schools (school_id, name, province, package, max_students, 
                                       expire_date, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', ('SCH001', 'โรงเรียนสาธิต', 'กรุงเทพมหานคร', 'premium', 1000,
                      '2025-12-31', 'active', datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        cursor.close()
        self.close_connection(conn)
    
    def get_user(self, username):
        conn = self.get_connection()
        try:
            cursor = conn.cursor() if self.db_type == 'sqlite' else conn.cursor(cursor_factory=self.RealDictCursor)
            
            if self.db_type == 'postgresql':
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            else:
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            
            user = cursor.fetchone()
            cursor.close()
            return dict(user) if user else None
        finally:
            self.close_connection(conn)
    
    def add_user(self, username, password, name, role, school_id=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            hashed = password_manager.hash_password(password)
            
            if self.db_type == 'postgresql':
                cursor.execute('''
                    INSERT INTO users (username, password, name, role, school_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (username, hashed, name, role, school_id, datetime.now()))
            else:
                cursor.execute('''
                    INSERT INTO users (username, password, name, role, school_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, hashed, name, role, school_id, datetime.now().isoformat()))
            
            conn.commit()
            cursor.close()
        finally:
            self.close_connection(conn)
    
    def get_students(self, school_id=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor() if self.db_type == 'sqlite' else conn.cursor(cursor_factory=self.RealDictCursor)
            
            if self.db_type == 'postgresql':
                if school_id:
                    cursor.execute('SELECT * FROM students WHERE school_id = %s', (school_id,))
                else:
                    cursor.execute('SELECT * FROM students')
            else:
                if school_id:
                    cursor.execute('SELECT * FROM students WHERE school_id = ?', (school_id,))
                else:
                    cursor.execute('SELECT * FROM students')
            
            students = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return students
        finally:
            self.close_connection(conn)
    
    def add_student(self, student_id, name, class_name, school_id, image_path, parent_line_token=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            if self.db_type == 'postgresql':
                cursor.execute('''
                    INSERT INTO students (student_id, name, class_name, school_id, image_path, parent_line_token, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (student_id, name, class_name, school_id, image_path, parent_line_token, datetime.now()))
            else:
                cursor.execute('''
                    INSERT INTO students (student_id, name, class_name, school_id, image_path, parent_line_token, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (student_id, name, class_name, school_id, image_path, parent_line_token, datetime.now().isoformat()))
            
            conn.commit()
            cursor.close()
        finally:
            self.close_connection(conn)
    
    def update_student(self, student_id, name, class_name, school_id, image_path):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            if self.db_type == 'postgresql':
                cursor.execute('''
                    UPDATE students SET name = %s, class_name = %s, image_path = %s
                    WHERE student_id = %s AND school_id = %s
                ''', (name, class_name, image_path, student_id, school_id))
            else:
                cursor.execute('''
                    UPDATE students SET name = ?, class_name = ?, image_path = ?
                    WHERE student_id = ? AND school_id = ?
                ''', (name, class_name, image_path, student_id, school_id))
            
            conn.commit()
            cursor.close()
        finally:
            self.close_connection(conn)
    
    def delete_student(self, student_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            if self.db_type == 'postgresql':
                cursor.execute('DELETE FROM students WHERE student_id = %s', (student_id,))
            else:
                cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            
            conn.commit()
            cursor.close()
        finally:
            self.close_connection(conn)
    
    def add_attendance(self, student_id, student_name, school_id, camera_type='general'):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            if self.db_type == 'postgresql':
                cursor.execute('''
                    INSERT INTO attendance (student_id, student_name, school_id, camera_type, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (student_id, student_name, school_id, camera_type, datetime.now()))
            else:
                cursor.execute('''
                    INSERT INTO attendance (student_id, student_name, school_id, camera_type, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, student_name, school_id, camera_type, datetime.now().isoformat()))
            
            conn.commit()
            cursor.close()
        finally:
            self.close_connection(conn)
    
    def get_attendance(self, school_id=None, date=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor() if self.db_type == 'sqlite' else conn.cursor(cursor_factory=self.RealDictCursor)
            
            if self.db_type == 'postgresql':
                if school_id:
                    cursor.execute('SELECT * FROM attendance WHERE school_id = %s ORDER BY timestamp DESC LIMIT 1000', (school_id,))
                else:
                    cursor.execute('SELECT * FROM attendance ORDER BY timestamp DESC LIMIT 1000')
            else:
                if school_id:
                    cursor.execute('SELECT * FROM attendance WHERE school_id = ? ORDER BY timestamp DESC LIMIT 1000', (school_id,))
                else:
                    cursor.execute('SELECT * FROM attendance ORDER BY timestamp DESC LIMIT 1000')
            
            attendance = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return attendance
        finally:
            self.close_connection(conn)
    
    def get_school(self, school_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor() if self.db_type == 'sqlite' else conn.cursor(cursor_factory=self.RealDictCursor)
            
            if self.db_type == 'postgresql':
                cursor.execute('SELECT * FROM schools WHERE school_id = %s', (school_id,))
            else:
                cursor.execute('SELECT * FROM schools WHERE school_id = ?', (school_id,))
            
            school = cursor.fetchone()
            cursor.close()
            
            if school:
                school = dict(school)
                if school.get('features'):
                    try:
                        school['features'] = json.loads(school['features'])
                    except:
                        school['features'] = []
            return school
        finally:
            self.close_connection(conn)
    
    def get_student_line_token(self, student_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            if self.db_type == 'postgresql':
                cursor.execute('SELECT parent_line_token FROM students WHERE student_id = %s', (student_id,))
            else:
                cursor.execute('SELECT parent_line_token FROM students WHERE student_id = ?', (student_id,))
            
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result and result[0] else None
        finally:
            self.close_connection(conn)
    
    def update_student_line_token(self, student_id, line_token):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            if self.db_type == 'postgresql':
                cursor.execute('UPDATE students SET parent_line_token = %s WHERE student_id = %s', (line_token, student_id))
            else:
                cursor.execute('UPDATE students SET parent_line_token = ? WHERE student_id = ?', (line_token, student_id))
            
            conn.commit()
            cursor.close()
        finally:
            self.close_connection(conn)
    
    def get_behavior(self, school_id=None, student_id=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor() if self.db_type == 'sqlite' else conn.cursor(cursor_factory=self.RealDictCursor)
            
            if self.db_type == 'postgresql':
                if student_id:
                    cursor.execute('SELECT * FROM behavior WHERE student_id = %s ORDER BY timestamp DESC', (student_id,))
                elif school_id:
                    cursor.execute('SELECT * FROM behavior WHERE school_id = %s ORDER BY timestamp DESC', (school_id,))
                else:
                    cursor.execute('SELECT * FROM behavior ORDER BY timestamp DESC')
            else:
                if student_id:
                    cursor.execute('SELECT * FROM behavior WHERE student_id = ? ORDER BY timestamp DESC', (student_id,))
                elif school_id:
                    cursor.execute('SELECT * FROM behavior WHERE school_id = ? ORDER BY timestamp DESC', (school_id,))
                else:
                    cursor.execute('SELECT * FROM behavior ORDER BY timestamp DESC')
            
            behaviors = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return behaviors
        finally:
            self.close_connection(conn)
    
    def get_all_schools(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor() if self.db_type == 'sqlite' else conn.cursor(cursor_factory=self.RealDictCursor)
            cursor.execute('SELECT * FROM schools ORDER BY created_at DESC')
            schools = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return schools
        finally:
            self.close_connection(conn)
    
    def get_stats(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM schools WHERE status = 'active'")
            total_schools = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'total_schools': total_schools,
                'total_students': total_students
            }
        finally:
            self.close_connection(conn)

db = Database()
print(f"✅ Database initialized: {db.db_type.upper()} (Pool: {db.pool is not None})")
