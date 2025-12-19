from flask import Flask, render_template, request, jsonify, redirect, url_for
import cv2
import numpy as np
import os
import json
import sqlite3
from datetime import datetime
import base64

app = Flask(__name__)

class WebStudentSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        self.students_data = {}
        self.face_labels = []
        self.face_images = []
        self.is_trained = False
        
        os.makedirs("data/students", exist_ok=True)
        os.makedirs("static/uploads", exist_ok=True)
        
        self.load_students()
        self.init_database()
        
        if len(self.students_data) > 0:
            self.train_recognizer()
    
    def init_database(self):
        conn = sqlite3.connect('data/attendance.db')
        cursor = conn.cursor()
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
    
    def add_student_from_image(self, student_id, name, image_data):
        try:
            # แปลง base64 เป็นรูปภาพ
            image_bytes = base64.b64decode(image_data.split(',')[1])
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # ลองหลายค่า parameter เพื่อตรวจจับใบหน้า
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))
            
            if len(faces) == 0:
                # ลองอีกครั้งด้วยค่าที่อ่อนไหวกว่า
                faces = self.face_cascade.detectMultiScale(gray, 1.05, 2, minSize=(20, 20))
            
            if len(faces) == 0:
                return False, "ไม่พบใบหน้าในรูปภาพ กรุณาถ่ายรูปใหม่ให้ใบหน้าชัดเจน"
            
            # ใช้ใบหน้าที่ใหญ่ที่สุด
            largest_face = max(faces, key=lambda face: face[2] * face[3])
            x, y, w, h = largest_face
            
            # ตรวจสอบขนาดใบหน้า
            if w < 50 or h < 50:
                return False, "ใบหน้าเล็กเกินไป กรุณาเข้าใกล้กล้องมากขึ้น"
            
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # เพิ่มข้อมูล
            label = len(self.students_data)
            self.students_data[label] = {
                'student_id': student_id,
                'name': name,
                'samples': 1
            }
            
            self.face_images.append(face_roi)
            self.face_labels.append(label)
            
            self.save_students()
            self.train_recognizer()
            
            return True, f"เพิ่มนักเรียน {name} สำเร็จ!"
            
        except Exception as e:
            return False, f"เกิดข้อผิดพลาด: {str(e)}"
    
    def save_students(self):
        with open('data/students_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.students_data, f, ensure_ascii=False, indent=2)
        
        np.save('data/face_images.npy', np.array(self.face_images))
        np.save('data/face_labels.npy', np.array(self.face_labels))
    
    def load_students(self):
        try:
            if os.path.exists('data/students_data.json'):
                with open('data/students_data.json', 'r', encoding='utf-8') as f:
                    self.students_data = json.load(f)
                self.students_data = {int(k): v for k, v in self.students_data.items()}
            
            if os.path.exists('data/face_images.npy'):
                self.face_images = np.load('data/face_images.npy').tolist()
                self.face_labels = np.load('data/face_labels.npy').tolist()
        except:
            pass
    
    def train_recognizer(self):
        if len(self.face_images) > 0:
            self.face_recognizer.train(self.face_images, np.array(self.face_labels))
            self.is_trained = True
    
    def get_today_attendance(self):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect('data/attendance.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT student_id, student_name, check_in_time 
            FROM attendance 
            WHERE date = ?
            ORDER BY check_in_time
        ''', (today,))
        results = cursor.fetchall()
        conn.close()
        return results

system = WebStudentSystem()

@app.route('/')
def index():
    return render_template('index.html', students=system.students_data)

@app.route('/add_student', methods=['POST'])
def add_student():
    student_id = request.form['student_id']
    name = request.form['name']
    image_data = request.form['image_data']
    
    success, message = system.add_student_from_image(student_id, name, image_data)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message})

@app.route('/attendance')
def attendance():
    today_attendance = system.get_today_attendance()
    return render_template('attendance.html', attendance=today_attendance)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)