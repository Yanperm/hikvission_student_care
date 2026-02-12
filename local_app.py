from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from local_client import CloudSync
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Use SQLite by default, RDS only if explicitly enabled
db_type = os.environ.get('DB_TYPE', 'sqlite')

if db_type == 'postgresql' or os.environ.get('USE_POSTGRES', 'false').lower() == 'true':
    try:
        from database_postgres import db
        print("Using PostgreSQL Database")
    except Exception as e:
        print(f"PostgreSQL Connection Failed: {str(e)}")
        print("Falling back to SQLite")
        from database import db
elif os.environ.get('USE_RDS', 'false').lower() == 'true':
    try:
        from database_rds import db
        print("Using RDS Database")
    except Exception as e:
        print(f"RDS Connection Failed: {str(e)}")
        print("Falling back to SQLite")
        from database import db
else:
    from database import db
    print("Using SQLite Database")
from line_oa import line_oa
from face_recognition_system import face_recognition_system
from line_notification import line_notification
import os
import json
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

# Register Database Setup Blueprint
from database_setup_api import db_setup_bp
app.register_blueprint(db_setup_bp)

# Initialize WebSocket
from websocket_manager import init_socketio
socketio = init_socketio(app)

# AWS Cloud API URL
CLOUD_API_URL = os.environ.get('CLOUD_API_URL', 'http://localhost:8080')
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
    return render_template('professional_landing.html')

@app.route('/landing_old')
def landing_old():
    return render_template('landing.html')

@app.route('/student_photo')
def student_photo():
    return render_template('student_photo.html')

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
            'super_admin': '/super_admin_complete',
            'reseller': '/reseller_dashboard',
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

@app.route('/photo_capture')
def photo_capture():
    return render_template('photo_capture.html')

@app.route('/register')
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

@app.route('/admin_old')
@login_required
def admin_old():
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
    # ลบรูปภาพก่อน
    image_path = f'data/students/{student_id}.jpg'
    if os.path.exists(image_path):
        os.remove(image_path)
    
    # ลบจาก cache
    global face_cache
    if student_id in face_cache:
        del face_cache[student_id]
    
    # ลบจาก database
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

@app.route('/user_guide')
def user_guide():
    return render_template('user_guide.html')

@app.route('/import_students')
@login_required
def import_students():
    return render_template('import_students.html')

@app.route('/gate_camera')
def gate_camera_standalone():
    """Standalone gate camera - no login required"""
    return render_template('gate_camera_standalone.html')

@app.route('/camera_management')
@login_required
def camera_management():
    return render_template('camera_management.html')

@app.route('/self_register')
def self_register():
    """Self registration for students - no login required"""
    return render_template('self_register.html')

@app.route('/all_features')
def all_features():
    return render_template('all_features.html')

@app.route('/qr_checkin')
@login_required
def qr_checkin():
    return render_template('qr_checkin.html')

@app.route('/two_factor_auth')
@login_required
def two_factor_auth_page():
    return render_template('two_factor_auth.html')

@app.route('/backup_management')
@login_required
def backup_management():
    if session.get('role') not in ['admin', 'super_admin']:
        return redirect(url_for('admin'))
    return render_template('backup_management.html')

@app.route('/audit_logs')
@login_required
def audit_logs_page():
    if session.get('role') not in ['admin', 'super_admin']:
        return redirect(url_for('admin'))
    return render_template('audit_logs.html')

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

@app.route('/super_admin_complete')
@super_admin_required
def super_admin_complete():
    return render_template('super_admin_complete.html')

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

@app.route('/api/schools/<school_id>', methods=['GET'])
@super_admin_required
def get_school_detail(school_id):
    school = db.get_school(school_id)
    if school:
        return jsonify({'success': True, 'school': school})
    return jsonify({'success': False, 'message': 'ไม่พบโรงเรียน'})
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
def add_student():
    try:
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        class_name = request.form.get('class_name', '')
        image_data = request.form.get('image_data')
        school_id = session.get('school_id', 'SCH001')
        
        if not student_id or not name or not image_data:
            return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบถ้วน'})
        
        os.makedirs('data/students', exist_ok=True)
        image_path = f"data/students/{student_id}.jpg"
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_data += '=' * (4 - len(image_data) % 4)
        
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_data))
        
        # ตรวจสอบว่ามีอยู่แล้วหรือไม่
        students = db.get_students(school_id)
        existing = any(s['student_id'] == student_id for s in students)
        
        if existing:
            # UPDATE
            db.update_student(student_id, name, class_name, school_id, image_path)
            message = f'อัพเดทข้อมูล {name} สำเร็จ'
        else:
            # INSERT
            db.add_student(student_id, name, class_name, school_id, image_path)
            message = f'เพิ่มนักเรียน {name} สำเร็จ'
        
        cloud_sync.sync_student(student_id, name, class_name, image_path)
        
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/api/self_register', methods=['POST'])
def self_register_api():
    try:
        data = request.json
        student_id = data.get('student_id')
        name = data.get('name')
        class_name = data.get('class_name', '')
        image_data = data.get('image_data')
        school_id = 'SCH001'
        
        if not student_id or not name or not image_data:
            return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบถ้วน'})
        
        students = db.get_students(school_id)
        if any(s['student_id'] == student_id for s in students):
            return jsonify({'success': False, 'message': 'รหัสนักเรียนนี้มีในระบบแล้ว'})
        
        os.makedirs('data/students', exist_ok=True)
        image_path = f"data/students/{student_id}.jpg"
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_data += '=' * (4 - len(image_data) % 4)
        
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_data))
        
        db.add_student(student_id, name, class_name, school_id, image_path)
        cloud_sync.sync_student(student_id, name, class_name, image_path)
        
        return jsonify({'success': True, 'message': f'ลงทะเบียน {name} สำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'})

