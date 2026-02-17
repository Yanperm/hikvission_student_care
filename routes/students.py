from flask import Blueprint, request, jsonify, session
from functools import wraps
from security.rate_limiter import limiter, UPLOAD_LIMIT, API_LIMIT
from database import db
import os
import base64
from datetime import datetime

student_bp = Blueprint('student', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_school_id():
    return session.get('school_id', 'SCH001')

@student_bp.route('/api/students', methods=['GET'])
@limiter.limit(API_LIMIT)
@login_required
def get_students():
    school_id = get_current_school_id()
    students = db.get_students(school_id)
    return jsonify({'success': True, 'students': students})

@student_bp.route('/add_student', methods=['POST'])
@limiter.limit(UPLOAD_LIMIT)
@login_required
def add_student():
    try:
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        class_name = request.form.get('class_name', '')
        image_data = request.form.get('image_data')
        school_id = get_current_school_id()
        
        if not student_id or not name or not image_data:
            return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบถ้วน'}), 400
        
        os.makedirs('data/students', exist_ok=True)
        image_path = f"data/students/{student_id}.jpg"
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_data += '=' * (4 - len(image_data) % 4)
        
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_data))
        
        students = db.get_students(school_id)
        existing = any(s['student_id'] == student_id for s in students)
        
        if existing:
            db.update_student(student_id, name, class_name, school_id, image_path)
            message = f'อัพเดทข้อมูล {name} สำเร็จ'
        else:
            db.add_student(student_id, name, class_name, school_id, image_path)
            message = f'เพิ่มนักเรียน {name} สำเร็จ'
        
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@student_bp.route('/delete_student/<student_id>', methods=['DELETE'])
@limiter.limit(API_LIMIT)
@login_required
def delete_student(student_id):
    try:
        image_path = f'data/students/{student_id}.jpg'
        if os.path.exists(image_path):
            os.remove(image_path)
        
        db.delete_student(student_id)
        return jsonify({'success': True, 'message': 'ลบนักเรียนสำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
