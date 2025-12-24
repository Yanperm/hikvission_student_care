"""
Two-Factor Authentication (2FA)
ใช้ TOTP (Time-based One-Time Password)
"""

import pyotp
import qrcode
from io import BytesIO
import base64

class TwoFactorAuth:
    def __init__(self):
        self.issuer_name = "Student Care System"
    
    def generate_secret(self):
        """สร้าง secret key สำหรับ 2FA"""
        return pyotp.random_base32()
    
    def get_totp_uri(self, username, secret):
        """สร้าง URI สำหรับ Google Authenticator"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=username,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code(self, username, secret):
        """สร้าง QR Code สำหรับ Google Authenticator"""
        uri = self.get_totp_uri(username, secret)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    def generate_qr_base64(self, username, secret):
        """สร้าง QR Code เป็น base64"""
        buffer = self.generate_qr_code(username, secret)
        img_base64 = base64.b64encode(buffer.read()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    def verify_token(self, secret, token):
        """ตรวจสอบ OTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def get_current_token(self, secret):
        """ดึง token ปัจจุบัน (สำหรับทดสอบ)"""
        totp = pyotp.TOTP(secret)
        return totp.now()

# สร้าง instance
two_fa = TwoFactorAuth()
