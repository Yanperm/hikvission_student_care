"""
Hikvision Face Recognition API Integration
เชื่อมต่อกับกล้อง Hikvision เพื่อใช้ Face Recognition ของกล้องโดยตรง
ความแม่นยำ 99%+
"""

import requests
from requests.auth import HTTPDigestAuth
import base64
import json
from datetime import datetime
import xml.etree.ElementTree as ET

class HikvisionFaceAPI:
    def __init__(self, ip, username='admin', password='admin', port=80):
        """
        เชื่อมต่อกล้อง Hikvision
        
        Args:
            ip: IP Address ของกล้อง (เช่น 192.168.1.64)
            username: Username (default: admin)
            password: Password
            port: Port (default: 80)
        """
        self.ip = ip
        self.port = port
        self.auth = HTTPDigestAuth(username, password)
        self.base_url = f"http://{ip}:{port}/ISAPI"
        self.timeout = 10
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ"""
        try:
            url = f"{self.base_url}/System/deviceInfo"
            response = requests.get(url, auth=self.auth, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Connection Error: {str(e)}")
            return False
    
    def add_face(self, student_id, name, image_path):
        """
        เพิ่มใบหน้าเข้า Face Library ของกล้อง
        
        Args:
            student_id: รหัสนักเรียน
            name: ชื่อนักเรียน
            image_path: path ของรูปภาพ
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # อ่านรูปภาพและแปลงเป็น base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # สร้าง XML สำหรับ Hikvision API
            url = f"{self.base_url}/Intelligent/FDLib/FaceDataRecord"
            
            xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<FaceDataRecord>
    <id>{student_id}</id>
    <name>{name}</name>
    <faceLibType>blackFD</faceLibType>
    <bornTime>{datetime.now().strftime('%Y-%m-%d')}</bornTime>
