"""
Student Import System
ระบบนำเข้าข้อมูลนักเรียนแบบครบวงจร
"""

import pandas as pd
import os
import shutil
from datetime import datetime
import zipfile

class StudentImportSystem:
    def __init__(self, db):
        self.db = db
    
    def import_from_excel(self, excel_file, school_id):
        """
        นำเข้าข้อมูลจาก Excel
        
        คอลัมน์ที่ต้องมี:
        - student_id: รหัสนักเรียน (บังคับ)
        - name: ชื่อ-นามสกุล (บังคับ)
        - class_name: ห้องเรียน
        - parent_name: ชื่อผู้ปกครอง
        - parent_phone: เบอร์โทรผู้ปกครอง
        - parent_line_id: LINE ID ผู้ปกครอง
        - image_filename: ชื่อไฟล์รูปภาพ (ถ้ามี)
        """
        try:
            # อ่าน Excel
            df = pd.read_excel(excel_file)
            
            # ตรวจสอบคอลัมน์ที่จำเป็น
            required_columns = ['student_id', 'name']
            for col in required_columns:
                if col not in df.columns:
                    return {
                        'success': False,
                        'message': f'ไม่พบคอลัมน์ {col} ในไฟล์ Excel'
                    }
            
            # นำเข้าข้อมูล
            imported = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    student_id = str(row['student_id']).strip()
                    name = str(row['name']).strip()
                    
                    if not student_id or not name:
                        errors.append(f"แถว {index+2}: ข้อมูลไม่ครบ")
                        continue
                    
                    # เตรียมข้อมูล
                    class_name = str(row.get('class_name', '')).strip()
                    parent_name = str(row.get('parent_name', '')).strip()
                    parent_phone = str(row.get('parent_phone', '')).strip()
                    parent_line_id = str(row.get('parent_line_id', '')).strip()
                    
                    # เพิ่มนักเรียน
                    self.db.add_student(
                        student_id=student_id,
                        name=name,
                        class_name=class_name,
                        school_id=school_id,
                        image_path=None
                    )
                    
                    # เพิ่มข้อมูลผู้ปกครอง (ถ้ามี)
                    if parent_line_id:
                        self.db.update_student_line_token(student_id, parent_line_id)
                    
                    imported += 1
                
                except Exception as e:
                    errors.append(f"แถว {index+2}: {str(e)}")
            
            return {
                'success': True,
                'imported': imported,
                'total': len(df),
                'errors': errors,
                'message': f'นำเข้าสำเร็จ {imported}/{len(df)} คน'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาด: {str(e)}'
            }
    
    def import_with_images(self, excel_file, images_zip, school_id):
        """
        นำเข้าข้อมูลพร้อมรูปภาพ
        
        Args:
            excel_file: ไฟล์ Excel ข้อมูลนักเรียน
            images_zip: ไฟล์ ZIP ที่มีรูปภาพ (ชื่อไฟล์ = student_id.jpg)
            school_id: รหัสโรงเรียน
        """
        try:
            # แตกไฟล์ ZIP
            temp_dir = 'data/temp_images'
            os.makedirs(temp_dir, exist_ok=True)
            
            with zipfile.ZipFile(images_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # นำเข้าข้อมูลจาก Excel
            result = self.import_from_excel(excel_file, school_id)
            
            if not result['success']:
                return result
            
            # จับคู่รูปภาพกับนักเรียน
            students = self.db.get_students(school_id)
            matched = 0
            
            for student in students:
                student_id = student['student_id']
                
                # หารูปภาพ
                possible_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
                image_found = False
                
                for ext in possible_extensions:
                    temp_image = os.path.join(temp_dir, f"{student_id}{ext}")
                    
                    if os.path.exists(temp_image):
                        # ย้ายรูปไปที่ data/students
                        final_path = f"data/students/{student_id}.jpg"
                        os.makedirs('data/students', exist_ok=True)
                        shutil.copy(temp_image, final_path)
                        
                        # อัพเดท database
                        self.db.update_student(
                            student_id=student_id,
                            name=student['name'],
                            class_name=student.get('class_name', ''),
                            school_id=school_id,
                            image_path=final_path
                        )
                        
                        matched += 1
                        image_found = True
                        break
                
                if not image_found:
                    print(f"⚠️ ไม่พบรูปภาพ: {student_id}")
            
            # ลบไฟล์ชั่วคราว
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            result['images_matched'] = matched
            result['message'] += f' | จับคู่รูปภาพ {matched} คน'
            
            return result
        
        except Exception as e:
            return {
                'success': False,
                'message': f'เกิดข้อผิดพลาด: {str(e)}'
            }
    
    def create_template_excel(self):
        """สร้าง Template Excel สำหรับนำเข้าข้อมูล"""
        template_data = {
            'student_id': ['STD001', 'STD002', 'STD003'],
            'name': ['สมชาย ใจดี', 'สมหญิง รักเรียน', 'สมศักดิ์ ขยัน'],
            'class_name': ['ม.1/1', 'ม.1/1', 'ม.1/2'],
            'parent_name': ['นายสมชาติ ใจดี', 'นางสมใจ รักเรียน', 'นายสมหมาย ขยัน'],
            'parent_phone': ['081-234-5678', '082-345-6789', '083-456-7890'],
            'parent_line_id': ['', '', ''],
            'image_filename': ['STD001.jpg', 'STD002.jpg', 'STD003.jpg']
        }
        
        df = pd.DataFrame(template_data)
        
        from io import BytesIO
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        return output

# สร้าง instance จะทำใน local_app.py
