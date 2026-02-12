"""
LINE OA Notification System
ระบบแจ้งเตือนผู้ปกครองผ่าน LINE Official Account
"""

import requests
import os
from datetime import datetime

class LineNotificationSystem:
    def __init__(self):
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
        self.api_url = 'https://api.line.me/v2/bot/message/push'
    
    def send_gate_notification(self, line_user_id, student_name, entry_type, time):
        """
        ส่งการแจ้งเตือนเข้า-ออกโรงเรียน
        
        Args:
            line_user_id: LINE User ID ของผู้ปกครอง
            student_name: ชื่อนักเรียน
            entry_type: 'checkin' หรือ 'checkout'
            time: เวลา
        """
        if not self.channel_access_token or not line_user_id:
            print("⚠️ ไม่มี LINE Token หรือ User ID")
            return False
        
        try:
            # สร้างข้อความ
            if entry_type == 'checkin':
                emoji = '🟢'
                title = 'บุตรของท่านมาถึงโรงเรียนแล้ว'
                message = f'{student_name} เข้าโรงเรียนเวลา {time}'
            else:
                emoji = '🟠'
                title = 'บุตรของท่านออกจากโรงเรียนแล้ว'
                message = f'{student_name} ออกจากโรงเรียนเวลา {time}'
            
            # Flex Message สำหรับ LINE
            flex_message = {
                "type": "flex",
                "altText": f"{emoji} {title}",
                "contents": {
                    "type": "bubble",
                    "hero": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": emoji,
                                "size": "xxl",
                                "align": "center"
                            }
                        ],
                        "backgroundColor": "#667eea" if entry_type == 'checkin' else "#f59e0b",
                        "paddingAll": "20px"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": title,
                                "weight": "bold",
                                "size": "lg",
                                "wrap": True
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "lg",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "spacing": "sm",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "นักเรียน",
                                                "color": "#aaaaaa",
                                                "size": "sm",
                                                "flex": 2
                                            },
                                            {
                                                "type": "text",
                                                "text": student_name,
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 5
                                            }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "spacing": "sm",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "เวลา",
                                                "color": "#aaaaaa",
                                                "size": "sm",
                                                "flex": 2
                                            },
                                            {
                                                "type": "text",
                                                "text": time,
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 5
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Student Care System",
                                "color": "#aaaaaa",
                                "size": "xs",
                                "align": "center"
                            }
                        ]
                    }
                }
            }
            
            # ส่งข้อความ
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.channel_access_token}'
            }
            
            payload = {
                'to': line_user_id,
                'messages': [flex_message]
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                print(f"✅ ส่ง LINE แจ้งเตือนสำเร็จ: {student_name}")
                return True
            else:
                print(f"❌ ส่ง LINE ไม่สำเร็จ: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ Error sending LINE: {str(e)}")
            return False
    
    def send_absent_notification(self, line_user_id, student_name, date):
        """แจ้งเตือนการขาดเรียน"""
        if not self.channel_access_token or not line_user_id:
            return False
        
        try:
            message = {
                "type": "text",
                "text": f"⚠️ แจ้งเตือนการขาดเรียน\n\n{student_name} ไม่มาโรงเรียนวันที่ {date}\n\nหากมีเหตุจำเป็น กรุณาติดต่อครูที่ปรึกษา"
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.channel_access_token}'
            }
            
            payload = {
                'to': line_user_id,
                'messages': [message]
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            return response.status_code == 200
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

# สร้าง instance
line_notification = LineNotificationSystem()
