"""
Advanced Face Recognition with Deep Learning
ใช้ face_recognition library (dlib) สำหรับ accuracy สูง 95-99%
"""

import face_recognition
import numpy as np
import cv2
import os
import pickle
from datetime import datetime

class AdvancedFaceRecognition:
    def __init__(self, data_dir='data/students'):
        self.data_dir = data_dir
        self.known_faces = []
        self.known_ids = []
        self.model_file = 'data/face_model.pkl'
        
    def train(self, students):
        """เทรนโมเดลจากรูปนักเรียน"""
        print("🤖 กำลังเทรนโมเดล AI...")
        self.known_faces = []
        self.known_ids = []
        
        for student in students:
            image_path = student.get('image_path')
            if image_path and os.path.exists(image_path):
                try:
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        self.known_faces.append(encodings[0])
                        self.known_ids.append(student['student_id'])
                        print(f"✅ เทรน: {student['name']}")
                except Exception as e:
                    print(f"❌ ข้ามไฟล์: {image_path} - {e}")
        
        # บันทึกโมเดล
        self.save_model()
        print(f"✅ เทรนเสร็จ! จำนวน: {len(self.known_faces)} คน")
        
    def save_model(self):
        """บันทึกโมเดล"""
        os.makedirs('data', exist_ok=True)
        with open(self.model_file, 'wb') as f:
            pickle.dump({
                'faces': self.known_faces,
                'ids': self.known_ids
            }, f)
        print(f"💾 บันทึกโมเดล: {self.model_file}")
    
    def load_model(self):
        """โหลดโมเดล"""
        if os.path.exists(self.model_file):
            with open(self.model_file, 'rb') as f:
                data = pickle.load(f)
                self.known_faces = data['faces']
                self.known_ids = data['ids']
            print(f"📂 โหลดโมเดล: {len(self.known_faces)} คน")
            return True
        return False
    
    def recognize(self, frame, tolerance=0.6):
        """จำแนกใบหน้าจากภาพ"""
        # ลดขนาดเพื่อประมวลผลเร็วขึ้น
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # หาใบหน้า
        face_locations = face_recognition.face_locations(rgb_frame, model='hog')
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        results = []
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # เปรียบเทียบกับใบหน้าที่รู้จัก
            matches = face_recognition.compare_faces(self.known_faces, face_encoding, tolerance=tolerance)
            face_distances = face_recognition.face_distance(self.known_faces, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    student_id = self.known_ids[best_match_index]
                    confidence = 1 - face_distances[best_match_index]
                    
                    # ขยายตำแหน่งกลับเป็นขนาดเดิม
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    results.append({
                        'student_id': student_id,
                        'confidence': float(confidence),
                        'location': (top, right, bottom, left)
                    })
        
        return results
    
    def recognize_from_base64(self, image_data):
        """จำแนกจาก base64 image"""
        import base64
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return self.recognize(frame)

# สร้าง instance
ai_face = AdvancedFaceRecognition()
