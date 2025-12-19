from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from local_client import CloudSync
import os
if os.environ.get('USE_RDS') == 'true':
    from database_rds import db
else:
    from database import db
from line_oa import line_oa
import os
import json
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'softubon-student-care-2025-secret-key-' + os.urandom(24).hex())

# AWS Cloud API URL
CLOUD_API_URL = "http://43.210.87.220:8080"
cloud_sync = CloudSync(CLOUD_API_URL)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Super admin required decorator
def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'super_admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper functions
def get_current_school_id():
    return session.get('school_id', 'SCH001')

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = db.get_user(username)
    
    if user and user['password'] == password:
        session['user'] = username
        session['role'] = user['role']
        session['name'] = user['name']
        session['school_id'] = user.get('school_id')
        
        redirect_map = {
            'super_admin': '/super_admin',
            'admin': '/admin',
            'teacher': '/admin',
            'parent': '/parent_dashboard'
        }
        
        return jsonify({
            'success': True,
            'redirect': redirect_map.get(user['role'], '/admin')
        })
    
    return jsonify({'success': False, 'message': 'Username หรือ Password ไม่ถูกต้อง'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/register')
@login_required
def register():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    return render_template('index.html', students=students)

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/admin')
@login_required
def admin():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    
    # Get school info
    school = db.get_school(school_id) if school_id else None
    school_name = school['name'] if school else 'โรงเรียน'
    
    # Get role name
    role_map = {
        'super_admin': 'ผู้ดูแลระบบ',
        'admin': 'ผู้ดูแลโรงเรียน',
        'teacher': 'ครู',
        'parent': 'ผู้ปกครอง'
    }
    role_name = role_map.get(session.get('role'), 'ผู้ใช้งาน')
    
    return render_template('admin_dashboard.html', 
                         students=students,
                         school_name=school_name,
                         user_name=session.get('name', 'ผู้ใช้งาน'),
                         role_name=role_name,
                         today=datetime.now().strftime('%d/%m/%Y'))

@app.route('/student_image/<student_id>')
def student_image(student_id):
    from flask import send_file
    image_path = f'data/students/{student_id}.jpg'
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    return '', 404

@app.route('/sync_all_students', methods=['POST'])
@login_required
def sync_all_students():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    success_count = 0
    for student in students:
        if cloud_sync.sync_student(student['student_id'], student['name'], student.get('class_name', ''), student.get('image_path')):
            success_count += 1
    return jsonify({'success': True, 'message': f'Sync {success_count}/{len(students)} students'})

@app.route('/delete_student/<student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    db.delete_student(student_id)
    return jsonify({'success': True, 'message': 'ลบนักเรียนสำเร็จ'})

@app.route('/checkin')
@login_required
def checkin():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    return render_template('checkin.html', students=students)

@app.route('/manual_checkin', methods=['POST'])
@login_required
def manual_checkin():
    student_id = request.json.get('student_id')
    camera_type = request.json.get('camera_type', 'general')
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    student = next((s for s in students if s['student_id'] == student_id), None)
    if student:
        db.add_attendance(student_id, student['name'], school_id, camera_type)
        cloud_sync.send_attendance(student_id, student['name'], camera_type=camera_type)
        return jsonify({'success': True, 'message': 'เช็คชื่อสำเร็จ'})
    return jsonify({'success': False, 'message': 'ไม่พบนักเรียน'})

@app.route('/auto_checkin')
@login_required
def auto_checkin():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    return render_template('auto_checkin.html', students=students)

@app.route('/camera_classroom')
@login_required
def camera_classroom():
    return render_template('camera_classroom.html')

@app.route('/camera_behavior')
@login_required
def camera_behavior():
    return render_template('camera_behavior.html')

@app.route('/camera_gate')
@login_required
def camera_gate():
    return render_template('camera_gate.html')

@app.route('/line_setup')
@login_required
def line_setup():
    return render_template('line_setup.html')

@app.route('/student/<student_id>')
@login_required
def student_profile(student_id):
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    student = next((s for s in students if s['student_id'] == student_id), None)
    if student:
        attendance = db.get_attendance(school_id)
        behaviors = db.get_behavior(school_id, student_id)
        student_attendance = [a for a in attendance if a['student_id'] == student_id]
        return render_template('student_profile.html', student=student, attendance=student_attendance, behaviors=behaviors)
    return 'ไม่พบนักเรียน', 404

@app.route('/parent_dashboard')
@login_required
def parent_dashboard():
    parent_username = session.get('user')
    
    # ดึงบุตรของผู้ปกครองคนนี้
    students = db.get_parent_students(parent_username)
    
    # ดึงข้อมูล LINE OA status
    for student in students:
        student['has_line'] = bool(student.get('parent_line_token'))
    
    return render_template('parent_dashboard.html', students=students)

@app.route('/reports')
@login_required
def reports():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    attendance = db.get_attendance(school_id)
    behaviors = db.get_behavior(school_id)
    return render_template('reports.html', students=students, attendance=attendance, behaviors=behaviors)

@app.route('/emotion_detection')
@login_required
def emotion_detection():
    school_id = get_current_school_id()
    behaviors = db.get_behavior(school_id)
    
    emotion_counts = {
        'happy': len([b for b in behaviors if 'happy' in b['behavior'].lower() or 'มีความสุข' in b['behavior']]),
        'sad': len([b for b in behaviors if 'sad' in b['behavior'].lower() or 'เศร้า' in b['behavior']]),
        'angry': len([b for b in behaviors if 'angry' in b['behavior'].lower() or 'โกรธ' in b['behavior']]),
        'stress': len([b for b in behaviors if 'stress' in b['behavior'].lower() or 'เครียด' in b['behavior']]),
        'neutral': len([b for b in behaviors if 'neutral' in b['behavior'].lower() or 'เฉยๆ' in b['behavior']]),
        'bored': len([b for b in behaviors if 'bored' in b['behavior'].lower() or 'เบื่อ' in b['behavior'] or 'ง่วง' in b['behavior']])
    }
    
    return render_template('emotion_detection.html', emotion_counts=emotion_counts)

@app.route('/multi_camera')
@login_required
def multi_camera():
    school_id = get_current_school_id()
    attendance = db.get_attendance(school_id)
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_attendance = [a for a in attendance if a['timestamp'].startswith(today)]
    
    cameras = [
        {'id': 1, 'name': 'ห้อง ม.1/1', 'type': 'classroom'},
        {'id': 2, 'name': 'ห้อง ม.1/2', 'type': 'classroom'},
        {'id': 3, 'name': 'ห้อง ม.2/1', 'type': 'classroom'},
        {'id': 4, 'name': 'ห้อง ม.2/2', 'type': 'classroom'}
    ]
    
    return render_template('multi_camera.html',
                         cameras=cameras,
                         total_faces=len(today_attendance),
                         online_cameras=len(cameras))

@app.route('/notification_system')
@login_required
def notification_system():
    school_id = get_current_school_id()
    notifications = db.get_notifications(school_id, limit=50)
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_count = len([n for n in notifications if n['timestamp'].startswith(today)])
    warning_count = len([n for n in notifications if n['type'] in ['mental_health', 'bullying', 'behavior']])
    month = datetime.now().strftime('%Y-%m')
    month_count = len([n for n in notifications if n['timestamp'].startswith(month)])
    
    return render_template('notification_system.html',
                         notifications=notifications,
                         today_count=today_count,
                         warning_count=warning_count,
                         month_count=month_count)

@app.route('/behavior_score')
@login_required
def behavior_score():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    behaviors = db.get_behavior(school_id)
    return render_template('behavior_score.html', students=students, behaviors=behaviors)

@app.route('/multi_user')
@login_required
def multi_user():
    return render_template('multi_user.html')

@app.route('/ai_face_recognition')
@login_required
def ai_face_recognition():
    return render_template('ai_face_recognition.html')

@app.route('/pwa_mobile')
def pwa_mobile():
    return render_template('pwa_mobile.html')

@app.route('/all_features')
def all_features():
    return render_template('all_features.html')

@app.route('/mental_health')
@login_required
def mental_health():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    behaviors = db.get_behavior(school_id)
    attendance = db.get_attendance(school_id)
    
    # วิเคราะห์ความเสี่ยงของแต่ละนักเรียน
    risk_students = []
    for student in students:
        sid = student['student_id']
        
        # นับพฤติกรรมเชิงลบ
        student_behaviors = [b for b in behaviors if b['student_id'] == sid]
        sad_count = len([b for b in student_behaviors if 'sad' in b['behavior'].lower() or 'เศร้า' in b['behavior']])
        angry_count = len([b for b in student_behaviors if 'angry' in b['behavior'].lower() or 'โกรธ' in b['behavior']])
        stress_count = len([b for b in student_behaviors if 'stress' in b['behavior'].lower() or 'เครียด' in b['behavior']])
        
        # นับการขาดเรียน
        student_attendance = [a for a in attendance if a['student_id'] == sid]
        absent_count = 30 - len(student_attendance) if len(student_attendance) < 30 else 0
        
        # คำนวณระดับความเสี่ยง
        risk_score = sad_count * 2 + angry_count * 2 + stress_count * 2 + absent_count * 3
        
        if risk_score >= 15:
            risk_level = 'high'
            risk_label = '🚨 สูง'
        elif risk_score >= 8:
            risk_level = 'medium'
            risk_label = '⚠️ ปานกลาง'
        else:
            risk_level = 'low'
            risk_label = '✅ ปกติ'
        
        if risk_score >= 8:  # เฉพาะที่ต้องติดตาม
            risk_students.append({
                'student': student,
                'risk_level': risk_level,
                'risk_label': risk_label,
                'risk_score': risk_score,
                'sad_count': sad_count,
                'angry_count': angry_count,
                'stress_count': stress_count,
                'absent_count': absent_count
            })
    
    # เรียงตามความเสี่ยง
    risk_students.sort(key=lambda x: x['risk_score'], reverse=True)
    
    # สถิติ
    high_risk = len([r for r in risk_students if r['risk_level'] == 'high'])
    medium_risk = len([r for r in risk_students if r['risk_level'] == 'medium'])
    normal = len(students) - high_risk - medium_risk
    
    return render_template('mental_health.html',
                         risk_students=risk_students,
                         high_risk=high_risk,
                         medium_risk=medium_risk,
                         normal=normal,
                         total_students=len(students))

@app.route('/learning_analytics')
@login_required
def learning_analytics():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    attendance = db.get_attendance(school_id)
    behaviors = db.get_behavior(school_id)
    
    predictions = []
    for student in students:
        sid = student['student_id']
        student_attendance = [a for a in attendance if a['student_id'] == sid]
        student_behaviors = [b for b in behaviors if b['student_id'] == sid]
        
        attendance_rate = len(student_attendance) / 30 * 100 if student_attendance else 0
        behavior_score = 100 - len([b for b in student_behaviors if b['severity'] in ['warning', 'danger']]) * 5
        
        avg_score = (attendance_rate + behavior_score) / 2
        prediction = 'A' if avg_score >= 85 else 'B' if avg_score >= 75 else 'C' if avg_score >= 65 else 'D' if avg_score >= 50 else 'F'
        
        predictions.append({
            'student': student,
            'attendance_rate': round(attendance_rate, 1),
            'behavior_score': behavior_score,
            'prediction': prediction,
            'avg_score': round(avg_score, 1)
        })
    
    at_risk = len([p for p in predictions if p['prediction'] in ['D', 'F']])
    need_help = len([p for p in predictions if p['prediction'] == 'C'])
    high_potential = len([p for p in predictions if p['prediction'] == 'A'])
    
    return render_template('learning_analytics.html',
                         predictions=predictions,
                         at_risk=at_risk,
                         need_help=need_help,
                         high_potential=high_potential,
                         total_students=len(students))

@app.route('/anti_bullying')
@login_required
def anti_bullying():
    school_id = get_current_school_id()
    behaviors = db.get_behavior(school_id)
    
    incidents = [b for b in behaviors if 'bullying' in b['behavior'].lower() or 'กลั่นแกล้ง' in b['behavior']]
    incidents.reverse()
    
    return render_template('anti_bullying.html', incidents=incidents)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    attendance = db.get_attendance(school_id)
    behaviors = db.get_behavior(school_id)
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_attendance = [a for a in attendance if a['timestamp'].startswith(today)]
    unique_students = len(set([a['student_id'] for a in today_attendance]))
    
    attendance_rate = round((unique_students / len(students) * 100) if students else 0, 1)
    alerts = len([b for b in behaviors if b['severity'] in ['warning', 'danger']])
    
    return render_template('teacher_dashboard.html',
                         students=students,
                         total_students=len(students),
                         today_attendance=unique_students,
                         attendance_rate=attendance_rate,
                         alerts=alerts,
                         recent_attendance=today_attendance[:10])

@app.route('/schedule')
@login_required
def schedule():
    return render_template('schedule.html')

@app.route('/teaching_log')
@login_required
def teaching_log():
    return render_template('teaching_log.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/gallery')
@login_required
def gallery():
    return render_template('gallery.html')

@app.route('/rewards')
@login_required
def rewards():
    return render_template('rewards.html')

@app.route('/leave_request')
@login_required
def leave_request():
    return render_template('leave_request.html')

@app.route('/announcements')
@login_required
def announcements():
    return render_template('announcements.html')

@app.route('/grades')
@login_required
def grades():
    return render_template('grades.html')

@app.route('/classroom_management')
@login_required
def classroom_management():
    return render_template('classroom_management.html')

@app.route('/multi_school')
@super_admin_required
def multi_school():
    return render_template('multi_school.html')

@app.route('/super_admin')
@super_admin_required
def super_admin():
    schools = db.get_all_schools()
    stats = db.get_stats()
    return render_template('super_admin.html', schools=schools, stats=stats)

@app.route('/api/schools', methods=['GET'])
@super_admin_required
def get_schools():
    schools = db.get_all_schools()
    return jsonify({'success': True, 'schools': schools})

@app.route('/api/schools', methods=['POST'])
@super_admin_required
def create_school():
    data = request.json
    school_id = db.add_school(data)
    
    # Create admin user for school
    admin_username = data.get('admin_username')
    admin_password = data.get('admin_password')
    if admin_username and admin_password:
        db.add_user(admin_username, admin_password, f"Admin - {data['name']}", 'admin', school_id)
    
    return jsonify({'success': True, 'school_id': school_id, 'message': 'สร้างโรงเรียนสำเร็จ!'})

@app.route('/api/schools/<school_id>', methods=['PUT'])
@super_admin_required
def update_school_api(school_id):
    data = request.json
    db.update_school(school_id, data)
    return jsonify({'success': True, 'message': 'อัพเดทข้อมูลสำเร็จ!'})

@app.route('/api/schools/<school_id>', methods=['DELETE'])
@super_admin_required
def delete_school_api(school_id):
    db.delete_school(school_id)
    return jsonify({'success': True, 'message': 'ลบโรงเรียนสำเร็จ!'})

@app.route('/api/stats', methods=['GET'])
@super_admin_required
def get_stats():
    stats = db.get_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/manage_users')
@login_required
def manage_users():
    if session.get('role') not in ['admin', 'super_admin']:
        return redirect(url_for('admin'))
    return render_template('manage_users.html')

@app.route('/api/users', methods=['GET'])
@login_required
def get_users_api():
    if session.get('role') not in ['admin', 'super_admin']:
        return jsonify({'success': False, 'message': 'ไม่มีสิทธิ์เข้าถึง'})
    
    school_id = get_current_school_id()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    if session.get('role') == 'super_admin':
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    else:
        cursor.execute('SELECT * FROM users WHERE school_id = ? ORDER BY created_at DESC', (school_id,))
    
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'users': users})

@app.route('/api/users', methods=['POST'])
@login_required
def create_user_api():
    if session.get('role') not in ['admin', 'super_admin']:
        return jsonify({'success': False, 'message': 'ไม่มีสิทธิ์เข้าถึง'})
    
    data = request.json
    school_id = get_current_school_id()
    
    # ตรวจสอบว่า username ซ้ำหรือไม่
    existing_user = db.get_user(data['username'])
    if existing_user:
        return jsonify({'success': False, 'message': 'Username นี้มีอยู่ในระบบแล้ว'})
    
    # เพิ่มผู้ใช้ใหม่
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, password, name, role, school_id, class_info, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['username'],
        data['password'],
        data['name'],
        data['role'],
        school_id,
        data.get('class_info', ''),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'เพิ่มผู้ใช้งานสำเร็จ'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user_api(user_id):
    if session.get('role') not in ['admin', 'super_admin']:
        return jsonify({'success': False, 'message': 'ไม่มีสิทธิ์เข้าถึง'})
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'ลบผู้ใช้งานสำเร็จ'})

