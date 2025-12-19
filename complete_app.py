from flask import Flask, render_template, request, jsonify, Response
import cv2
import numpy as np
import os
import json
import sqlite3
from datetime import datetime
import base64

app = Flask(__name__)

class CompleteSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        self.students_data = {}
        self.face_labels = []
        self.face_images = []
        self.is_trained = False
        self.last_recognition = {}
        
        os.makedirs("data/students", exist_ok=True)
        
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
            image_bytes = base64.b64decode(image_data.split(',')[1])
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))
            
            if len(faces) == 0:
                faces = self.face_cascade.detectMultiScale(gray, 1.05, 2, minSize=(20, 20))
            
            if len(faces) == 0:
                return False, "ไม่พบใบหน้าในรูปภาพ"
            
            largest_face = max(faces, key=lambda face: face[2] * face[3])
            x, y, w, h = largest_face
            
            if w < 50 or h < 50:
                return False, "ใบหน้าเล็กเกินไป"
            
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
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
    
    def check_in_student(self, label):
        if label not in self.students_data:
            return False
        
        current_time = datetime.now()
        if label in self.last_recognition:
            time_diff = (current_time - self.last_recognition[label]).seconds
            if time_diff < 30:
                return False
        
        self.last_recognition[label] = current_time
        
        conn = sqlite3.connect('data/attendance.db')
        cursor = conn.cursor()
        
        student_id = self.students_data[label]['student_id']
        student_name = self.students_data[label]['name']
        today = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")
        
        cursor.execute('''
            INSERT INTO attendance (student_id, student_name, check_in_time, date)
            VALUES (?, ?, ?, ?)
        ''', (student_id, student_name, time_str, today))
        
        conn.commit()
        conn.close()
        return True
    
    def get_today_attendance(self):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect('data/attendance.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT student_id, student_name, check_in_time 
            FROM attendance 
            WHERE date = ?
            ORDER BY check_in_time DESC
            LIMIT 10
        ''', (today,))
        results = cursor.fetchall()
        conn.close()
        return results

system = CompleteSystem()

def generate_frames():
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = system.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                if system.is_trained:
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (100, 100))
                    
                    label, confidence = system.face_recognizer.predict(face_roi)
                    
                    if confidence < 100 and label in system.students_data:
                        name = system.students_data[label]['name']
                        student_id = system.students_data[label]['student_id']
                        
                        system.check_in_student(label)
                        
                        color = (0, 255, 0)
                        display_text = f"{name} ({student_id})"
                    else:
                        color = (0, 0, 255)
                        display_text = "Unknown"
                else:
                    color = (255, 0, 0)
                    display_text = "No Training Data"
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.rectangle(frame, (x, y-40), (x+w, y), color, -1)
                cv2.putText(frame, display_text, (x+5, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.putText(frame, f"Students: {len(system.students_data)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            current_time = datetime.now().strftime("%H:%M:%S")
            cv2.putText(frame, current_time, (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except:
        pass
    finally:
        cap.release()

@app.route('/')
def index():
    return render_template('complete.html', students=system.students_data)

@app.route('/complete')
def complete():
    return render_template('complete.html', students=system.students_data)

@app.route('/add_student', methods=['POST'])
def add_student():
    student_id = request.form['student_id']
    name = request.form['name']
    image_data = request.form['image_data']
    
    success, message = system.add_student_from_image(student_id, name, image_data)
    return jsonify({'success': success, 'message': message})

@app.route('/realtime')
def realtime():
    return render_template('realtime.html', students=system.students_data)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance_today')
def attendance_today():
    results = system.get_today_attendance()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)