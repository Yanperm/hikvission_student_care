"""
Export Manager - PDF and Excel Export
สำหรับ Export รายงานเป็น PDF และ Excel
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
from io import BytesIO
from datetime import datetime

class ExportManager:
    def __init__(self):
        # ลงทะเบียนฟอนต์ไทย (ถ้ามี)
        try:
            pdfmetrics.registerFont(TTFont('THSarabunNew', 'THSarabunNew.ttf'))
            self.thai_font = 'THSarabunNew'
        except:
            self.thai_font = 'Helvetica'
    
    def export_attendance_pdf(self, attendance_data, school_name="โรงเรียน"):
        """Export รายงานการเข้าเรียนเป็น PDF"""
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont(self.thai_font, 20)
        p.drawString(2*cm, height - 2*cm, f"รายงานการเข้าเรียน - {school_name}")
        
        p.setFont(self.thai_font, 12)
        p.drawString(2*cm, height - 3*cm, f"วันที่: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Table Header
        y = height - 5*cm
        p.setFont(self.thai_font, 14)
        p.drawString(2*cm, y, "รหัสนักเรียน")
        p.drawString(6*cm, y, "ชื่อ-นามสกุล")
        p.drawString(12*cm, y, "เวลา")
        p.drawString(16*cm, y, "ประเภท")
        
        # Draw line
        p.line(2*cm, y - 0.3*cm, width - 2*cm, y - 0.3*cm)
        
        # Data
        y -= 1*cm
        p.setFont(self.thai_font, 12)
        
        for i, record in enumerate(attendance_data[:30]):  # จำกัด 30 รายการต่อหน้า
            if y < 3*cm:  # ถ้าใกล้ท้ายหน้า
                p.showPage()  # ขึ้นหน้าใหม่
                y = height - 3*cm
            
            p.drawString(2*cm, y, str(record.get('student_id', '-')))
            p.drawString(6*cm, y, str(record.get('student_name', '-'))[:20])
            
            timestamp = record.get('timestamp', '')
            if timestamp:
                time_str = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
                p.drawString(12*cm, y, time_str[:5])
            
            camera_type = record.get('camera_type', 'general')
            type_map = {
                'gate_in': 'เข้าโรงเรียน',
                'gate_out': 'ออกโรงเรียน',
                'classroom': 'ห้องเรียน',
                'general': 'ทั่วไป'
            }
            p.drawString(16*cm, y, type_map.get(camera_type, camera_type))
            
            y -= 0.8*cm
        
        # Footer
        p.setFont(self.thai_font, 10)
        p.drawString(2*cm, 2*cm, f"จำนวนทั้งหมด: {len(attendance_data)} รายการ")
        p.drawString(2*cm, 1.5*cm, "สร้างโดย Student Care System")
        
        p.save()
        buffer.seek(0)
        return buffer
    
    def export_attendance_excel(self, attendance_data):
        """Export รายงานการเข้าเรียนเป็น Excel"""
        # แปลงเป็น DataFrame
        df = pd.DataFrame(attendance_data)
        
        # เลือกเฉพาะคอลัมน์ที่ต้องการ
        columns = ['student_id', 'student_name', 'timestamp', 'camera_type']
        df = df[[col for col in columns if col in df.columns]]
        
        # เปลี่ยนชื่อคอลัมน์เป็นภาษาไทย
        df.columns = ['รหัสนักเรียน', 'ชื่อ-นามสกุล', 'เวลา', 'ประเภท']
        
        # แปลงประเภทกล้อง
        type_map = {
            'gate_in': 'เข้าโรงเรียน',
            'gate_out': 'ออกโรงเรียน',
            'classroom': 'ห้องเรียน',
            'general': 'ทั่วไป'
        }
        if 'ประเภท' in df.columns:
            df['ประเภท'] = df['ประเภท'].map(lambda x: type_map.get(x, x))
        
        # สร้าง Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='การเข้าเรียน', index=False)
            
            # ปรับความกว้างคอลัมน์
            worksheet = writer.sheets['การเข้าเรียน']
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 30
            worksheet.column_dimensions['C'].width = 20
            worksheet.column_dimensions['D'].width = 15
        
        buffer.seek(0)
        return buffer
    
    def export_behavior_pdf(self, behavior_data, school_name="โรงเรียน"):
        """Export รายงานพฤติกรรมเป็น PDF"""
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont(self.thai_font, 20)
        p.drawString(2*cm, height - 2*cm, f"รายงานพฤติกรรม - {school_name}")
        
        p.setFont(self.thai_font, 12)
        p.drawString(2*cm, height - 3*cm, f"วันที่: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Table Header
        y = height - 5*cm
        p.setFont(self.thai_font, 14)
        p.drawString(2*cm, y, "รหัส")
        p.drawString(5*cm, y, "ชื่อ")
        p.drawString(10*cm, y, "พฤติกรรม")
        p.drawString(16*cm, y, "ระดับ")
        
        p.line(2*cm, y - 0.3*cm, width - 2*cm, y - 0.3*cm)
        
        # Data
        y -= 1*cm
        p.setFont(self.thai_font, 12)
        
        for record in behavior_data[:30]:
            if y < 3*cm:
                p.showPage()
                y = height - 3*cm
            
            p.drawString(2*cm, y, str(record.get('student_id', '-'))[:8])
            p.drawString(5*cm, y, str(record.get('student_name', '-'))[:15])
            p.drawString(10*cm, y, str(record.get('behavior', '-'))[:20])
            
            severity = record.get('severity', 'normal')
            severity_map = {
                'normal': 'ปกติ',
                'info': 'ข้อมูล',
                'warning': 'เตือน',
                'danger': 'อันตราย'
            }
            p.drawString(16*cm, y, severity_map.get(severity, severity))
            
            y -= 0.8*cm
        
        # Footer
        p.setFont(self.thai_font, 10)
        p.drawString(2*cm, 2*cm, f"จำนวนทั้งหมด: {len(behavior_data)} รายการ")
        p.drawString(2*cm, 1.5*cm, "สร้างโดย Student Care System")
        
        p.save()
        buffer.seek(0)
        return buffer
    
    def export_behavior_excel(self, behavior_data):
        """Export รายงานพฤติกรรมเป็น Excel"""
        df = pd.DataFrame(behavior_data)
        
        columns = ['student_id', 'student_name', 'behavior', 'severity', 'timestamp']
        df = df[[col for col in columns if col in df.columns]]
        
        df.columns = ['รหัสนักเรียน', 'ชื่อ-นามสกุล', 'พฤติกรรม', 'ระดับ', 'เวลา']
        
        # แปลงระดับความรุนแรง
        severity_map = {
            'normal': 'ปกติ',
            'info': 'ข้อมูล',
            'warning': 'เตือน',
            'danger': 'อันตราย'
        }
        if 'ระดับ' in df.columns:
            df['ระดับ'] = df['ระดับ'].map(lambda x: severity_map.get(x, x))
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='พฤติกรรม', index=False)
            
            worksheet = writer.sheets['พฤติกรรม']
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 30
            worksheet.column_dimensions['C'].width = 40
            worksheet.column_dimensions['D'].width = 12
            worksheet.column_dimensions['E'].width = 20
        
        buffer.seek(0)
        return buffer
    
    def export_summary_pdf(self, stats, school_name="โรงเรียน"):
        """Export รายงานสรุปเป็น PDF"""
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont(self.thai_font, 24)
        p.drawString(2*cm, height - 2*cm, f"รายงานสรุป - {school_name}")
        
        p.setFont(self.thai_font, 12)
        p.drawString(2*cm, height - 3*cm, f"วันที่: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Stats
        y = height - 5*cm
        p.setFont(self.thai_font, 16)
        
        p.drawString(2*cm, y, f"👥 นักเรียนทั้งหมด: {stats.get('total_students', 0)} คน")
        y -= 1.5*cm
        
        p.drawString(2*cm, y, f"✅ เข้าเรียนวันนี้: {stats.get('today_attendance', 0)} คน")
        y -= 1.5*cm
        
        p.drawString(2*cm, y, f"📊 เปอร์เซ็นต์การเข้าเรียน: {stats.get('attendance_rate', 0)}%")
        y -= 1.5*cm
        
        p.drawString(2*cm, y, f"⚠️ พฤติกรรมที่ต้องติดตาม: {stats.get('behavior_alerts', 0)} รายการ")
        y -= 1.5*cm
        
        p.drawString(2*cm, y, f"🔔 การแจ้งเตือนที่ยังไม่อ่าน: {stats.get('unread_notifications', 0)} รายการ")
        
        # Footer
        p.setFont(self.thai_font, 10)
        p.drawString(2*cm, 2*cm, "สร้างโดย Student Care System")
        p.drawString(2*cm, 1.5*cm, "© 2025 SOFTUBON CO.,LTD.")
        
        p.save()
        buffer.seek(0)
        return buffer

# สร้าง instance
export_manager = ExportManager()
