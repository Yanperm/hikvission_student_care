from flask import Blueprint, request, jsonify
from auth_manager import auth_manager
from validator import validator
from logger_manager import logger
from analytics_manager import AnalyticsManager
from backup_manager import backup_manager
from config_manager import config_manager

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/auth/login', methods=['POST'])
def login():
    """User authentication"""
    try:
        data = request.get_json()
        username = validator.sanitize_input(data.get('username'))
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Rate limiting
        client_ip = request.remote_addr
        rate_ok, rate_msg = validator.rate_limit_check(client_ip, max_requests=10, window_minutes=15)
        if not rate_ok:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return jsonify({'error': rate_msg}), 429
        
        if auth_manager.verify_password(username, password):
            token = auth_manager.generate_token(username)
            logger.info(f"User {username} logged in successfully")
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'username': username,
                    'role': auth_manager.users[username]['role'],
                    'name': auth_manager.users[username]['name']
                }
            })
        else:
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/students', methods=['GET'])
@auth_manager.require_auth()
def get_students():
    """Get all students"""
    try:
        # This would integrate with your database manager
        students = {}  # system.db.get_students()
        return jsonify({
            'success': True,
            'data': students,
            'count': len(students)
        })
    except Exception as e:
        logger.error(f"Get students error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve students'}), 500

@api.route('/students', methods=['POST'])
@auth_manager.require_auth(required_role='admin')
def add_student():
    """Add new student"""
    try:
        data = request.get_json()
        
        # Validate input
        student_id = validator.sanitize_input(data.get('student_id'))
        name = validator.sanitize_input(data.get('name'))
        
        valid_id, id_msg = validator.validate_student_id(student_id)
        if not valid_id:
            return jsonify({'error': id_msg}), 400
        
        valid_name, name_msg = validator.validate_name(name)
        if not valid_name:
            return jsonify({'error': name_msg}), 400
        
        # Add student logic here
        # success, message = system.add_student(student_id, name)
        
        logger.info(f"Student added: {student_id} - {name}")
        return jsonify({
            'success': True,
            'message': 'Student added successfully'
        })
        
    except Exception as e:
        logger.error(f"Add student error: {str(e)}")
        return jsonify({'error': 'Failed to add student'}), 500

@api.route('/attendance/today', methods=['GET'])
@auth_manager.require_auth()
def get_today_attendance():
    """Get today's attendance"""
    try:
        # This would integrate with your database manager
        attendance = []  # system.get_today_attendance()
        return jsonify({
            'success': True,
            'data': attendance,
            'count': len(attendance)
        })
    except Exception as e:
        logger.error(f"Get attendance error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve attendance'}), 500

@api.route('/reports/attendance', methods=['GET'])
@auth_manager.require_auth()
def get_attendance_report():
    """Generate attendance report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # This would integrate with analytics manager
        # analytics = AnalyticsManager(system.db)
        # report = analytics.get_attendance_report(start_date, end_date)
        
        report = {'message': 'Report generation not implemented yet'}
        
        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate report'}), 500

@api.route('/system/backup', methods=['POST'])
@auth_manager.require_auth(required_role='admin')
def create_backup():
    """Create system backup"""
    try:
        include_images = request.get_json().get('include_images', True)
        
        success, result = backup_manager.create_backup(include_images)
        
        if success:
            logger.info(f"Backup created: {result}")
            return jsonify({
                'success': True,
                'message': 'Backup created successfully',
                'backup_file': result
            })
        else:
            logger.error(f"Backup failed: {result}")
            return jsonify({'error': result}), 500
            
    except Exception as e:
        logger.error(f"Backup error: {str(e)}")
        return jsonify({'error': 'Backup failed'}), 500

@api.route('/system/backups', methods=['GET'])
@auth_manager.require_auth(required_role='admin')
def list_backups():
    """List all backups"""
    try:
        backups = backup_manager.list_backups()
        return jsonify({
            'success': True,
            'data': backups,
            'count': len(backups)
        })
    except Exception as e:
        logger.error(f"List backups error: {str(e)}")
        return jsonify({'error': 'Failed to list backups'}), 500

@api.route('/system/config', methods=['GET'])
@auth_manager.require_auth(required_role='admin')
def get_config():
    """Get system configuration"""
    try:
        return jsonify({
            'success': True,
            'data': config_manager.config
        })
    except Exception as e:
        logger.error(f"Get config error: {str(e)}")
        return jsonify({'error': 'Failed to get configuration'}), 500

@api.route('/system/config', methods=['PUT'])
@auth_manager.require_auth(required_role='admin')
def update_config():
    """Update system configuration"""
    try:
        data = request.get_json()
        
        for key, value in data.items():
            config_manager.set(key, value)
        
        logger.info("System configuration updated")
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully'
        })
    except Exception as e:
        logger.error(f"Update config error: {str(e)}")
        return jsonify({'error': 'Failed to update configuration'}), 500

@api.route('/system/status', methods=['GET'])
@auth_manager.require_auth()
def get_system_status():
    """Get system status"""
    try:
        # This would check various system components
        status = {
            'database': 'connected',
            'camera': 'active',
            'face_recognition': 'ready',
            'uptime': '2h 30m',
            'memory_usage': '45%',
            'cpu_usage': '23%'
        }
        
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"System status error: {str(e)}")
        return jsonify({'error': 'Failed to get system status'}), 500

@api.route('/camera/control', methods=['POST'])
@auth_manager.require_auth()
def camera_control():
    """Control camera (start/stop)"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'start' or 'stop'
        
        if action not in ['start', 'stop']:
            return jsonify({'error': 'Invalid action'}), 400
        
        # This would integrate with your camera system
        # if action == 'start':
        #     system.start_camera()
        # else:
        #     system.stop_camera()
        
        logger.info(f"Camera {action} command executed")
        return jsonify({
            'success': True,
            'message': f'Camera {action}ed successfully'
        })
    except Exception as e:
        logger.error(f"Camera control error: {str(e)}")
        return jsonify({'error': 'Camera control failed'}), 500

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@api.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500