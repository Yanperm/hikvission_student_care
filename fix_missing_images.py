"""แก้ไขปัญหารูปภาพหาย - สร้างรูป placeholder"""
import os
from PIL import Image, ImageDraw, ImageFont

def create_placeholder(student_id, name):
    """สร้างรูป placeholder สำหรับนักเรียนที่ไม่มีรูป"""
    img = Image.new('RGB', (200, 200), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    
    # วาดข้อความ
    text = f"{name}\n{student_id}"
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((200 - text_width) // 2, (200 - text_height) // 2)
    draw.text(position, text, fill=(100, 100, 100))
    
    # บันทึกไฟล์
    output_path = f'data/students/{student_id}.jpg'
    img.save(output_path)
    print(f'✅ สร้าง placeholder: {output_path}')

if __name__ == '__main__':
    from database_universal import db
    
    students = db.get_students('SCH001')
    
    for student in students:
        student_id = student['student_id']
        name = student['name']
        image_path = f'data/students/{student_id}.jpg'
        
        if not os.path.exists(image_path):
            print(f'⚠️ ไม่พบรูป: {student_id} - {name}')
            create_placeholder(student_id, name)
    
    print('\n✅ เสร็จสิ้น!')
