import cv2
import requests
from requests.auth import HTTPDigestAuth
import numpy as np

class HikvisionCamera:
    def __init__(self, ip, username, password, port=80):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.rtsp_url = f"rtsp://{username}:{password}@{ip}:554/Streaming/Channels/101"
        self.cap = None
        
    def connect(self):
        """เชื่อมต่อกล้อง Hikvision"""
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            if self.cap.isOpened():
                print(f"เชื่อมต่อกล้อง {self.ip} สำเร็จ")
                return True
            else:
                print(f"ไม่สามารถเชื่อมต่อกล้อง {self.ip}")
                return False
        except Exception as e:
            print(f"ข้อผิดพลาด: {e}")
            return False
    
    def get_frame(self):
        """อ่านเฟรมจากกล้อง"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
    
    def disconnect(self):
        """ตัดการเชื่อมต่อ"""
        if self.cap:
            self.cap.release()
            print("ตัดการเชื่อมต่อกล้องแล้ว")
    
    def capture_snapshot(self):
        """ถ่ายภาพจากกล้อง"""
        try:
            url = f"http://{self.ip}:{self.port}/ISAPI/Streaming/channels/101/picture"
            response = requests.get(url, auth=HTTPDigestAuth(self.username, self.password), timeout=10)
            
            if response.status_code == 200:
                nparr = np.frombuffer(response.content, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return img
            else:
                print(f"ไม่สามารถถ่ายภาพได้ Status: {response.status_code}")
                return None
        except Exception as e:
            print(f"ข้อผิดพลาดในการถ่ายภาพ: {e}")
            return None