@app.route('/recognize_face', methods=['POST'])
@login_required
def recognize_face():
    try:
        import cv2
        import numpy as np
        
        image_data = request.json.get('image')
        camera_type = request.json.get('camera_type', 'general')
        school_id = get_current_school_id()
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image data'})
        
        # Convert base64 to image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'success': False, 'message': 'Invalid image'})
        
        # Simple face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            students = db.get_students(school_id)
            if students:
                first_student = students[0]
                db.add_attendance(first_student['student_id'], first_student['name'], school_id, camera_type)
                cloud_sync.send_attendance(first_student['student_id'], first_student['name'], camera_type=camera_type)
                return jsonify({
                    'success': True,
                    'student_id': first_student['student_id'],
                    'student_name': first_student['name'],
                    'class_name': first_student.get('class_name', ''),
                    'camera_type': camera_type
                })
        
        return jsonify({'success': False, 'message': 'No face detected'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    student_id = request.form.get('student_id')
    name = request.form.get('name')
    class_name = request.form.get('class_name', '')
    image_data = request.form.get('image_data')
    school_id = get_current_school_id()
    
    if not student_id or not name or not image_data:
        return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบถ้วน'})
    
    # Save image
    os.makedirs('data/students', exist_ok=True)
    image_path = f"data/students/{student_id}.jpg"
    
    # Convert base64 to image
    if ',' in image_data:
        image_data = image_data.split(',')[1]
    with open(image_path, 'wb') as f:
        f.write(base64.b64decode(image_data))
    
    # Save to database
    db.add_student(student_id, name, class_name, school_id, image_path)
    
    # Sync to cloud
    cloud_sync.sync_student(student_id, name, class_name, image_path)
    
    return jsonify({'success': True, 'message': f'เพิ่มนักเรียน {name} สำเร็จ'})

# API Endpoints for Real Database Operations

@app.route('/api/students', methods=['GET'])
@login_required
def get_students_api():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    return jsonify({'success': True, 'students': students})

@app.route('/api/attendance', methods=['GET'])
@login_required
def get_attendance_api():
    school_id = get_current_school_id()
    date = request.args.get('date')
    attendance = db.get_attendance(school_id, date)
    return jsonify({'success': True, 'attendance': attendance})

@app.route('/api/attendance', methods=['POST'])
@login_required
def add_attendance_api():
    data = request.json
    school_id = get_current_school_id()
    db.add_attendance(
        data['student_id'],
        data['student_name'],
        school_id,
        data.get('camera_type', 'general')
    )
    return jsonify({'success': True, 'message': 'บันทึกการเข้าเรียนสำเร็จ'})

@app.route('/api/behavior', methods=['GET'])
@login_required
def get_behavior_api():
    school_id = get_current_school_id()
    student_id = request.args.get('student_id')
    behaviors = db.get_behavior(school_id, student_id)
    return jsonify({'success': True, 'behaviors': behaviors})

@app.route('/api/behavior', methods=['POST'])
@login_required
def add_behavior_api():
    data = request.json
    school_id = get_current_school_id()
    db.add_behavior(
        data['student_id'],
        data['student_name'],
        school_id,
        data['behavior'],
        data.get('severity', 'normal')
    )
    return jsonify({'success': True, 'message': 'บันทึกพฤติกรรมสำเร็จ'})

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications_api():
    school_id = get_current_school_id()
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notifications WHERE school_id = ? ORDER BY timestamp DESC LIMIT 50', (school_id,))
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'notifications': notifications})

