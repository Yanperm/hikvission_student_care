import cv2
import face_recognition
import numpy as np
import os
import pickle
from datetime import datetime

class FaceRecognitionSystem:
    def __init__(self, students_data_path="data/students"):
        self.students_data_path = students_data_path
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_student_faces()
        
    def load_student_faces(self):
        """โหลดข้อมูลใบหน้านักเรียนจากโฟลเดอร์"""
        self.known_face_encodings = []
        self.known_face_names = []
        
        if not os.path.exists(self.students_data_path):
            os.makedirs(self.students_data_path)
            return
            
        for filename in os.listdir(self.students_data_path):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                student_id = os.path.splitext(filename)[0]
                image_path = os.path.join(self.students_data_path, filename)
                
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(student_id)
                    print(f"โหลดข้อมูลนักเรียน: {student_id}")
    
    def add_student(self, student_id, image_path):
        """เพิ่มนักเรียนใหม่"""
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                # บันทึกรูปภาพ
                new_path = os.path.join(self.students_data_path, f"{student_id}.jpg")
                cv2.imwrite(new_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                
                # เพิ่มเข้าระบบ
                self.known_face_encodings.append(encodings[0])
                self.known_face_names.append(student_id)
                return True
            return False
        except Exception as e:
            print(f"ข้อผิดพลาดในการเพิ่มนักเรียน: {e}")
            return False
    
    def recognize_faces(self, frame):
        """ตรวจจับและจดจำใบหน้า"""
        # ลดขนาดภาพเพื่อเพิ่มความเร็ว
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        
        # หาตำแหน่งใบหน้า
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognized_students = []
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                name = self.known_face_names[best_match_index]
                recognized_students.append(name)
        
        # ขยายตำแหน่งกลับเป็นขนาดเดิม
        face_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations]
        
        return face_locations, recognized_students
    
    def draw_faces(self, frame, face_locations, names):
        """วาดกรอบและชื่อบนใบหน้า"""
        for (top, right, bottom, left), name in zip(face_locations, names):
            # วาดกรอบ
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # วาดชื่อ
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
        
        return frame