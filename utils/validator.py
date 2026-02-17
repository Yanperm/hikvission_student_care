import re
from flask import jsonify

class Validator:
    @staticmethod
    def validate_student_id(student_id):
        if not student_id or len(student_id) < 3 or len(student_id) > 20:
            return False, 'รหัสนักเรียนต้องมี 3-20 ตัวอักษร'
        if not re.match(r'^[A-Za-z0-9]+$', student_id):
            return False, 'รหัสนักเรียนต้องเป็นตัวอักษรและตัวเลขเท่านั้น'
        return True, None
    
    @staticmethod
    def validate_name(name):
        if not name or len(name) < 2 or len(name) > 100:
            return False, 'ชื่อต้องมี 2-100 ตัวอักษร'
        return True, None
    
    @staticmethod
    def validate_email(email):
        if not email:
            return True, None
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, 'รูปแบบอีเมลไม่ถูกต้อง'
        return True, None
    
    @staticmethod
    def validate_phone(phone):
        if not phone:
            return True, None
        if not re.match(r'^[0-9]{9,10}$', phone):
            return False, 'เบอร์โทรต้องเป็นตัวเลข 9-10 หลัก'
        return True, None
    
    @staticmethod
    def sanitize_input(text):
        if not text:
            return text
        text = text.strip()
        text = re.sub(r'[<>]', '', text)
        return text

validator = Validator()