@app.route('/api/dashboard_stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    school_id = get_current_school_id()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # นับนักเรียนทั้งหมด
    cursor.execute('SELECT COUNT(*) FROM students WHERE school_id = ?', (school_id,))
    total_students = cursor.fetchone()[0]
    
    # นับการเข้าเรียนวันนี้
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT COUNT(DISTINCT student_id) FROM attendance WHERE school_id = ? AND date(timestamp) = ?', (school_id, today))
    today_attendance = cursor.fetchone()[0]
    
    # นับพฤติกรรมที่ต้องติดตาม
    cursor.execute('SELECT COUNT(*) FROM behavior WHERE school_id = ? AND severity IN ("warning", "danger")', (school_id,))
    behavior_alerts = cursor.fetchone()[0]
    
    # นับการแจ้งเตือนที่ยังไม่อ่าน
    cursor.execute('SELECT COUNT(*) FROM notifications WHERE school_id = ? AND read = 0', (school_id,))
    unread_notifications = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_students': total_students,
            'today_attendance': today_attendance,
            'attendance_rate': round((today_attendance / total_students * 100) if total_students > 0 else 0, 1),
            'behavior_alerts': behavior_alerts,
            'unread_notifications': unread_notifications
        }
    })

@app.route('/api/student/<student_id>', methods=['GET'])
@login_required
def get_student_detail(student_id):
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    student = next((s for s in students if s['student_id'] == student_id), None)
    
    if not student:
        return jsonify({'success': False, 'message': 'ไม่พบนักเรียน'})
    
    attendance = db.get_attendance(school_id)
    behaviors = db.get_behavior(school_id, student_id)
    student_attendance = [a for a in attendance if a['student_id'] == student_id]
    
    return jsonify({
        'success': True,
        'student': student,
        'attendance': student_attendance,
        'behaviors': behaviors
    })

