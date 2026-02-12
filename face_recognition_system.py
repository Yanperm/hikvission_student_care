"""
Face Recognition System (OpenCV Version)
ระบบจดจำใบหน้าที่แม่นยำด้วย OpenCV
"""

import cv2
import numpy as np
import os
import pickle
from datetime import datetime

class FaceRecognitionSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.known_faces = {}  # {student_id: face_features}
        self.labels_path = 'data/face_labels.pkl'
        self.load_model()
    
    def train_from_students(self, students):
        """เทรนโมเดลจากข้อมูลนักเรียน"""
        print("🔄 กำลังเทรนโมเดล Face Recognition...")
        
        success_count = 0
        for student in students:
            image_path = student.get('image_path')
            student_id = student.get('student_id')
            
            if not image_path or not os.path.exists(image_path):
                continue
            
            try:
                image = cv2.imread(image_path)
                if image is None:
                    continue
                
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                detected_faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(detected_faces) > 0:
                    (x, y, w, h) = detected_faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (100, 100))
                    
                    # เก็บ histogram เป็น feature
                    self.known_faces[student_id] = face_roi.flatten()
                    success_count += 1
                    print(f"✅ เทรนสำเร็จ: {student.get('name')} ({student_id})")
                else:
                    print(f"⚠️ ไม่พบใบหน้า: {student.get('name')}")
            
            except Exception as e:
                print(f"❌ Error: {student.get('name')} - {str(e)}")
        
        if success_count > 0:
            self.save_model()
            print(f"✅ เทรนเสร็จสิ้น! จำนวน {success_count}/{len(students)} คน")
        else:
            print("❌ ไม่มีข้อมูลให้เทรน")
        
        return success_count
    
    def save_model(self):
        """บันทึกโมเดล"""
        os.makedirs('data', exist_ok=True)
        with open(self.labels_path, 'wb') as f:
            pickle.dump(self.known_faces, f)
        print(f"💾 บันทึกโมเดลที่: {self.labels_path}")
    
    def load_model(self):
        """โหลดโมเดล"""
        if os.path.exists(self.labels_path):
            try:
                with open(self.labels_path, 'rb') as f:
                    self.known_faces = pickle.load(f)
                print(f"✅ โหลดโมเดล: {len(self.known_faces)} คน")
            except Exception as e:
                print(f"⚠️ ไม่สามารถโหลดโมเดล: {str(e)}")
    
    def recognize_face(self, image_array):
        """จดจำใบหน้าจากรูปภาพ"""
        try:
            if len(self.known_faces) == 0:
                return []
            
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            results = []
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (100, 100))
                face_features = face_roi.flatten()
                
                # เปรียบเทียบกับใบหน้าที่รู้จัก
                best_match = None
                best_distance = float('inf')
                
                for student_id, known_features in self.known_faces.items():
                    distance = np.linalg.norm(face_features - known_features)
                    if distance < best_distance:
                        best_distance = distance
                        best_match = student_id
                
                # threshold สำหรับการจับคู่
                if best_match and best_distance < 3000:
                    confidence = max(0, 1 - (best_distance / 5000))
                    results.append({
                        'student_id': best_match,
                        'confidence': float(confidence),
                        'location': (x, y, w, h)
                    })
            
            return results
        
        except Exception as e:
            print(f"❌ Error in recognize_face: {str(e)}")
            return []
    
    def recognize_from_base64(self, base64_image):
        """จดจำใบหน้าจาก base64 string"""
        import base64
        from io import BytesIO
        from PIL import Image
        
        try:
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data))
            image_array = np.array(image)
            
            # แปลง RGB เป็น BGR สำหรับ OpenCV
            if len(image_array.shape) == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            return self.recognize_face(image_array)
        
        except Exception as e:
            print(f"❌ Error in recognize_from_base64: {str(e)}")
            return []
    
    @property
    def known_face_ids(self):
        """รายการ student_id ที่เทรนแล้ว"""
        return list(self.known_faces.values())

# สร้าง instance
face_recognition_system = FaceRecognitionSystem()
