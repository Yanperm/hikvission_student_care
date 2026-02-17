from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from security.password_manager import password_manager
from security.rate_limiter import limiter, LOGIN_LIMIT
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_page():
    return render_template('login.html')

@auth_bp.route('/api/login', methods=['POST'])
@limiter.limit(LOGIN_LIMIT)
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบ'}), 400
    
    user = db.get_user(username)
    
    if user and password_manager.verify_password(password, user['password']):
        session.permanent = True
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
    
    return jsonify({'success': False, 'message': 'Username หรือ Password ไม่ถูกต้อง'}), 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))
