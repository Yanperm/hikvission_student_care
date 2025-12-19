from flask import Flask, render_template, request, jsonify
from local_client import CloudSync
import os
import json
import base64
from datetime import datetime

app = Flask(__name__)

# AWS Cloud API URL
CLOUD_API_URL = "http://43.210.87.220:8080"
cloud_sync = CloudSync(CLOUD_API_URL)

# Simple student storage
STUDENTS_FILE = 'data/students_data.json'

def load_students():
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_students(students):
    os.makedirs('data', exist_ok=True)
    with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(students, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    students = load_students()
    return render_template('index.html', students=students)

@app.route('/admin')
def admin():
    students = load_students()
    return render_template('admin.html', students=students, today=datetime.now().strftime('%d/%m/%Y'))

@app.route('/student_image/<student_id>')
def student_image(student_id):
    from flask import send_file
    image_path = f'data/students/{student_id}.jpg'
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    return '', 404

@app.route('/sync_all_students', methods=['POST'])
def sync_all_students():
    students = load_students()
    success_count = 0
    for student_id, student in students.items():
        if cloud_sync.sync_student(student_id, student['name'], '', student.get('image_path')):
            success_count += 1
    return jsonify({'success': True, 'message': f'Sync {success_count}/{len(students)} students'})

@app.route('/delete_student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    students = load_students()
    if student_id in students:
        image_path = students[student_id].get('image_path')
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        del students[student_id]
        save_students(students)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Student not found'})

@app.route('/checkin')
def checkin():
    students = load_students()
    return render_template('checkin.html', students=students)

@app.route('/manual_checkin', methods=['POST'])
def manual_checkin():
    student_id = request.json.get('student_id')
    students = load_students()
    if student_id in students:
        student = students[student_id]
        cloud_sync.send_attendance(student_id, student['name'])
        return jsonify({'success': True, 'message': 'Check-in success'})
    return jsonify({'success': False, 'message': 'Student not found'})

@app.route('/auto_checkin')
def auto_checkin():
    students = load_students()
    return render_template('auto_checkin.html', students=students)

@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    import cv2
    import numpy as np
    
    image_data = request.json.get('image')
    if not image_data:
        return jsonify({'success': False})
    
    # Convert base64 to image
    image_data = image_data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Simple face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) > 0:
        # For demo: match with first student (replace with real face recognition)
        students = load_students()
        if students:
            first_student = list(students.values())[0]
            return jsonify({
                'success': True,
                'student_id': first_student['student_id'],
                'student_name': first_student['name']
            })
    
    return jsonify({'success': False})

@app.route('/add_student', methods=['POST'])
def add_student():
    student_id = request.form.get('student_id')
    name = request.form.get('name')
    image_data = request.form.get('image_data')
    
    if not student_id or not name or not image_data:
        return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบถ้วน'})
    
    # Save image
    os.makedirs('data/students', exist_ok=True)
    image_path = f"data/students/{student_id}.jpg"
    
    # Convert base64 to image
    image_data = image_data.split(',')[1]
    with open(image_path, 'wb') as f:
        f.write(base64.b64decode(image_data))
    
    # Save student data
    students = load_students()
    students[student_id] = {
        'student_id': student_id,
        'name': name,
        'image_path': image_path,
        'created_at': datetime.now().isoformat()
    }
    save_students(students)
    
    # Sync to cloud
    cloud_sync.sync_student(student_id, name, '', image_path)
    
    return jsonify({'success': True, 'message': f'เพิ่มนักเรียน {name} สำเร็จ'})

if __name__ == '__main__':
    os.makedirs('data/students', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
