"""
Notification Manager
- Email (SMTP)
- SMS (Twilio)
- LINE OA
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class NotificationManager:
    def __init__(self):
        # Email Config
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@studentcare.com')
        
        # SMS Config (Twilio)
        self.twilio_sid = os.getenv('TWILIO_SID', '')
        self.twilio_token = os.getenv('TWILIO_TOKEN', '')
        self.twilio_phone = os.getenv('TWILIO_PHONE', '')
    
    def send_email(self, to_email, subject, body, html=True):
        """ส่ง Email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
    
    def send_sms(self, to_phone, message):
        """ส่ง SMS ผ่าน Twilio"""
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_sid, self.twilio_token)
            
            message = client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to_phone
            )
            
            print(f"✅ SMS sent to {to_phone}")
            return True
        except Exception as e:
            print(f"❌ SMS error: {e}")
            return False
    
    def send_parent_notification(self, student_name, event_type, details, email=None, phone=None):
        """แจ้งเตือนผู้ปกครอง"""
        
        # Email Template
        if email:
            subject = f"แจ้งเตือน: {student_name}"
            body = f"""
            <html>
            <body style="font-family: 'IBM Plex Sans Thai', sans-serif;">
                <h2>🎓 Student Care System</h2>
                <h3>{event_type}</h3>
                <p><strong>นักเรียน:</strong> {student_name}</p>
                <p><strong>รายละเอียด:</strong> {details}</p>
                <p><strong>เวลา:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M น.')}</p>
                <hr>
                <p style="color: #666;">ระบบดูแลนักเรียนอัจฉริยะ</p>
            </body>
            </html>
            """
            self.send_email(email, subject, body)
        
        # SMS
        if phone:
            sms_text = f"Student Care: {event_type}\n{student_name}\n{details}"
            self.send_sms(phone, sms_text)
    
    def send_attendance_alert(self, student_name, status, parent_email=None, parent_phone=None):
        """แจ้งเตือนการเข้าเรียน"""
        if status == 'checkin':
            event = "🟢 เข้าโรงเรียน"
            details = f"{student_name} เข้าโรงเรียนเรียบร้อยแล้ว"
        else:
            event = "🟠 ออกจากโรงเรียน"
            details = f"{student_name} ออกจากโรงเรียนแล้ว"
        
        self.send_parent_notification(student_name, event, details, parent_email, parent_phone)
    
    def send_behavior_alert(self, student_name, behavior, severity, parent_email=None, parent_phone=None):
        """แจ้งเตือนพฤติกรรม"""
        severity_map = {
            'danger': '🚨 ด่วน',
            'warning': '⚠️ เตือน',
            'info': 'ℹ️ แจ้งเพื่อทราบ'
        }
        
        event = f"{severity_map.get(severity, '')} พฤติกรรม"
        details = behavior
        
        self.send_parent_notification(student_name, event, details, parent_email, parent_phone)

# สร้าง instance
notifier = NotificationManager()
