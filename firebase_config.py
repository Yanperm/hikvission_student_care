import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
import json

class FirebaseManager:
    def __init__(self, service_account_path=None):
        if not firebase_admin._apps:
            if service_account_path:
                cred = credentials.Certificate(service_account_path)
            else:
                # ใช้ default credentials หรือ environment variables
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
    
    def add_student(self, student_id, name, image_data=None):
        """เพิ่มนักเรียนใน Firestore"""
        try:
            doc_ref = self.db.collection('students').document(student_id)
            doc_ref.set({
                'student_id': student_id,
                'name': name,
                'created_at': datetime.now(),
                'active': True
            })
            return True, "เพิ่มนักเรียนสำเร็จ"
        except Exception as e:
            return False, f"เกิดข้อผิดพลาด: {str(e)}"
    
    def get_students(self):
        """ดึงข้อมูลนักเรียนทั้งหมด"""
        try:
            students = {}
            docs = self.db.collection('students').where('active', '==', True).stream()
            
            for doc in docs:
                data = doc.to_dict()
                students[doc.id] = {
                    'student_id': data['student_id'],
                    'name': data['name']
                }
            return students
        except Exception as e:
            print(f"Error getting students: {e}")
            return {}
    
    def record_attendance(self, student_id, student_name):
        """บันทึกการเข้าเรียน"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            time_str = datetime.now().strftime("%H:%M:%S")
            
            doc_ref = self.db.collection('attendance').add({
                'student_id': student_id,
                'student_name': student_name,
                'date': today,
                'time': time_str,
                'timestamp': datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error recording attendance: {e}")
            return False
    
    def get_today_attendance(self):
        """ดึงข้อมูลการเข้าเรียนวันนี้"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            docs = self.db.collection('attendance').where('date', '==', today).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                results.append((data['student_id'], data['student_name'], data['time']))
            
            return results
        except Exception as e:
            print(f"Error getting attendance: {e}")
            return []