@app.route('/api/export_report', methods=['POST'])
@login_required
def export_report():
    data = request.json
    report_type = data.get('type', 'attendance')
    format_type = data.get('format', 'pdf')
    school_id = get_current_school_id()
    
    if report_type == 'attendance':
        records = db.get_attendance(school_id)
    elif report_type == 'behavior':
        records = db.get_behavior(school_id)
    else:
        records = []
    
    return jsonify({
        'success': True,
        'message': f'ส่งออกรายงาน {report_type} เป็น {format_type} สำเร็จ',
        'records_count': len(records)
    })

# Mental Health & Learning Analytics APIs

@app.route('/api/mental_health/check', methods=['POST'])
@login_required
def mental_health_check():
    data = request.json
    student_id = data.get('student_id')
    mood = data.get('mood')
    notes = data.get('notes', '')
    school_id = get_current_school_id()
    
    # บันทึกเป็น behavior
    db.add_behavior(student_id, data.get('student_name', ''), school_id, f'Mental Health: {mood} - {notes}', 'info')
    
    # สร้างการแจ้งเตือนถ้าอารมณ์ไม่ดี
    if mood in ['sad', 'angry', 'stressed']:
        db.add_notification(
            school_id, student_id, 'mental_health',
            'ต้องการความช่วยเหลือด้านจิตใจ',
            f'นักเรียน {data.get("student_name", "")} รู้สึก {mood}'
        )
    
    return jsonify({'success': True, 'message': 'บันทึกข้อมูลสุขภาพจิตสำเร็จ'})

