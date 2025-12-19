import sqlite3
from datetime import datetime, date
import os

class AttendanceSystem:
    def __init__(self, db_path="data/attendance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """สร้างฐานข้อมูล"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ตารางนักเรียน
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                class_room TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตารางการเข้าเรียน
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                date DATE,
                time TIME,
                status TEXT DEFAULT 'present',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_student(self, student_id, name, class_room=""):
        """เพิ่มนักเรียน"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO students (student_id, name, class_room)
                VALUES (?, ?, ?)
            ''', (student_id, name, class_room))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"ข้อผิดพลาดในการเพิ่มนักเรียน: {e}")
            return False
    
    def mark_attendance(self, student_id):
        """บันทึกการเข้าเรียน"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = date.today()
            now = datetime.now().time()
            
            # ตรวจสอบว่าเช็คชื่อวันนี้แล้วหรือยัง
            cursor.execute('''
                SELECT id FROM attendance 
                WHERE student_id = ? AND date = ?
            ''', (student_id, today))
            
            if cursor.fetchone():
                conn.close()
                return False, "เช็คชื่อแล้ววันนี้"
            
            # บันทึกการเข้าเรียน
            cursor.execute('''
                INSERT INTO attendance (student_id, date, time)
                VALUES (?, ?, ?)
            ''', (student_id, today, now))
            
            conn.commit()
            conn.close()
            return True, "เช็คชื่อสำเร็จ"
            
        except Exception as e:
            print(f"ข้อผิดพลาดในการบันทึกการเข้าเรียน: {e}")
            return False, str(e)
    
    def get_today_attendance(self):
        """ดูการเข้าเรียนวันนี้"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = date.today()
            cursor.execute('''
                SELECT s.student_id, s.name, a.time, a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.date = ?
                ORDER BY a.time
            ''', (today,))
            
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            print(f"ข้อผิดพลาด: {e}")
            return []
    
    def get_student_info(self, student_id):
        """ดูข้อมูลนักเรียน"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT student_id, name, class_room
                FROM students
                WHERE student_id = ?
            ''', (student_id,))
            
            result = cursor.fetchone()
            conn.close()
            return result
            
        except Exception as e:
            print(f"ข้อผิดพลาด: {e}")
            return None
    
    def get_all_students(self):
        """ดูรายชื่อนักเรียนทั้งหมด"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT student_id, name, class_room FROM students ORDER BY student_id')
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            print(f"ข้อผิดพลาด: {e}")
            return []