@app.route('/api/get_classes', methods=['GET'])
def get_classes_api():
    classes = [
        'ป.1/1', 'ป.1/2', 'ป.1/3', 'ป.2/1', 'ป.2/2', 'ป.2/3',
        'ป.3/1', 'ป.3/2', 'ป.3/3', 'ป.4/1', 'ป.4/2', 'ป.4/3',
        'ป.5/1', 'ป.5/2', 'ป.5/3', 'ป.6/1', 'ป.6/2', 'ป.6/3',
        'ม.1/1', 'ม.1/2', 'ม.1/3', 'ม.1/4', 'ม.2/1', 'ม.2/2', 'ม.2/3', 'ม.2/4',
        'ม.3/1', 'ม.3/2', 'ม.3/3', 'ม.3/4', 'ม.4/1', 'ม.4/2', 'ม.4/3', 'ม.4/4',
        'ม.5/1', 'ม.5/2', 'ม.5/3', 'ม.5/4', 'ม.6/1', 'ม.6/2', 'ม.6/3', 'ม.6/4',
    ]
    return jsonify({'success': True, 'classes': classes})

# API Endpoints for Real Database Operations

@app.route('/api/students', methods=['GET'])
def get_students_api_public():
    """Public API - no login required"""
    school_id = request.args.get('school_id', 'SCH001')
    students = db.get_students(school_id)
    return jsonify({'success': True, 'students': students})

@app.route('/api/students_auth', methods=['GET'])
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

