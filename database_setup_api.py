"""
Database Setup API
API สำหรับตั้งค่า Database ผ่าน UI
"""

from flask import Blueprint, request, jsonify, render_template
import mysql.connector
import os

db_setup_bp = Blueprint('db_setup', __name__)

@db_setup_bp.route('/database_setup')
def database_setup():
    return render_template('database_setup.html')

@db_setup_bp.route('/api/database/test', methods=['POST'])
def test_database():
    """ทดสอบการเชื่อมต่อ Database"""
    try:
        config = request.json
        
        conn = mysql.connector.connect(
            host=config['host'],
            port=int(config['port']),
            user=config['user'],
            password=config['password'],
            database=config['database'],
            connect_timeout=5
        )
        conn.close()
        
        return jsonify({'success': True, 'message': 'เชื่อมต่อสำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@db_setup_bp.route('/api/database/save', methods=['POST'])
def save_database_config():
    """บันทึกการตั้งค่า Database"""
    try:
        config = request.json
        
        # อ่าน .env เดิม (ถ้ามี)
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_lines = [line for line in f.readlines() if not line.startswith('MYSQL_') and not line.startswith('USE_MYSQL')]
        
        # เพิ่มค่าใหม่
        env_lines.append(f"USE_MYSQL=true\n")
        env_lines.append(f"MYSQL_HOST={config['host']}\n")
        env_lines.append(f"MYSQL_PORT={config['port']}\n")
        env_lines.append(f"MYSQL_USER={config['user']}\n")
        env_lines.append(f"MYSQL_PASSWORD={config['password']}\n")
        env_lines.append(f"MYSQL_DATABASE={config['database']}\n")
        
        # บันทึก
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        return jsonify({'success': True, 'message': 'บันทึกสำเร็จ'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@db_setup_bp.route('/api/database/current', methods=['GET'])
def get_current_database():
    """ดูการตั้งค่าปัจจุบัน"""
    try:
        use_mysql = os.getenv('USE_MYSQL', 'false').lower() == 'true'
        db_type = 'mysql' if use_mysql else 'sqlite'
        
        return jsonify({
            'success': True,
            'type': db_type,
            'connected': True
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
