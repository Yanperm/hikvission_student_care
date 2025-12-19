# LINE Notify Integration
# © 2025 SOFTUBON CO.,LTD.

import requests

class LineNotify:
    def __init__(self):
        self.api_url = 'https://notify-api.line.me/api/notify'
    
    def send_message(self, token, message):
        """
        ส่งข้อความผ่าน LINE Notify
        
        Args:
            token: LINE Notify Token ของผู้ปกครอง
            message: ข้อความที่ต้องการส่ง
        """
        if not token:
            return False
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        data = {
            'message': message
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"LINE Notify Error: {e}")
            return False
    
    def send_gate_entry(self, token, student_name, entry_type, time):
        """
        แจ้งเตือนเข้า-ออกโรงเรียน
        """
        if entry_type == 'checkin':
            message = f"""
🟢 บุตรของท่านมาถึงโรงเรียนแล้ว

👤 ชื่อ: {student_name}
⏰ เวลา: {time}
📍 สถานที่: ประตูโรงเรียน

ขอบคุณที่ส่งบุตรมาโรงเรียนตรงเวลา
"""
        else:
            message = f"""
🟠 บุตรของท่านออกจากโรงเรียนแล้ว

👤 ชื่อ: {student_name}
⏰ เวลา: {time}
📍 สถานที่: ประตูโรงเรียน

กรุณารับบุตรด้วยความปลอดภัย
"""
        
        return self.send_message(token, message)
    
    def send_attendance_alert(self, token, student_name, date):
        """
        แจ้งเตือนขาดเรียน
        """
        message = f"""
⚠️ แจ้งเตือนการขาดเรียน

👤 ชื่อ: {student_name}
📅 วันที่: {date}

บุตรของท่านไม่มีการเช็คชื่อเข้าเรียนวันนี้
กรุณาติดต่อโรงเรียนหากมีข้อสงสัย
"""
        return self.send_message(token, message)
    
    def send_behavior_alert(self, token, student_name, behavior, severity):
        """
        แจ้งเตือนพฤติกรรม
        """
        icon = '⚠️' if severity == 'warning' else '🚨' if severity == 'danger' else 'ℹ️'
        
        message = f"""
{icon} แจ้งเตือนพฤติกรรม

👤 ชื่อ: {student_name}
📝 พฤติกรรม: {behavior}
⏰ เวลา: {datetime.now().strftime('%H:%M น.')}

กรุณาติดตามพฤติกรรมของบุตร
"""
        return self.send_message(token, message)

# Initialize
line_notify = LineNotify()