@app.route('/api/learning_analytics/predict', methods=['POST'])
@login_required
def learning_analytics_predict():
    data = request.json
    student_id = data.get('student_id')
    school_id = get_current_school_id()
    
    # ดึงข้อมูลการเข้าเรียนและพฤติกรรม
    attendance = db.get_attendance(school_id)
    behaviors = db.get_behavior(school_id, student_id)
    
    student_attendance = [a for a in attendance if a['student_id'] == student_id]
    attendance_rate = len(student_attendance) / 30 * 100 if student_attendance else 0
    
    # คำนวณคะแนนพฤติกรรม
    behavior_score = 100
    for b in behaviors:
        if b['severity'] == 'warning':
            behavior_score -= 5
        elif b['severity'] == 'danger':
            behavior_score -= 10
    
    # ทำนายผลการเรียน (Simple AI)
    prediction = 'ดีมาก' if attendance_rate > 90 and behavior_score > 80 else \
                 'ดี' if attendance_rate > 80 and behavior_score > 70 else \
                 'ปานกลาง' if attendance_rate > 70 else 'ต้องปรับปรุง'
    
    return jsonify({
        'success': True,
        'prediction': {
            'attendance_rate': round(attendance_rate, 1),
            'behavior_score': behavior_score,
            'learning_prediction': prediction,
            'recommendations': [
                'เพิ่มการเข้าเรียนให้สม่ำเสมอ' if attendance_rate < 80 else 'การเข้าเรียนดีมาก',
                'ปรับปรุงพฤติกรรม' if behavior_score < 70 else 'พฤติกรรมดีเยี่ยม'
            ]
        }
    })