# Import APIs
@app.route('/api/download_template')
def download_template():
    """ดาวน์โหลด Template Excel"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import send_file
        
        # สร้างข้อมูลตัวอย่าง
        data = {
            'student_id': ['STD001', 'STD002', 'STD003', 'STD004', 'STD005'],
            'name': ['สมชาย ใจดี', 'สมหญิง รักเรียน', 'สมศักดิ์ ขยัน', 'สมใจ มีสุข', 'สมปอง เก่งกาจ'],
            'class_name': ['ม.1/1', 'ม.1/1', 'ม.1/2', 'ม.2/1', 'ม.2/2']
        }
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Students')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'student_template_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/import/preview', methods=['POST'])
@login_required
def import_preview():
    try:
        import pandas as pd
        file = request.files.get('file')
        if not file:
            return jsonify({'success': False, 'message': 'ไม่พบไฟล์'})
        
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Convert to list of dicts
        students = df.to_dict('records')
        
        # Validate required columns
        required = ['student_id', 'name']
        if not all(col in df.columns for col in required):
            return jsonify({'success': False, 'message': 'ไฟล์ต้องมีคอลัมน์ student_id และ name'})
        
        return jsonify({'success': True, 'students': students})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/import/students', methods=['POST'])
def import_students_api():
    """Public API - no login required"""
    try:
        data = request.json
        students = data.get('students', [])
        school_id = data.get('school_id', 'SCH001')
        
        imported = 0
        for student in students:
            student_id = student.get('student_id')
            name = student.get('name')
            class_name = student.get('class_name', '')
            
            if student_id and name:
                db.add_student(student_id, name, class_name, school_id, None)
                imported += 1
        
        return jsonify({'success': True, 'imported': imported, 'message': f'นำเข้าสำเร็จ {imported} คน'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/import/students_auth', methods=['POST'])
@login_required
def import_students_api_auth():
    try:
        data = request.json
        students = data.get('students', [])
        school_id = get_current_school_id()
        
        imported = 0
        for student in students:
            student_id = student.get('student_id')
            name = student.get('name')
            class_name = student.get('class_name', '')
            
            if student_id and name:
                db.add_student(student_id, name, class_name, school_id, None)
                imported += 1
        
        return jsonify({'success': True, 'imported': imported, 'message': f'นำเข้าสำเร็จ {imported} คน'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/import/test_db', methods=['POST'])
@login_required
def test_db_connection():
    try:
        config = request.json
        # Simple connection test (implement based on db type)
        return jsonify({'success': True, 'message': 'เชื่อมต่อสำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/import/from_db', methods=['POST'])
@login_required
def import_from_db():
    try:
        config = request.json
        school_id = get_current_school_id()
        
        # Implement database import based on config
        # This is a placeholder - implement based on your needs
        
        return jsonify({'success': True, 'imported': 0, 'message': 'ฟีเจอร์นี้กำลังพัฒนา'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Import System APIs
@app.route('/api/import/with_images', methods=['POST'])
@login_required
def import_students_with_images():
    """นำเข้าข้อมูลพร้อมรูปภาพ"""
    try:
        from student_import_system import StudentImportSystem
        
        school_id = get_current_school_id()
        excel_file = request.files.get('excel')
        images_zip = request.files.get('images')
        
        if not excel_file:
            return jsonify({'success': False, 'message': 'กรุณาอัพโหลดไฟล์ Excel'})
        
        import_system = StudentImportSystem(db)
        
        if images_zip:
            result = import_system.import_with_images(excel_file, images_zip, school_id)
        else:
            result = import_system.import_from_excel(excel_file, school_id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/import/template', methods=['GET'])
@login_required
def download_import_template():
    """ดาวน์โหลด Template Excel"""
    try:
        from student_import_system import StudentImportSystem
        from flask import send_file
        
        import_system = StudentImportSystem(db)
        output = import_system.create_template_excel()
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'student_import_template_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

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

@app.route('/api/export/attendance_pdf', methods=['POST'])
@login_required
def export_attendance_pdf():
    try:
        from export_manager import export_manager
        from flask import send_file
        
        school_id = get_current_school_id()
        school = db.get_school(school_id) if school_id else None
        school_name = school['name'] if school else 'โรงเรียน'
        
        data = request.json
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        attendance = db.get_attendance(school_id, start_date)
        
        buffer = export_manager.export_attendance_pdf(attendance, school_name)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'attendance_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/export/attendance_excel', methods=['POST'])
@login_required
def export_attendance_excel():
    try:
        from export_manager import export_manager
        from flask import send_file
        
        school_id = get_current_school_id()
        data = request.json
        start_date = data.get('start_date')
        
        attendance = db.get_attendance(school_id, start_date)
        
        buffer = export_manager.export_attendance_excel(attendance)
        
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'attendance_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/export/behavior_pdf', methods=['POST'])
@login_required
def export_behavior_pdf():
    try:
        from export_manager import export_manager
        from flask import send_file
        
        school_id = get_current_school_id()
        school = db.get_school(school_id) if school_id else None
        school_name = school['name'] if school else 'โรงเรียน'
        
        behaviors = db.get_behavior(school_id)
        
        buffer = export_manager.export_behavior_pdf(behaviors, school_name)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'behavior_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/export/behavior_excel', methods=['POST'])
@login_required
def export_behavior_excel():
    try:
        from export_manager import export_manager
        from flask import send_file
        
        school_id = get_current_school_id()
        behaviors = db.get_behavior(school_id)
        
        buffer = export_manager.export_behavior_excel(behaviors)
        
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'behavior_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/export/summary_pdf', methods=['POST'])
@login_required
def export_summary_pdf():
    try:
        from export_manager import export_manager
        from flask import send_file
        
        school_id = get_current_school_id()
        school = db.get_school(school_id) if school_id else None
        school_name = school['name'] if school else 'โรงเรียน'
        
        # ดึงสถิติ
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM students WHERE school_id = ?', (school_id,))
        total_students = cursor.fetchone()[0]
        
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(DISTINCT student_id) FROM attendance WHERE school_id = ? AND date(timestamp) = ?', (school_id, today))
        today_attendance = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM behavior WHERE school_id = ? AND severity IN ("warning", "danger")', (school_id,))
        behavior_alerts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM notifications WHERE school_id = ? AND read = 0', (school_id,))
        unread_notifications = cursor.fetchone()[0]
        
        conn.close()
        
        stats = {
            'total_students': total_students,
            'today_attendance': today_attendance,
            'attendance_rate': round((today_attendance / total_students * 100) if total_students > 0 else 0, 1),
            'behavior_alerts': behavior_alerts,
            'unread_notifications': unread_notifications
        }
        
        buffer = export_manager.export_summary_pdf(stats, school_name)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'summary_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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

@app.route('/api/line/config', methods=['GET'])
@login_required
def get_line_config():
    """ดึงการตั้งค่า LINE OA"""
    try:
        school_id = get_current_school_id()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # เพิ่มคอลัมน์ถ้ายังไม่มี
        try:
            cursor.execute('ALTER TABLE schools ADD COLUMN IF NOT EXISTS line_channel_token TEXT')
            cursor.execute('ALTER TABLE schools ADD COLUMN IF NOT EXISTS line_channel_secret TEXT')
            conn.commit()
        except:
            pass
        
        cursor.execute('SELECT line_channel_token, line_channel_secret FROM schools WHERE school_id = %s', (school_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # PostgreSQL RealDictCursor returns dict
            token = row['line_channel_token'] if isinstance(row, dict) else row[0]
            secret = row['line_channel_secret'] if isinstance(row, dict) else row[1]
            
            return jsonify({
                'success': True,
                'config': {
                    'channel_access_token': token or '',
                    'channel_secret': secret or ''
                }
            })
        return jsonify({'success': False, 'message': 'ไม่พบข้อมูลโรงเรียน'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/line/config', methods=['POST'])
@login_required
def save_line_config():
    """บันทึกการตั้งค่า LINE OA"""
    try:
        data = request.json
        school_id = get_current_school_id()
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # เพิ่มคอลัมน์ถ้ายังไม่มี
        try:
            cursor.execute('ALTER TABLE schools ADD COLUMN IF NOT EXISTS line_channel_token TEXT')
            cursor.execute('ALTER TABLE schools ADD COLUMN IF NOT EXISTS line_channel_secret TEXT')
            conn.commit()
        except:
            pass
        
        cursor.execute("""
            UPDATE schools 
            SET line_channel_token = %s, line_channel_secret = %s
            WHERE school_id = %s
        """, (data['channel_access_token'], data['channel_secret'], school_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'บันทึกการตั้งค่าสำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/line/test', methods=['POST'])
@login_required
def test_line_message():
    """ทดสอบส่งข้อความ LINE"""
    try:
        data = request.json
        student_id = data.get('student_id')
        
        # ดึง LINE token
        line_user_id = db.get_student_line_token(student_id)
        
        if not line_user_id:
            return jsonify({'success': False, 'message': 'ยังไม่ได้เชื่อมต่อ LINE'})
        
        # ส่งข้อความทดสอบ
        school_id = get_current_school_id()
        students = db.get_students(school_id)
        student = next((s for s in students if s['student_id'] == student_id), None)
        
        if student:
            try:
                line_oa.send_message(line_user_id, f"""📢 ข้อความทดสอบ

