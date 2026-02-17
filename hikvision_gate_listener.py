"""
Hikvision Gate Camera Event Listener
รับ Event การตรวจจับใบหน้าจากกล้อง Hikvision แบบ Real-time
"""

from hikvision_face_api import init_hikvision
from database_universal import db
from local_client import CloudSync
from line_oa import LineOA
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

CLOUD_API_URL = os.environ.get('CLOUD_API_URL', 'http://43.210.87.220:8080')
cloud_sync = CloudSync(CLOUD_API_URL)

def handle_face_detection(result):
    """จัดการเมื่อกล้องตรวจจับใบหน้า"""
    student_id = result['student_id']
    student_name = result['name']
    confidence = result['confidence']
    
    print(f"✅ ตรวจจับ: {student_name} ({confidence*100:.1f}%)")
    
    # บันทึกเข้าฐานข้อมูล
    school_id = 'SCH001'  # ดึงจาก config
    camera_type = 'gate_in'  # หรือ gate_out
    
    db.add_attendance(student_id, student_name, school_id, camera_type)
    
    # แจ้งเตือน LINE
    line_user_id = db.get_student_line_token(student_id)
    if line_user_id:
        school = db.get_school(school_id)
        if school and school.get('line_channel_token'):
            line = LineOA(school['line_channel_token'])
            current_time = datetime.now().strftime('%H:%M น.')
            line.send_gate_entry(line_user_id, student_name, 'checkin', current_time)
    
    # Sync to Cloud
    cloud_sync.send_attendance(student_id, student_name, camera_type=camera_type)

if __name__ == '__main__':
    # อ่าน config จาก database
    school = db.get_school('SCH001')
    
    if not school or not school.get('camera_ip'):
        print("❌ กรุณาตั้งค่ากล้อง Hikvision ก่อน")
        exit(1)
    
    # เชื่อมต่อกล้อง
    camera = init_hikvision(
        school['camera_ip'],
        school.get('camera_user', 'admin'),
        school.get('camera_pass', 'admin')
    )
    
    if not camera.test_connection():
        print("❌ ไม่สามารถเชื่อมต่อกล้องได้")
        exit(1)
    
    print(f"🎥 เชื่อมต่อกล้อง {school['camera_ip']} สำเร็จ")
    print("⏳ รอรับ Event...")
    
    # เริ่มรับ Event
    camera.get_face_detection_events(callback=handle_face_detection)