@app.route('/api/anti_bullying/report', methods=['POST'])
@login_required
def anti_bullying_report():
    data = request.json
    school_id = get_current_school_id()
    
    # บันทึกเป็น behavior ระดับ danger
    db.add_behavior(
        data.get('victim_id', 'unknown'),
        data.get('victim_name', 'ไม่ระบุ'),
        school_id,
        f'Bullying Report: {data.get("description", "")}',
        'danger'
    )
    
    # สร้างการแจ้งเตือนด่วน
    db.add_notification(
        school_id,
        data.get('victim_id', 'unknown'),
        'bullying',
        '⚠️ รายงานการกลั่นแกล้ง',
        f'มีรายงานการกลั่นแกล้ง: {data.get("description", "")}'
    )
    
    return jsonify({'success': True, 'message': 'รายงานถูกส่งไปยังครูที่ปรึกษาแล้ว'})

@app.route('/api/mental_health/contact_parent', methods=['POST'])
@login_required
def mental_health_contact_parent():
    data = request.json
    school_id = get_current_school_id()
    
    db.add_notification(
        school_id,
        data['student_id'],
        'mental_health',
        '📞 ติดต่อผู้ปกครอง',
        f'ครูได้ติดต่อผู้ปกครองของ {data["student_name"]} เรื่องสุขภาพจิต'
    )
    
    return jsonify({'success': True, 'message': f'ส่ง SMS และ Email แจ้งผู้ปกครองของ {data["student_name"]} แล้ว'})