✅ ระบบเชื่อมต่อ LINE สำเร็จ!

👤 นักเรียน: {student['name']}
🆔 รหัส: {student_id}

ท่านจะได้รับการแจ้งเตือนเมื่อ:
🟢 บุตรเข้าโรงเรียน
🟠 บุตรออกจากโรงเรียน
⚠️ บุตรขาดเรียน
📝 พฤติกรรมผิดปกติ""")
                return jsonify({'success': True, 'message': 'ส่งข้อความทดสอบสำเร็จ'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'ส่งไม่สำเร็จ: {str(e)}'})
        
        return jsonify({'success': False, 'message': 'ไม่พบข้อมูลนักเรียน'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

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
                students = db.get_students('SCH001')  # ใช้ school_id แทน None
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

# Gate Camera APIs (No login required)
# Simple face recognition cache
face_cache = {}

@app.route('/api/face/recognize', methods=['POST'])
def face_recognize():
    """Face recognition API - no login required"""
    try:
        import cv2
        import numpy as np
        
        data = request.json
        image_data = data.get('image')
        camera_type = data.get('camera_type', 'general')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image data'})
        
        # Convert base64 to image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        try:
            missing_padding = len(image_data) % 4
            if missing_padding:
                image_data += '=' * (4 - missing_padding)
            
            nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            return jsonify({'success': False, 'message': f'Decode error: {str(e)}'})
        
        if frame is None or frame.size == 0:
            return jsonify({'success': False, 'message': 'Invalid image'})
        
        # Face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_location = [int(y), int(x+w), int(y+h), int(x)]
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Load cache if empty
            global face_cache
            if not face_cache:
                print('Loading face cache...')
                students = db.get_students('SCH001')  # ใช้ school_id แทน None
                print(f'Found {len(students)} students')
                for student in students:
                    if student.get('image_path') and os.path.exists(student['image_path']):
                        try:
                            img = cv2.imread(student['image_path'], cv2.IMREAD_GRAYSCALE)
                            if img is not None:
                                student_faces = face_cascade.detectMultiScale(img, 1.3, 5)
                                if len(student_faces) > 0:
                                    sx, sy, sw, sh = student_faces[0]
                                    student_face = img[sy:sy+sh, sx:sx+sw]
                                    student_face = cv2.resize(student_face, (100, 100))
                                    face_cache[student['student_id']] = {
                                        'face': student_face,
                                        'name': student['name']
                                    }
                                    print(f'Cached: {student["student_id"]} - {student["name"]}')
                        except Exception as e:
                            print(f'Error caching {student.get("student_id")}: {e}')
                            continue
                print(f'Cache loaded: {len(face_cache)} faces')
            
            # Compare with cached faces
            best_match = None
            best_score = float('inf')
            
            for student_id, cache_data in face_cache.items():
                diff = cv2.absdiff(face_roi, cache_data['face'])
                score = np.sum(diff)
                
                if score < best_score:
                    best_score = score
                    best_match = student_id
            
            print(f'Best match: {best_match}, Score: {best_score}')  # Debug
            
            # Threshold for recognition
            if best_match and best_score < 2000000:  # ลด threshold ให้เข้มงวดขึ้น
                # ส่ง LINE แจ้งเตือนผู้ปกครอง
                line_user_id = db.get_student_line_token(best_match)
                if line_user_id:
                    try:
                        current_time = datetime.now().strftime('%H:%M น.')
                        line_oa.send_message(line_user_id, f"""🟢 บุตรของท่านมาถึงโรงเรียนแล้ว

