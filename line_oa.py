# LINE Official Account (OA) Integration
# © 2025 SOFTUBON CO.,LTD.

import requests
import json

class LineOA:
    def __init__(self, channel_access_token=None):
        self.channel_access_token = channel_access_token
        self.api_url = 'https://api.line.me/v2/bot/message/push'
    
    def send_message(self, user_id, message):
        """ส่งข้อความผ่าน LINE OA"""
        if not user_id or not self.channel_access_token:
            print(f"[LINE] ไม่มี user_id หรือ token")
            return False
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.channel_access_token}'
        }
        
        data = {
            'to': user_id,
            'messages': [{'type': 'text', 'text': message}]
        }
        
        try:
            print(f"[LINE] ส่งถึง {user_id[:10]}...")
            response = requests.post(self.api_url, headers=headers, data=json.dumps(data), timeout=10)
            print(f"[LINE] Status: {response.status_code}")
            if response.status_code != 200:
                print(f"[LINE] Error: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"[LINE] Exception: {e}")
            return False
    
    def send_gate_entry(self, user_id, student_name, entry_type, time):
        """แจ้งเตือนเข้า-ออกโรงเรียน"""
        if entry_type == 'checkin':
            icon = '🟢'
            title = 'บุตรของท่านมาถึงโรงเรียนแล้ว'
        else:
            icon = '🟠'
            title = 'บุตรของท่านออกจากโรงเรียนแล้ว'
        
        message = f"""{icon} {title}

👤 ชื่อ: {student_name}
⏰ เวลา: {time}
📍 สถานที่: ประตูโรงเรียน

ขอบคุณที่ไว้วางใจ Student Care System"""
        
        return self.send_message(user_id, message)

    def reply_message(self, reply_token, message):
        """ตอบกลับข้อความ"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.channel_access_token}'
        }
        
        data = {
            'replyToken': reply_token,
            'messages': [{'type': 'text', 'text': message}]
        }
        
        try:
            response = requests.post('https://api.line.me/v2/bot/message/reply', 
                                   headers=headers, data=json.dumps(data))
            return response.status_code == 200
        except Exception as e:
            print(f"LINE Reply Error: {e}")
            return False

line_oa = LineOA()