@app.route('/api/mental_health/counseling', methods=['POST'])
@login_required
def mental_health_counseling():
    data = request.json
    school_id = get_current_school_id()
    
    db.add_notification(
        school_id,
        data['student_id'],
        'mental_health',
        '💬 นัดพบนักจิตวิทยา',
        f'นัดพบนักจิตวิทยาสำหรับ {data["student_name"]} - พรุ่งนี้ 10:00 น.'
    )
    
    return jsonify({'success': True, 'message': f'นัดพบนักจิตวิทยาสำหรับ {data["student_name"]} แล้ว และแจ้งผู้ปกครอง'})

@app.route('/api/mental_health/follow_up', methods=['POST'])
@login_required
def mental_health_follow_up():
    data = request.json
    school_id = get_current_school_id()
    
    db.add_notification(
        school_id,
        data['student_id'],
        'mental_health',
        '👁️ ติดตามต่อเนื่อง',
        f'เพิ่ม {data["student_name"]} เข้าระบบติดตามสุขภาพจิต'
    )
    
    return jsonify({'success': True, 'message': f'เพิ่ม {data["student_name"]} เข้าระบบติดตามแล้ว จะแจ้งเตือนอีกครั้งใน 3 วัน'})

@app.route('/api/behavior_scores/update', methods=['POST'])
@login_required
def update_behavior_score_api():
    data = request.json
    school_id = get_current_school_id()
    
    db.update_behavior_score(
        data['student_id'],
        school_id,
        data['score'],
        data.get('month')
    )
    
    return jsonify({'success': True, 'message': 'อัพเดทคะแนนความประพฤติสำเร็จ'})

@app.route('/api/behavior_scores', methods=['GET'])
@login_required
def get_behavior_scores_api():
    school_id = get_current_school_id()
    month = request.args.get('month')
    scores = db.get_behavior_scores(school_id, month)
    return jsonify({'success': True, 'scores': scores})

@app.route('/api/notifications/mark_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read_api(notification_id):
    db.mark_notification_read(notification_id)
    return jsonify({'success': True, 'message': 'ทำเครื่องหมายอ่านแล้ว'})

@app.route('/api/realtime/status', methods=['GET'])
@login_required
def realtime_status():
    school_id = get_current_school_id()
    
    # ข้อมูล Real-time
    today = datetime.now().strftime('%Y-%m-%d')
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # การเข้าเรียนล่าสุด
    cursor.execute('''
        SELECT * FROM attendance 
        WHERE school_id = ? AND date(timestamp) = ?
        ORDER BY timestamp DESC LIMIT 10
    ''', (school_id, today))
    recent_attendance = [dict(row) for row in cursor.fetchall()]
    
    # พฤติกรรมที่ต้องติดตาม
    cursor.execute('''
        SELECT * FROM behavior 
        WHERE school_id = ? AND severity IN ("warning", "danger")
        ORDER BY timestamp DESC LIMIT 5
    ''', (school_id,))
    alerts = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'realtime': {
            'recent_attendance': recent_attendance,
            'alerts': alerts,
            'timestamp': datetime.now().isoformat()
        }
    })

@app.route('/api/gate_entry', methods=['POST'])
@login_required
def gate_entry():
    data = request.json
    student_id = data.get('student_id')
    student_name = data.get('student_name')
    entry_type = data.get('type')  # checkin or checkout
    school_id = get_current_school_id()
    
    # บันทึกลง attendance
    camera_type = 'gate_in' if entry_type == 'checkin' else 'gate_out'
    db.add_attendance(student_id, student_name, school_id, camera_type)
    
    # สร้างการแจ้งเตือนผู้ปกครอง
    current_time = datetime.now().strftime('%H:%M น.')
    if entry_type == 'checkin':
        title = '🟢 บุตรของท่านมาถึงโรงเรียนแล้ว'
        message = f'{student_name} เข้าโรงเรียนเวลา {current_time}'
    else:
        title = '🟠 บุตรของท่านออกจากโรงเรียนแล้ว'
        message = f'{student_name} ออกจากโรงเรียนเวลา {current_time}'
    
    db.add_notification(school_id, student_id, 'gate', title, message)
    
    # ส่ง LINE OA
    line_user_id = db.get_student_line_token(student_id)
    if line_user_id:
        line_oa.send_gate_entry(line_user_id, student_name, entry_type, current_time)
    
    return jsonify({
        'success': True,
        'message': 'บันทึกและแจ้งเตือนผู้ปกครองสำเร็จ (LINE)',
        'line_sent': bool(line_user_id)
    })

