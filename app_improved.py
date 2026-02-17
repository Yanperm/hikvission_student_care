from flask import Flask, render_template, session
from flask_cors import CORS
import os

# Import config
from config import Config

# Import security
from security.csrf_protection import csrf
from security.rate_limiter import limiter

# Import blueprints
from routes.auth import auth_bp
from routes.students import student_bp

# Import database
from database_improved import db

# Import WebSocket
from websocket_manager import init_socketio

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Initialize WebSocket
    socketio = init_socketio(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    
    # Main routes
    @app.route('/')
    def index():
        return render_template('professional_landing.html')
    
    @app.route('/admin')
    def admin():
        if 'user' not in session:
            return render_template('login.html')
        
        school_id = session.get('school_id', 'SCH001')
        students = db.get_students(school_id)
        school = db.get_school(school_id) if school_id else None
        
        return render_template('admin_dashboard.html', 
                             students=students,
                             school_name=school['name'] if school else 'โรงเรียน',
                             user_name=session.get('name', 'ผู้ใช้งาน'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(e):
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'error': 'Rate limit exceeded'}, 429
    
    return app, socketio

if __name__ == '__main__':
    os.makedirs('data/students', exist_ok=True)
    app, socketio = create_app()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
