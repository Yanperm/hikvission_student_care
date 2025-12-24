"""
QR Code Check-in System
สร้างและสแกน QR Code สำหรับเช็คชื่อ
"""

import qrcode
from io import BytesIO
import cv2
from pyzbar.pyzbar import decode
import base64

class QRCodeManager:
    def __init__(self):
        self.prefix = "STUDENTCARE:"
    
    def generate_student_qr(self, student_id, student_name):
        """สร้าง QR Code สำหรับนักเรียน"""
        data = f"{self.prefix}{student_id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    def generate_qr_base64(self, student_id, student_name):
        """สร้าง QR Code เป็น base64"""
        buffer = self.generate_student_qr(student_id, student_name)
        img_base64 = base64.b64encode(buffer.read()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    def scan_qr_from_frame(self, frame):
        """สแกน QR Code จากภาพ"""
        decoded_objects = decode(frame)
        
        results = []
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            
            if data.startswith(self.prefix):
                student_id = data.replace(self.prefix, '')
                results.append({
                    'student_id': student_id,
                    'type': 'qr_code',
                    'location': obj.rect
                })
        
        return results
    
    def scan_qr_from_base64(self, image_data):
        """สแกน QR Code จาก base64"""
        import numpy as np
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return self.scan_qr_from_frame(frame)

# สร้าง instance
qr_manager = QRCodeManager()