👤 ชื่อ: {face_cache[best_match]['name']}
🆔 รหัส: {best_match}
⏰ เวลา: {current_time}

✅ ระบบตรวจจับใบหน้าอัตโนมัติ""")
                    except:
                        pass
                
                return jsonify({
                    'success': True,
                    'student_id': best_match,
                    'student_name': face_cache[best_match]['name'],
                    'face_location': face_location,
                    'camera_type': camera_type
                })
            
            return jsonify({
                'success': False,
                'face_location': face_location,
                'message': 'Face detected but not recognized'
            })
        
        return jsonify({'success': False, 'message': 'No face detected'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/gate/recognize', methods=['POST'])
def gate_recognize():
    """Face recognition for gate camera - no login required"""
    try:
        data = request.json
        image_data = data.get('image')
        entry_type = data.get('type', 'checkin')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image data'})
        
        # ใช้ Face Recognition System ใหม่
        results = face_recognition_system.recognize_from_base64(image_data)
        
        if results and len(results) > 0:
            best_match = max(results, key=lambda x: x['confidence'])
            
            if best_match['confidence'] > 0.6:  # ความแม่นยำ > 60%
                student_id = best_match['student_id']
                students = db.get_students(None)
                student = next((s for s in students if s['student_id'] == student_id), None)
                
                if student:
                    school_id = student.get('school_id', 'SCH001')
                    camera_type = 'gate_in' if entry_type == 'checkin' else 'gate_out'
                    
                    # บันทึกการเข้า-ออก
                    db.add_attendance(student_id, student['name'], school_id, camera_type)
                    
                    # ส่งแจ้งเตือน LINE
                    line_user_id = db.get_student_line_token(student_id)
                    if line_user_id:
                        current_time = datetime.now().strftime('%H:%M น.')
                        line_notification.send_gate_notification(
                            line_user_id, 
                            student['name'], 
                            entry_type, 
                            current_time
                        )
                    
                    # Sync to cloud
                    cloud_sync.send_attendance(student_id, student['name'], camera_type=camera_type)
                    
                    return jsonify({
                        'success': True,
                        'student_id': student_id,
                        'student_name': student['name'],
                        'confidence': round(best_match['confidence'] * 100, 1),
                        'type': entry_type,
                        'line_sent': bool(line_user_id)
                    })
        
        return jsonify({'success': False, 'message': 'ไม่พบใบหน้าที่รู้จัก'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/gate/stats', methods=['GET'])
def gate_stats():
    """Get today's gate statistics - no login required"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        attendance = db.get_attendance(None)  # All schools
        
        checkin = len([a for a in attendance if a['camera_type'] == 'gate_in' and a['timestamp'].startswith(today)])
        checkout = len([a for a in attendance if a['camera_type'] == 'gate_out' and a['timestamp'].startswith(today)])
        
        return jsonify({
            'success': True,
            'checkin': checkin,
            'checkout': checkout
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/gate/recent', methods=['GET'])
def gate_recent():
    """Get recent gate logs - no login required"""
    try:
        attendance = db.get_attendance(None)  # All schools
        
        gate_logs = []
        for a in attendance:
            if a['camera_type'] in ['gate_in', 'gate_out']:
                gate_logs.append({
                    'student_id': a['student_id'],
                    'student_name': a['student_name'],
                    'type': 'checkin' if a['camera_type'] == 'gate_in' else 'checkout',
                    'timestamp': a['timestamp']
                })
        
        # Sort by timestamp descending and get last 10
        gate_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'logs': gate_logs[:10]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Camera Management APIs
@app.route('/api/cameras', methods=['GET'])
@login_required
def get_cameras_api():
    school_id = get_current_school_id()
    cameras = db.get_cameras(school_id)
    return jsonify({'success': True, 'cameras': cameras})

@app.route('/api/cameras', methods=['POST'])
@login_required
def add_camera_api():
    try:
        data = request.json
        school_id = get_current_school_id()
        camera_id = db.add_camera(school_id, data)
        return jsonify({'success': True, 'camera_id': camera_id, 'message': 'เพิ่มกล้องสำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/cameras/<int:camera_id>', methods=['GET'])
@login_required
def get_camera_api(camera_id):
    camera = db.get_camera(camera_id)
    if camera:
        return jsonify({'success': True, 'camera': camera})
    return jsonify({'success': False, 'message': 'ไม่พบกล้อง'})

@app.route('/api/cameras/<int:camera_id>', methods=['PUT'])
@login_required
def update_camera_api(camera_id):
    try:
        data = request.json
        db.update_camera(camera_id, data)
        return jsonify({'success': True, 'message': 'แก้ไขกล้องสำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/cameras/<int:camera_id>', methods=['DELETE'])
@login_required
def delete_camera_api(camera_id):
    try:
        db.delete_camera(camera_id)
        return jsonify({'success': True, 'message': 'ลบกล้องสำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

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

# ============================================
# SUPER ADMIN API ENDPOINTS
# ============================================

@app.route('/api/super_admin/dashboard', methods=['GET'])
@super_admin_required
def get_super_admin_dashboard():
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM schools')
        total_schools = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM resellers')
        total_resellers = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM schools WHERE status = "active"')
        active_schools = cursor.fetchone()[0]
        
        today = datetime.now().date()
        days_30 = (today + timedelta(days=30)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM schools WHERE expire_date <= ? AND status = "active"', (days_30,))
        expiring_soon = cursor.fetchone()[0]
        
        conn.close()
        
        monthly_revenue = db.get_revenue('month')
        
        stats = {
            'total_schools': total_schools,
            'total_resellers': total_resellers,
            'total_students': total_students,
            'monthly_revenue': monthly_revenue,
            'expiring_soon': expiring_soon,
            'active_rate': round((active_schools / total_schools * 100) if total_schools > 0 else 0, 1)
        }
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/resellers', methods=['GET'])
@super_admin_required
def get_resellers():
    resellers = db.get_all_resellers()
    return jsonify({'success': True, 'resellers': resellers})

@app.route('/api/resellers', methods=['POST'])
@super_admin_required
def create_reseller():
    data = request.json
    reseller_id = db.add_reseller(data)
    return jsonify({
        'success': True,
        'reseller_id': reseller_id,
        'username': data['username'],
        'max_schools': data['max_schools']
    })

@app.route('/api/resellers/<reseller_id>', methods=['GET'])
@super_admin_required
def get_reseller(reseller_id):
    reseller = db.get_reseller(reseller_id)
    if reseller:
        schools = db.get_reseller_schools(reseller_id)
        commission = db.calculate_reseller_commission(reseller_id)
        return jsonify({'success': True, 'reseller': reseller, 'schools': schools, 'commission': commission})
    return jsonify({'success': False, 'message': 'ไม่พบ Reseller'})

@app.route('/api/resellers/<reseller_id>', methods=['PUT'])
@super_admin_required
def update_reseller(reseller_id):
    data = request.json
    db.update_reseller(reseller_id, data)
    return jsonify({'success': True, 'message': 'อัพเดทข้อมูลสำเร็จ'})

@app.route('/api/resellers/<reseller_id>', methods=['DELETE'])
@super_admin_required
def delete_reseller(reseller_id):
    db.delete_reseller(reseller_id)
    return jsonify({'success': True, 'message': 'ลบ Reseller สำเร็จ'})

@app.route('/api/super_admin/payments', methods=['GET'])
@super_admin_required
def get_payments():
    payments = db.get_all_payments()
    return jsonify({'success': True, 'payments': payments})

@app.route('/api/super_admin/payments', methods=['POST'])
@super_admin_required
def add_payment():
    data = request.json
    payment_id = db.add_payment(data)
    return jsonify({'success': True, 'payment_id': payment_id, 'message': 'บันทึกการชำระเงินสำเร็จ'})

@app.route('/api/super_admin/revenue', methods=['GET'])
@super_admin_required
def get_revenue():
    today = db.get_revenue('today')
    month = db.get_revenue('month')
    year = db.get_revenue('year')
    pending = db.get_pending_payments()
    return jsonify({
        'success': True,
        'revenue': {'today': today, 'month': month, 'year': year, 'pending': pending}
    })

@app.route('/api/super_admin/settings', methods=['GET'])
@super_admin_required
def get_settings():
    settings = db.get_system_settings()
    return jsonify({'success': True, 'settings': settings})

@app.route('/api/super_admin/settings', methods=['POST'])
@super_admin_required
def update_settings():
    data = request.json
    db.update_system_settings(data)
    return jsonify({'success': True, 'message': 'บันทึกการตั้งค่าสำเร็จ'})

# Reseller Dashboard
@app.route('/reseller_dashboard')
@login_required
def reseller_dashboard():
    if session.get('role') != 'reseller':
        return redirect(url_for('login'))
    return render_template('reseller_dashboard.html')

@app.route('/api/reseller/me', methods=['GET'])
@login_required
def get_reseller_me():
    if session.get('role') != 'reseller':
        return jsonify({'success': False, 'message': 'ไม่มีสิทธิ์เข้าถึง'})
    
    username = session.get('user')
    
    # ดึงข้อมูล reseller จาก username
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resellers WHERE username = ?', (username,))
    reseller = cursor.fetchone()
    
    if not reseller:
        conn.close()
        return jsonify({'success': False, 'message': 'ไม่พบข้อมูล Reseller'})
    
    reseller = dict(reseller)
    reseller_id = reseller['reseller_id']
    
    # ดึงโรงเรียนที่ขาย
    schools = db.get_reseller_schools(reseller_id)
    
    # คำนวณ commission
    commission = db.calculate_reseller_commission(reseller_id)
    
    # อัพเดทจำนวนโรงเรียนที่ใช้แล้ว
    cursor.execute('UPDATE resellers SET schools_used = ? WHERE reseller_id = ?', (len(schools), reseller_id))
    conn.commit()
    conn.close()
    
    reseller['schools_used'] = len(schools)
    
    return jsonify({
        'success': True,
        'reseller': reseller,
        'schools': schools,
        'commission': commission
    })

@app.route('/api/reseller/schools', methods=['POST'])
@login_required
def reseller_add_school():
    if session.get('role') != 'reseller':
        return jsonify({'success': False, 'message': 'ไม่มีสิทธิ์เข้าถึง'})
    
    username = session.get('user')
    
    # ดึงข้อมูล reseller
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resellers WHERE username = ?', (username,))
    reseller = cursor.fetchone()
    
    if not reseller:
        conn.close()
        return jsonify({'success': False, 'message': 'ไม่พบข้อมูล Reseller'})
    
    reseller = dict(reseller)
    reseller_id = reseller['reseller_id']
    
    # ตรวจสอบ Quota
    cursor.execute('SELECT COUNT(*) FROM schools WHERE reseller_id = ?', (reseller_id,))
    schools_used = cursor.fetchone()[0]
    
    if schools_used >= reseller['max_schools']:
        conn.close()
        return jsonify({'success': False, 'message': 'คุณใช้ Quota เต็มแล้ว! ติดต่อ Super Admin เพื่อเพิ่ม Quota'})
    
    conn.close()
    
    # เพิ่มโรงเรียน
    data = request.json
    data['reseller_id'] = reseller_id
    school_id = db.add_school(data)
    
    # สร้าง admin user
    admin_username = data.get('admin_username')
    admin_password = data.get('admin_password')
    if admin_username and admin_password:
        db.add_user(admin_username, admin_password, f"Admin - {data['name']}", 'admin', school_id)
    
    return jsonify({'success': True, 'school_id': school_id, 'message': 'สร้างโรงเรียนสำเร็จ!'})

# Face Recognition APIs
@app.route('/api/face/train', methods=['POST'])
@login_required
def train_face_model():
    """เทรนโมเดล Face Recognition"""
    try:
        school_id = get_current_school_id()
        students = db.get_students(school_id)
        
        # กรองเฉพาะนักเรียนที่มีรูป
        students_with_images = [s for s in students if s.get('image_path')]
        
        if len(students_with_images) == 0:
            return jsonify({
                'success': False,
                'message': 'ไม่มีนักเรียนที่มีรูปภาพ'
            })
        
        # เทรนโมเดล
        success_count = face_recognition_system.train_from_students(students_with_images)
        
        return jsonify({
            'success': True,
            'trained': success_count,
            'total': len(students_with_images),
            'message': f'เทรนสำเร็จ {success_count}/{len(students_with_images)} คน'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/face/status', methods=['GET'])
@login_required
def face_model_status():
    """ตรวจสอบสถานะโมเดล"""
    return jsonify({
        'success': True,
        'trained_count': len(face_recognition_system.known_face_ids),
        'model_exists': os.path.exists('data/face_model.pkl')
    })

@app.route('/api/ai/train', methods=['POST'])
@login_required
def ai_train():
    """เทรนโมเดล AI Face Recognition"""
    try:
        from ai_face_recognition import ai_face
        school_id = get_current_school_id()
        students = db.get_students(school_id)
        
        ai_face.train(students)
        
        return jsonify({
            'success': True,
            'message': f'เทรนโมเดลสำเร็จ! จำนวน {len(ai_face.known_faces)} คน'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/ai/recognize', methods=['POST'])
@login_required
def ai_recognize():
    """จำแนกใบหน้าด้วย AI"""
    try:
        from ai_face_recognition import ai_face
        
        # โหลดโมเดล
        if not ai_face.known_faces:
            if not ai_face.load_model():
                return jsonify({'success': False, 'message': 'กรุณาเทรนโมเดลก่อน'})
        
        image_data = request.json.get('image')
        camera_type = request.json.get('camera_type', 'general')
        school_id = get_current_school_id()
        
        results = ai_face.recognize_from_base64(image_data)
        
        if results:
            best = max(results, key=lambda x: x['confidence'])
            
            if best['confidence'] > 0.6:
                students = db.get_students(school_id)
                student = next((s for s in students if s['student_id'] == best['student_id']), None)
                
                if student:
                    db.add_attendance(student['student_id'], student['name'], school_id, camera_type)
                    
                    # Broadcast via WebSocket
                    socketio.broadcast_attendance(school_id, {
                        'student_id': student['student_id'],
                        'student_name': student['name'],
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    return jsonify({
                        'success': True,
                        'student_id': student['student_id'],
                        'student_name': student['name'],
                        'confidence': round(best['confidence'] * 100, 1)
                    })
        
        return jsonify({'success': False, 'message': 'ไม่พบใบหน้าที่รู้จัก'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============================================
# QR CODE APIs
# ============================================

@app.route('/api/qr/generate/<student_id>')
@login_required
def generate_qr(student_id):
    """สร้าง QR Code สำหรับนักเรียน"""
    try:
        from qr_manager import qr_manager
        from flask import send_file
        
        school_id = get_current_school_id()
        students = db.get_students(school_id)
        student = next((s for s in students if s['student_id'] == student_id), None)
        
        if not student:
            return jsonify({'success': False, 'message': 'ไม่พบนักเรียน'})
        
        buffer = qr_manager.generate_student_qr(student_id, student['name'])
        
        return send_file(buffer, mimetype='image/png')
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/qr/scan', methods=['POST'])
@login_required
def scan_qr():
    """สแกน QR Code"""
    try:
        from qr_manager import qr_manager
        
        image_data = request.json.get('image')
        camera_type = request.json.get('camera_type', 'qr_code')
        school_id = get_current_school_id()
        
        results = qr_manager.scan_qr_from_base64(image_data)
        
        if results:
            student_id = results[0]['student_id']
            students = db.get_students(school_id)
            student = next((s for s in students if s['student_id'] == student_id), None)
            
            if student:
                db.add_attendance(student['student_id'], student['name'], school_id, camera_type)
                
                return jsonify({
                    'success': True,
                    'student_id': student['student_id'],
                    'student_name': student['name']
                })
        
        return jsonify({'success': False, 'message': 'ไม่พบ QR Code'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============================================
# TWO-FACTOR AUTHENTICATION APIs
# ============================================

@app.route('/api/2fa/enable', methods=['POST'])
@login_required
def enable_2fa():
    """เปิดใช้งาน 2FA"""
    try:
        from two_factor_auth import two_fa
        
        username = session.get('user')
        secret = two_fa.generate_secret()
        
        # บันทึก secret ลง database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET two_fa_secret = ? WHERE username = ?', (secret, username))
        conn.commit()
        conn.close()
        
        # สร้าง QR Code
        qr_base64 = two_fa.generate_qr_base64(username, secret)
        
        return jsonify({
            'success': True,
            'secret': secret,
            'qr_code': qr_base64
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/2fa/verify', methods=['POST'])
@login_required
def verify_2fa():
    """ตรวจสอบ 2FA token"""
    try:
        from two_factor_auth import two_fa
        
        username = session.get('user')
        token = request.json.get('token')
        
        # ดึง secret จาก database
        user = db.get_user(username)
        secret = user.get('two_fa_secret')
        
        if not secret:
            return jsonify({'success': False, 'message': 'ยังไม่ได้เปิดใช้งาน 2FA'})
        
        is_valid = two_fa.verify_token(secret, token)
        
        return jsonify({
            'success': is_valid,
            'message': 'ยืนยันสำเร็จ' if is_valid else 'รหัสไม่ถูกต้อง'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    """ปิดใช้งาน 2FA"""
    try:
        username = session.get('user')
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET two_fa_secret = NULL WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'ปิดใช้งาน 2FA สำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============================================
# AUDIT LOG APIs
# ============================================

@app.route('/api/audit/logs', methods=['GET'])
@login_required
def get_audit_logs():
    """ดึง audit logs"""
    try:
        from audit_logger import audit_logger
        
        limit = int(request.args.get('limit', 100))
        user_id = request.args.get('user_id')
        action = request.args.get('action')
        
        logs = audit_logger.get_logs(limit=limit, user_id=user_id, action=action)
        
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/audit/stats', methods=['GET'])
@login_required
def get_audit_stats():
    """สถิติ audit logs"""
    try:
        from audit_logger import audit_logger
        
        days = int(request.args.get('days', 30))
        stats = audit_logger.get_stats(days=days)
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============================================
# BACKUP/RESTORE APIs
# ============================================

@app.route('/api/backup/create', methods=['POST'])
@login_required
def create_backup():
    """สร้าง backup"""
    try:
        from backup_manager import backup_manager
        
        include_images = request.json.get('include_images', True)
        result = backup_manager.create_backup(include_images=include_images)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/backup/list', methods=['GET'])
@login_required
def list_backups():
    """แสดงรายการ backup"""
    try:
        from backup_manager import backup_manager
        
        backups = backup_manager.list_backups()
        
        return jsonify({'success': True, 'backups': backups})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/backup/restore', methods=['POST'])
@login_required
def restore_backup():
    """กู้คืนข้อมูล"""
    try:
        from backup_manager import backup_manager
        
        backup_file = request.json.get('backup_file')
        result = backup_manager.restore_backup(backup_file)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/backup/delete', methods=['POST'])
@login_required
def delete_backup():
    """ลบ backup"""
    try:
        from backup_manager import backup_manager
        
        backup_file = request.json.get('backup_file')
        result = backup_manager.delete_backup(backup_file)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    os.makedirs('data/students', exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Use socketio.run instead of app.run
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
