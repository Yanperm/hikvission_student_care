from flask import Flask, render_template, request, jsonify, Response, session, redirect, url_for
import cv2
import numpy as np
import os
import json
import sqlite3
from datetime import datetime
import base64
import threading

try:
    from database_manager import create_database
    from auth_manager import auth_manager
    from validator import validator
    from logger_manager import logger
    from config_manager import config_manager
    from backup_manager import backup_manager
    from api_routes import api
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback to basic functionality
    auth_manager = None
    api = None

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

if api:
    app.register_blueprint(api)

class SingleCameraSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        self.students_data = {}
        self.face_labels = []
        self.face_images = []
        self.is_trained = False
        self.last_recognition = {}
        self.current_detection = {}  # เก็บข้อมูลการตรวจจับปัจจุบัน
        
        # กล้องเดียว
        self.cap = None
        self.camera_active = False
        self.current_frame = None
        self.lock = threading.Lock()
        
        os.makedirs("data/students", exist_ok=True)
        
        # เชื่อมต่อฐานข้อมูล
        try:
            if 'create_database' in globals():
                with open('config.json', 'r') as f:
                    config = json.load(f)
                
                db_config = config['database']
                self.db = create_database(db_config['type'], **db_config['config'])
                print(f"Connected to {db_config['type'].upper()} database")
            else:
                raise ImportError("Database manager not available")
        except Exception as e:
            print(f"Using basic SQLite: {e}")
            self.db = None
        
        try:
            self.load_students()
            self.init_database()
        except:
            pass
        
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
    
    def start_camera(self):
        if not self.camera_active:
            self.cap = cv2.VideoCapture(0)
            self.camera_active = True
            threading.Thread(target=self._camera_loop, daemon=True).start()
    
    def stop_camera(self):
        self.camera_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def _camera_loop(self):
        while self.camera_active:
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
                
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.current_frame = frame.copy()
            else:
                # กล้องหยุดทำงาน ลองเชื่อมต่อใหม่
                print("Camera disconnected, reconnecting...")
                if self.cap:
                    self.cap.release()
                self.cap = cv2.VideoCapture(0)
                cv2.waitKey(1000)  # รอ 1 วินาที
    
    def get_frame(self):
        with self.lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def add_student_from_image(self, student_id, name, image_data):
        try:
            image_bytes = base64.b64decode(image_data.split(',')[1])
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # ตรวจสอบขนาดรูปภาพ
            if gray.shape[0] < 50 or gray.shape[1] < 50:
                return False, "รูปภาพเล็กเกินไป"
            
            try:
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                if len(faces) == 0:
                    faces = self.face_cascade.detectMultiScale(
                        gray, 
                        scaleFactor=1.05, 
                        minNeighbors=3, 
                        minSize=(20, 20),
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )
            except Exception as e:
                return False, f"ตรวจจับใบหน้าไม่ได้: {str(e)}"
            
            if len(faces) == 0:
                return False, "ไม่พบใบหน้าในรูปภาพ"
            
            largest_face = max(faces, key=lambda face: face[2] * face[3])
            x, y, w, h = largest_face
            
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
            self.face_recognizer.train(np.array(self.face_images), np.array(self.face_labels))
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
        
        # บันทึกลงฐานข้อมูล
        self.db.record_attendance(student_id, student_name)
        
        return True
    
    def get_today_attendance(self):
        return self.db.get_today_attendance()

system = SingleCameraSystem()

def generate_frames():
    while True:
        frame = system.get_frame()
        if frame is None:
            # สร้าง frame ว่างเมื่อไม่มีข้อมูล
            blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank_frame, "Camera Disconnected", (150, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', blank_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            continue
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        try:
            faces = system.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
        except Exception as e:
            print(f"Face detection error: {e}")
            faces = []
        
        for (x, y, w, h) in faces:
            if system.is_trained:
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (100, 100))
                
                label, confidence = system.face_recognizer.predict(face_roi)
                
                if confidence < 70 and label in system.students_data:
                    name = system.students_data[label]['name']
                    student_id = system.students_data[label]['student_id']
                    
                    print(f"Detected: {name} (ID: {student_id}) - Confidence: {100-confidence:.1f}%")
                    
                    # อัปเดตข้อมูลการตรวจจับปัจจุบัน
                    system.current_detection = {
                        'name': name,
                        'student_id': student_id,
                        'confidence': 100 - confidence,
                        'timestamp': datetime.now()
                    }
                    
                    if system.check_in_student(label):
                        print(f"Checked in: {name}")
                    
                    color = (0, 255, 0)
                    display_text = name
                else:
                    color = (0, 0, 255)
                    display_text = "Unknown"
            else:
                color = (255, 0, 0)
                display_text = "No Data"
            
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

@app.route('/')
def index():
    return render_template('professional_ui.html', students=system.students_data)

@app.route('/admin')
@auth_manager.require_auth()
def admin_panel():
    return render_template('admin_panel.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if auth_manager.verify_password(username, password):
            token = auth_manager.generate_token(username)
            session['token'] = token
            session['user'] = username
            logger.info(f"User {username} logged in")
            return redirect(url_for('admin_panel'))
        else:
            logger.warning(f"Failed login attempt: {username}")
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    user = session.get('user')
    session.clear()
    if user:
        logger.info(f"User {user} logged out")
    return redirect(url_for('login'))

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/add_student', methods=['POST'])
def add_student():
    try:
        # Rate limiting
        client_ip = request.remote_addr
        rate_ok, rate_msg = validator.rate_limit_check(client_ip)
        if not rate_ok:
            return jsonify({'success': False, 'message': rate_msg}), 429
        
        student_id = validator.sanitize_input(request.form['student_id'])
        name = validator.sanitize_input(request.form['name'])
        image_data = request.form['image_data']
        
        # Validate inputs
        valid_id, id_msg = validator.validate_student_id(student_id)
        if not valid_id:
            return jsonify({'success': False, 'message': id_msg})
        
        valid_name, name_msg = validator.validate_name(name)
        if not valid_name:
            return jsonify({'success': False, 'message': name_msg})
        
        valid_image, image_msg = validator.validate_image_data(image_data)
        if not valid_image:
            return jsonify({'success': False, 'message': image_msg})
        
        success, message = system.add_student_from_image(student_id, name, image_data)
        
        if success:
            logger.info(f"Student added: {student_id} - {name}")
        else:
            logger.warning(f"Failed to add student: {student_id} - {message}")
        
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        logger.error(f"Add student error: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/start_camera', methods=['POST'])
def start_camera():
    system.start_camera()
    return jsonify({'success': True})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    system.stop_camera()
    return jsonify({'success': True})

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance_today')
def attendance_today():
    results = system.get_today_attendance()
    return jsonify(results)

@app.route('/current_detection')
def current_detection():
    # ส่งข้อมูลการจดจำปัจจุบัน
    if system.current_detection and 'timestamp' in system.current_detection:
        time_diff = (datetime.now() - system.current_detection['timestamp']).seconds
        if time_diff < 5:  # แสดงเฉพาะที่ตรวจจับได้ใน 5 วินาทีที่ผ่านมา
            return jsonify({
                'detected': True,
                'name': system.current_detection['name'],
                'student_id': system.current_detection['student_id'],
                'confidence': system.current_detection['confidence'],
                'time_ago': time_diff
            })
    
    return jsonify({'detected': False})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)