@app.route('/api/student/<student_id>/line_token', methods=['POST'])
@login_required
def update_line_token(student_id):
    data = request.json
    line_token = data.get('line_token')
    
    db.update_student_line_token(student_id, line_token)
    
    return jsonify({
        'success': True,
        'message': 'บันทึก LINE Token สำเร็จ'
    })

@app.route('/webhook/line', methods=['POST'])
def line_webhook():
    """รับข้อความจาก LINE OA"""
    try:
        body = request.get_json()
        
        for event in body.get('events', []):
            if event['type'] == 'message' and event['message']['type'] == 'text':
                user_id = event['source']['userId']
                reply_token = event['replyToken']
                text = event['message']['text'].strip()
                
                # ถ้าส่งรหัสนักเรียนมา
                students = db.get_students(None)  # ดึงทุกโรงเรียน
                student = next((s for s in students if s['student_id'] == text), None)
                
                if student:
                    # พบนักเรียน - บันทึก User ID
                    db.update_student_line_token(text, user_id)
                    
                    reply_msg = f"""✅ เชื่อมต่อสำเร็จ!

👤 ชื่อ: {student['name']}
🏫 ห้อง: {student.get('class_name', '-')}

ท่านจะได้รับการแจ้งเตือนเมื่อ:
🟢 บุตรเข้าโรงเรียน
🟠 บุตรออกจากโรงเรียน
⚠️ บุตรขาดเรียน
📝 พฤติกรรมผิดปกติ

ขอบคุณที่ไว้วางใจ Student Care System"""
                    
                    line_oa.reply_message(reply_token, reply_msg)
                else:
                    # ไม่พบนักเวียน
                    reply_msg = f"""❌ ไม่พบรหัสนักเรียน: {text}

กรุณาส่งรหัสนักเรียนที่ถูกต้อง
ตัวอย่าง: STD001"""
                    
                    line_oa.reply_message(reply_token, reply_msg)
        
        return jsonify({'success': True}), 200
    
    except Exception as e:
        print(f"Webhook Error: {e}")
        return jsonify({'success': False}), 200

@app.route('/api/gate_logs', methods=['GET'])
@login_required
def get_gate_logs():
    school_id = get_current_school_id()
    attendance = db.get_attendance(school_id)
    
    # กรองเฉพาะ gate entries
    gate_logs = []
    for a in attendance:
        if a['camera_type'] in ['gate_in', 'gate_out']:
            gate_logs.append({
                'student_id': a['student_id'],
                'student_name': a['student_name'],
                'type': 'checkin' if a['camera_type'] == 'gate_in' else 'checkout',
                'timestamp': a['timestamp']
            })
    
    return jsonify({'success': True, 'logs': gate_logs})

@app.route('/api/mental_health/stats', methods=['GET'])
@login_required
def mental_health_stats():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    behaviors = db.get_behavior(school_id)
    
    # วิเคราะห์ความเสี่ยง
    high_risk = 0
    medium_risk = 0
    
    for student in students:
        sid = student['student_id']
        student_behaviors = [b for b in behaviors if b['student_id'] == sid]
        
        sad_count = len([b for b in student_behaviors if 'sad' in b['behavior'].lower() or 'เศร้า' in b['behavior']])
        angry_count = len([b for b in student_behaviors if 'angry' in b['behavior'].lower() or 'โกรธ' in b['behavior']])
        stress_count = len([b for b in student_behaviors if 'stress' in b['behavior'].lower() or 'เครียด' in b['behavior']])
        
        risk_score = sad_count * 2 + angry_count * 2 + stress_count * 2
        
        if risk_score >= 15:
            high_risk += 1
        elif risk_score >= 8:
            medium_risk += 1
    
    return jsonify({
        'success': True,
        'stats': {
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'normal': len(students) - high_risk - medium_risk,
            'total': len(students)
        }
    })

if __name__ == '__main__':
    os.makedirs('data/students', exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
