import cv2
import numpy as np
import os
import json
import sqlite3
from datetime import datetime

class StudentCheckInSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        self.students_data = {}
        self.face_labels = []
        self.face_images = []
        self.is_trained = False
        self.last_recognition = {}
        
        # สร้างโฟลเดอร์
        os.makedirs("data/students", exist_ok=True)
        os.makedirs("data/faces", exist_ok=True)
        
        # โหลดข้อมูล
        self.load_students()
        self.init_database()
        
        if len(self.students_data) > 0:
            self.train_recognizer()
    
    def init_database(self):
        """สร้างฐานข้อมูล"""
        conn = sqlite3.connect('data/attendance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                student_name TEXT,
                check_in_time TEXT,
                date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_student(self, student_id, name, num_samples=30):
        """เพิ่มนักเรียนใหม่โดยการถ่ายรูป"""
        print(f"Adding student: {name}")
        print("Look at the camera and press SPACE to capture faces")
        print("Press ESC when done")
        
        cap = cv2.VideoCapture(0)
        sample_count = 0
        face_samples = []
        
        while sample_count < num_samples:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # แสดงข้อมูล
                cv2.putText(frame, f"Samples: {sample_count}/{num_samples}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Student: {name}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Press SPACE to capture", 
                           (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Add Student - Face Capture', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE
                if len(faces) > 0:
                    x, y, w, h = faces[0]  # ใช้ใบหน้าแรกที่พบ
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (100, 100))  # ปรับขนาดให้เท่ากัน
                    
                    face_samples.append(face_roi)
                    sample_count += 1
                    print(f"Captured sample {sample_count}")
                else:
                    print("No face detected!")
            
            elif key == 27:  # ESC
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if len(face_samples) > 0:
            # บันทึกข้อมูลนักเรียน
            label = len(self.students_data)
            self.students_data[label] = {
                'student_id': student_id,
                'name': name,
                'samples': len(face_samples)
            }
            
            # เพิ่มข้อมูลสำหรับการฝึก
            for face_sample in face_samples:
                self.face_images.append(face_sample)
                self.face_labels.append(label)
            
            # บันทึกข้อมูล
            self.save_students()
            self.train_recognizer()
            
            print(f"Successfully added {name} with {len(face_samples)} samples")
            return True
        else:
            print("No samples captured!")
            return False
    
    def save_students(self):
        """บันทึกข้อมูลนักเรียน"""
        with open('data/students_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.students_data, f, ensure_ascii=False, indent=2)
        
        # บันทึกรูปใบหน้า
        np.save('data/face_images.npy', np.array(self.face_images))
        np.save('data/face_labels.npy', np.array(self.face_labels))
    
    def load_students(self):
        """โหลดข้อมูลนักเรียน"""
        try:
            if os.path.exists('data/students_data.json'):
                with open('data/students_data.json', 'r', encoding='utf-8') as f:
                    self.students_data = json.load(f)
                
                # แปลง key เป็น int
                self.students_data = {int(k): v for k, v in self.students_data.items()}
            
            if os.path.exists('data/face_images.npy') and os.path.exists('data/face_labels.npy'):
                self.face_images = np.load('data/face_images.npy').tolist()
                self.face_labels = np.load('data/face_labels.npy').tolist()
            
            print(f"Loaded {len(self.students_data)} students")
            
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def train_recognizer(self):
        """ฝึกตัวจดจำใบหน้า"""
        if len(self.face_images) > 0 and len(self.face_labels) > 0:
            print("Training face recognizer...")
            self.face_recognizer.train(self.face_images, np.array(self.face_labels))
            self.is_trained = True
            print("Training completed!")
        else:
            print("No training data available")
    
    def check_in_student(self, label):
        """เช็คอินนักเรียน"""
        if label not in self.students_data:
            return False
        
        current_time = datetime.now()
        today = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")
        
        student_name = self.students_data[label]['name']
        
        # ป้องกันการเช็คอินซ้ำ (ภายใน 30 วินาที)
        if label in self.last_recognition:
            time_diff = (current_time - self.last_recognition[label]).seconds
            if time_diff < 30:
                return False
        
        self.last_recognition[label] = current_time
        
        # บันทึกลงฐานข้อมูล
        conn = sqlite3.connect('data/attendance.db')
        cursor = conn.cursor()
        
        student_id = self.students_data[label]['student_id']
        
        cursor.execute('''
            INSERT INTO attendance (student_id, student_name, check_in_time, date)
            VALUES (?, ?, ?, ?)
        ''', (student_id, student_name, time_str, today))
        
        conn.commit()
        conn.close()
        
        print(f"✅ {student_name} checked in at {time_str}")
        return True
    
    def get_today_attendance(self):
        """ดูรายการเช็คอินวันนี้"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect('data/attendance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT student_id, student_name, check_in_time 
            FROM attendance 
            WHERE date = ?
            ORDER BY check_in_time
        ''', (today,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def run_recognition(self):
        """รันระบบจดจำใบหน้า"""
        if not self.is_trained:
            print("No trained model available. Please add students first.")
            return
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Cannot open camera")
            return
        
        print("Face Recognition System Started")
        print("Press 'q' to quit, 's' to show attendance")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (100, 100))
                
                # จดจำใบหน้า
                label, confidence = self.face_recognizer.predict(face_roi)
                
                # ตั้งค่า threshold สำหรับการจดจำ
                if confidence < 100:  # ยิ่งน้อยยิ่งแม่นยำ
                    if label in self.students_data:
                        name = self.students_data[label]['name']
                        student_id = self.students_data[label]['student_id']
                        
                        # เช็คอินอัตโนมัติ
                        self.check_in_student(label)
                        
                        # แสดงข้อมูล
                        color = (0, 255, 0)  # เขียว
                        display_text = f"{name} ({student_id})"
                        conf_text = f"Conf: {confidence:.1f}"
                    else:
                        color = (0, 165, 255)  # ส้ม
                        display_text = f"ID: {label}"
                        conf_text = f"Conf: {confidence:.1f}"
                else:
                    color = (0, 0, 255)  # แดง
                    display_text = "Unknown"
                    conf_text = f"Conf: {confidence:.1f}"
                
                # วาดกรอบและข้อความ
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.rectangle(frame, (x, y-40), (x+w, y), color, -1)
                
                cv2.putText(frame, display_text, (x+5, y-25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, conf_text, (x+5, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # แสดงข้อมูลระบบ
            cv2.putText(frame, f"Students: {len(self.students_data)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # แสดงเวลา
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, current_time, (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Student Check-in System', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.show_attendance()
        
        cap.release()
        cv2.destroyAllWindows()
    
    def show_attendance(self):
        """แสดงรายการเช็คอินวันนี้"""
        attendance = self.get_today_attendance()
        today = datetime.now().strftime("%Y-%m-%d")
        
        print(f"\n=== Attendance Report {today} ===")
        if attendance:
            for student_id, name, time in attendance:
                print(f"{time} - {name} ({student_id})")
        else:
            print("No check-ins today")
        print("=" * 40)

def main():
    system = StudentCheckInSystem()
    
    while True:
        print("\n=== Student Check-in System ===")
        print("1. Add Student")
        print("2. Start Recognition")
        print("3. Show Today's Attendance")
        print("4. Exit")
        
        choice = input("Select option: ")
        
        if choice == '1':
            student_id = input("Student ID: ")
            name = input("Student Name: ")
            system.add_student(student_id, name)
            
        elif choice == '2':
            system.run_recognition()
            
        elif choice == '3':
            system.show_attendance()
            
        elif choice == '4':
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()