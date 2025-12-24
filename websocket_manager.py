"""
Real-time WebSocket Manager
สำหรับ live camera feed และ notifications
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from functools import wraps

def init_socketio(app):
    """Initialize SocketIO"""
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    @socketio.on('connect')
    def handle_connect():
        print('✅ Client connected')
        emit('connected', {'message': 'Connected to server'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('❌ Client disconnected')
    
    @socketio.on('join_school')
    def handle_join_school(data):
        """Join school room for notifications"""
        school_id = data.get('school_id')
        join_room(school_id)
        emit('joined', {'school_id': school_id})
    
    @socketio.on('leave_school')
    def handle_leave_school(data):
        """Leave school room"""
        school_id = data.get('school_id')
        leave_room(school_id)
    
    @socketio.on('request_camera_feed')
    def handle_camera_feed(data):
        """Request camera feed"""
        camera_id = data.get('camera_id')
        emit('camera_feed_started', {'camera_id': camera_id})
    
    @socketio.on('stop_camera_feed')
    def handle_stop_camera(data):
        """Stop camera feed"""
        camera_id = data.get('camera_id')
        emit('camera_feed_stopped', {'camera_id': camera_id})
    
    # Helper functions
    def broadcast_attendance(school_id, attendance_data):
        """Broadcast attendance to school room"""
        socketio.emit('new_attendance', attendance_data, room=school_id)
    
    def broadcast_notification(school_id, notification_data):
        """Broadcast notification to school room"""
        socketio.emit('new_notification', notification_data, room=school_id)
    
    def broadcast_behavior(school_id, behavior_data):
        """Broadcast behavior alert to school room"""
        socketio.emit('new_behavior', behavior_data, room=school_id)
    
    # Attach helper functions to socketio
    socketio.broadcast_attendance = broadcast_attendance
    socketio.broadcast_notification = broadcast_notification
    socketio.broadcast_behavior = broadcast_behavior
    
    return socketio
