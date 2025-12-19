from abc import ABC, abstractmethod
from datetime import datetime
import sqlite3
import json
import os

class DatabaseInterface(ABC):
    @abstractmethod
    def add_student(self, student_id, name): pass
    
    @abstractmethod
    def get_students(self): pass
    
    @abstractmethod
    def record_attendance(self, student_id, student_name): pass
    
    @abstractmethod
    def get_today_attendance(self): pass

class SQLiteDB(DatabaseInterface):
    def __init__(self, db_path="data/attendance.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE,
                name TEXT,
                created_at TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                student_name TEXT,
                check_in_time TEXT,
                date TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_student(self, student_id, name):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO students (student_id, name, created_at) VALUES (?, ?, ?)',
                         (student_id, name, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True, "เพิ่มนักเรียนสำเร็จ"
        except Exception as e:
            return False, str(e)
    
    def get_students(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT student_id, name FROM students')
        results = cursor.fetchall()
        conn.close()
        return {i: {'student_id': row[0], 'name': row[1]} for i, row in enumerate(results)}
    
    def record_attendance(self, student_id, student_name):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = datetime.now().strftime("%Y-%m-%d")
            time_str = datetime.now().strftime("%H:%M:%S")
            cursor.execute('INSERT INTO attendance (student_id, student_name, check_in_time, date) VALUES (?, ?, ?, ?)',
                         (student_id, student_name, time_str, today))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_today_attendance(self):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT student_id, student_name, check_in_time FROM attendance WHERE date = ? ORDER BY check_in_time DESC LIMIT 10', (today,))
        results = cursor.fetchall()
        conn.close()
        return results

class FirebaseDB(DatabaseInterface):
    def __init__(self, config_path=None):
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            import os
            
            if not firebase_admin._apps:
                # Try different credential methods
                if config_path and os.path.exists(config_path):
                    cred = credentials.Certificate(config_path)
                elif os.path.exists('firebase_credentials.json'):
                    cred = credentials.Certificate('firebase_credentials.json')
                else:
                    # Use default credentials (for Cloud Run)
                    cred = credentials.ApplicationDefault()
                
                firebase_admin.initialize_app(cred, {
                    'projectId': 'solutions-4e649',
                    'databaseURL': 'https://solutions-4e649-default-rtdb.asia-southeast1.firebasedatabase.app'
                })
            
            self.db = firestore.client()
        except ImportError:
            raise Exception("Firebase SDK not installed. Run: pip install firebase-admin")
    
    def add_student(self, student_id, name):
        try:
            self.db.collection('students').document(student_id).set({
                'student_id': student_id,
                'name': name,
                'created_at': datetime.now()
            })
            return True, "เพิ่มนักเรียนสำเร็จ"
        except Exception as e:
            return False, str(e)
    
    def get_students(self):
        try:
            docs = self.db.collection('students').where('active', '==', True).stream()
            students = {}
            for i, doc in enumerate(docs):
                data = doc.to_dict()
                students[i] = {
                    'student_id': data.get('student_id', ''),
                    'name': data.get('name', ''),
                    'class': data.get('class', ''),
                    'samples': 1
                }
            return students
        except Exception as e:
            print(f"Error getting students from Firebase: {e}")
            return {}
    
    def record_attendance(self, student_id, student_name):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            time_str = datetime.now().strftime("%H:%M:%S")
            self.db.collection('attendance').add({
                'student_id': student_id,
                'student_name': student_name,
                'date': today,
                'time': time_str,
                'timestamp': datetime.now()
            })
            return True
        except:
            return False
    
    def get_today_attendance(self):
        try:
            from firebase_admin import firestore
            today = datetime.now().strftime("%Y-%m-%d")
            docs = self.db.collection('attendance').where('date', '==', today).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()
            return [(doc.to_dict()['student_id'], doc.to_dict()['student_name'], doc.to_dict()['time']) for doc in docs]
        except:
            return []

class MySQLDB(DatabaseInterface):
    def __init__(self, host, user, password, database):
        try:
            import mysql.connector
            self.conn = mysql.connector.connect(
                host=host, user=user, password=password, database=database
            )
            self._init_db()
        except ImportError:
            raise Exception("MySQL connector not installed. Run: pip install mysql-connector-python")
    
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) UNIQUE,
                name VARCHAR(100),
                created_at DATETIME
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50),
                student_name VARCHAR(100),
                check_in_time TIME,
                date DATE
            )
        ''')
        self.conn.commit()
    
    def add_student(self, student_id, name):
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO students (student_id, name, created_at) VALUES (%s, %s, %s)',
                         (student_id, name, datetime.now()))
            self.conn.commit()
            return True, "เพิ่มนักเรียนสำเร็จ"
        except Exception as e:
            return False, str(e)
    
    def get_students(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT student_id, name FROM students')
        results = cursor.fetchall()
        return {i: {'student_id': row[0], 'name': row[1]} for i, row in enumerate(results)}
    
    def record_attendance(self, student_id, student_name):
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO attendance (student_id, student_name, check_in_time, date) VALUES (%s, %s, %s, %s)',
                         (student_id, student_name, datetime.now().time(), datetime.now().date()))
            self.conn.commit()
            return True
        except:
            return False
    
    def get_today_attendance(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT student_id, student_name, check_in_time FROM attendance WHERE date = %s ORDER BY check_in_time DESC LIMIT 10', 
                      (datetime.now().date(),))
        return cursor.fetchall()

def create_database(db_type, **config):
    """Factory function สำหรับสร้าง database instance"""
    if db_type.lower() == 'sqlite':
        return SQLiteDB(config.get('db_path', 'data/attendance.db'))
    elif db_type.lower() == 'firebase':
        return FirebaseDB(config.get('config_path'))
    elif db_type.lower() == 'mysql':
        return MySQLDB(config['host'], config['user'], config['password'], config['database'])
    else:
        raise ValueError(f"Unsupported database type: {db_type}")