import requests
import json
from datetime import datetime

class CloudSync:
    def __init__(self, api_url):
        self.api_url = api_url
    
    def send_attendance(self, student_id, student_name, timestamp=None, camera_type='general'):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        data = {
            'student_id': student_id,
            'student_name': student_name,
            'timestamp': timestamp,
            'status': 'present',
            'camera_type': camera_type
        }
        
        try:
            response = requests.post(f"{self.api_url}/api/attendance", json=data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to sync: {e}")
            return False
    
    def send_behavior(self, student_id, student_name, behavior, severity='normal', timestamp=None, camera_type='behavior'):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        data = {
            'student_id': student_id,
            'student_name': student_name,
            'timestamp': timestamp,
            'behavior': behavior,
            'severity': severity,
            'camera_type': camera_type
        }
        
        try:
            response = requests.post(f"{self.api_url}/api/behavior", json=data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to sync behavior: {e}")
            return False
    
    def sync_student(self, student_id, student_name, class_name, image_path=None):
        data = {
            'student_id': student_id,
            'student_name': student_name,
            'class_name': class_name
        }
        
        try:
            if image_path:
                with open(image_path, 'rb') as f:
                    files = {'image': f}
                    response = requests.post(f"{self.api_url}/api/students", data=data, files=files, timeout=10)
            else:
                response = requests.post(f"{self.api_url}/api/students", json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to sync student: {e}")
            return False
