"""
Face Recognition System
ระบบจดจำใบหน้าที่แม่นยำสูง
"""

import face_recognition
import numpy as np
import cv2
import os
import pickle
from datetime import datetime

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self.model_path = 'data/face_model.pkl'
        self.load_model()
    
    def train_from_students(self, students):
        """เทรนโมเดลจากข้อมูลนักเรียน"""
        print("🔄 กำลังเทรนโมเดล Face Recognition...")
        
        self.known_face_encodings = []
        self.known_face_ids = []
        
        success_count = 0
        for student in students:
            image_path = student.get('image_path')
            student_id = student.get('student_id')
            
            if not image_path or not os.path.exists(image_path):
                continue
            
            try:
                # โหลดรูป
                image = face_recognition.load_image_file(image_path)
                
                # หา face encoding
                face_encodings = face_recognition.face_encodings(image)
                
                if len(face_encodings) > 0:
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_ids.append(student_id)
                    success_count += 1
                    print(f"✅ เทรนสำเร็จ: {student.get('name')} ({student_id})")
                else:
                    print(f"⚠️ ไม่พบใบหน้า: {student.get('name')}")
            
            except Exception as e:
                print(f"❌ Error: {student.get('name')} - {str(e)}")
        
        # บันทึกโมเดล
        self.save_model()
        print(f"✅ เทรนเสร็จสิ้น! จำนวน {success_count}/{len(students)} คน")
        
        return success_count
    
    def save_model(self):
        """บันทึกโมเดล"""
        os.makedirs('data', exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'encodings': self.known_face_encodings,
                'ids': self.known_face_ids
            }, f)
        print(f"💾 บันทึกโมเดลที่: {self.model_path}")
    
    def load_model(self):
        """โหลดโมเดล"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_ids = data['ids']
                print(f"✅ โหลดโมเดล: {len(self.known_face_ids)} คน")
            except Exception as e:
                print(f"⚠️ ไม่สามารถโหลดโมเดล: {str(e)}")
    
    def recognize_face(self, image_path_or_array):
        """จดจำใบหน้าจากรูปภาพ"""
        try:
            # โหลดรูป
            if isinstance(image_path_or_array, str):
                image = face_recognition.load_image_file(image_path_or_array)
            else:
                image = image_path_or_array
            
            # หา face locations และ encodings
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            results = []
            
            for face_encoding, face_location in zip(face_encodings, face_locations):
                # เปรียบเทียบกับใบหน้าที่รู้จัก
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, 
                    face_encoding,
                    tolerance=0.5  # ยิ่งต่ำยิ่งเข้มงวด (0.4-0.6 แนะนำ)
                )
                
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, 
                    face_encoding
                )
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        student_id = self.known_face_ids[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                        
                        results.append({
                            'student_id': student_id,
                            'confidence': float(confidence),
                            'location': face_location
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
            # แปลง base64 เป็น image
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data))
            image_array = np.array(image)
            
            # แปลง BGR เป็น RGB ถ้าจำเป็น
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            return self.recognize_face(image_array)
        
        except Exception as e:
            print(f"❌ Error in recognize_from_base64: {str(e)}")
            return []

# สร้าง instance
face_recognition_system = FaceRecognitionSystem()