</FaceDataRecord>"""
            
            headers = {'Content-Type': 'application/xml'}
            response = requests.post(url, data=xml_data, auth=self.auth, headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 201]:
                # อัพโหลดรูปภาพ
                face_url = f"{self.base_url}/Intelligent/FDLib/FaceDataRecord/picture/{student_id}"
                files = {'file': ('face.jpg', image_data, 'image/jpeg')}
                pic_response = requests.put(face_url, files=files, auth=self.auth, timeout=self.timeout)
                
                if pic_response.status_code in [200, 201]:
                    return {'success': True, 'message': f'เพิ่มใบหน้า {name} สำเร็จ'}
                else:
                    return {'success': False, 'message': f'อัพโหลดรูปไม่สำเร็จ: {pic_response.status_code}'}
            else:
                return {'success': False, 'message': f'เพิ่มข้อมูลไม่สำเร็จ: {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def delete_face(self, student_id):
        """ลบใบหน้าออกจาก Face Library"""
        try:
            url = f"{self.base_url}/Intelligent/FDLib/FaceDataRecord/{student_id}"
            response = requests.delete(url, auth=self.auth, timeout=self.timeout)
            
            if response.status_code in [200, 204]:
                return {'success': True, 'message': f'ลบใบหน้า {student_id} สำเร็จ'}
            else:
                return {'success': False, 'message': f'ลบไม่สำเร็จ: {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def get_face_list(self):
        """ดึงรายการใบหน้าทั้งหมดในกล้อง"""
        try:
            url = f"{self.base_url}/Intelligent/FDLib/FaceDataRecord"
            response = requests.get(url, auth=self.auth, timeout=self.timeout)
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.content)
                faces = []
                for record in root.findall('.//FaceDataRecord'):
                    face_id = record.find('id').text if record.find('id') is not None else None
                    name = record.find('name').text if record.find('name') is not None else None
                    if face_id and name:
                        faces.append({'id': face_id, 'name': name})
                return {'success': True, 'faces': faces}
            else:
                return {'success': False, 'message': f'ดึงข้อมูลไม่สำเร็จ: {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def get_face_detection_events(self, callback=None):
        """
        รับ Event การจับใบหน้าแบบ Real-time
        
        Args:
            callback: ฟังก์ชันที่จะถูกเรียกเมื่อจับใบหน้าได้
                      callback(student_id, name, confidence, timestamp)
        """
        try:
            url = f"{self.base_url}/Event/notification/alertStream"
            response = requests.get(url, auth=self.auth, stream=True, timeout=None)
            
            print("🎥 เริ่มรับ Event จากกล้อง...")
            
            buffer = b""
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    buffer += chunk
                    
                    # หา boundary ของ event
                    if b'</EventNotificationAlert>' in buffer:
                        try:
                            # Parse XML
                            xml_str = buffer.decode('utf-8', errors='ignore')
                            start = xml_str.find('<?xml')
                            end = xml_str.find('</EventNotificationAlert>') + len('</EventNotificationAlert>')
                            
                            if start >= 0 and end > start:
                                event_xml = xml_str[start:end]
                                root = ET.fromstring(event_xml)
                                
                                # ดึงข้อมูลจาก Event
                                event_type = root.find('.//eventType')
                                if event_type is not None and 'faceDetection' in event_type.text:
                                    student_id = root.find('.//TargetID')
                                    name = root.find('.//name')
                                    similarity = root.find('.//similarity')
                                    timestamp = root.find('.//dateTime')
                                    
                                    if student_id is not None and name is not None:
                                        result = {
                                            'student_id': student_id.text,
                                            'name': name.text,
                                            'confidence': float(similarity.text) / 100 if similarity is not None else 0.0,
                                            'timestamp': timestamp.text if timestamp is not None else datetime.now().isoformat()
                                        }
                                        
                                        print(f"✅ จับใบหน้า: {result['name']} ({result['confidence']*100:.1f}%)")
                                        
                                        if callback:
                                            callback(result)
                                
                                buffer = buffer[buffer.find(b'</EventNotificationAlert>') + len(b'</EventNotificationAlert>'):]
                        
                        except Exception as e:
                            print(f"⚠️ Parse Error: {str(e)}")
                            buffer = b""
        
        except Exception as e:
            print(f"❌ Event Stream Error: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def get_rtsp_url(self, channel=1, stream=1):
        """
        สร้าง RTSP URL สำหรับดึง Video Stream
        
        Args:
            channel: Channel ของกล้อง (default: 1)
            stream: Stream type (1=Main, 2=Sub)
        
        Returns:
            str: RTSP URL
        """
        username = self.auth.username
        password = self.auth.password
        return f"rtsp://{username}:{password}@{self.ip}:554/Streaming/Channels/{channel}0{stream}"
    
    def sync_all_students(self, students):
        """
        Sync นักเรียนทั้งหมดเข้ากล้อง
        
        Args:
            students: list of dict [{'student_id': '', 'name': '', 'image_path': ''}]
        
        Returns:
            dict: {'success': int, 'failed': int, 'total': int}
        """
        success = 0
        failed = 0
        
        print(f"🔄 เริ่ม Sync {len(students)} คน...")
        
        for student in students:
            result = self.add_face(
                student['student_id'],
                student['name'],
                student['image_path']
            )
            
            if result['success']:
                success += 1
                print(f"✅ {student['name']}")
            else:
                failed += 1
                print(f"❌ {student['name']}: {result['message']}")
        
        print(f"\n📊 สรุป: สำเร็จ {success}/{len(students)} คน")
        
        return {
            'success': success,
            'failed': failed,
            'total': len(students)
        }

# สร้าง instance
hikvision_api = None

def init_hikvision(ip, username='admin', password='admin'):
    """เริ่มต้นการเชื่อมต่อกล้อง Hikvision"""
    global hikvision_api
    hikvision_api = HikvisionFaceAPI(ip, username, password)
    return hikvision_api
