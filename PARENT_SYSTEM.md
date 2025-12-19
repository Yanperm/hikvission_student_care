# 👨👩👧 ระบบผู้ปกครอง - คู่มือการใช้งาน

## ✅ ฟีเจอร์ที่พร้อมใช้งาน

### 1. รองรับหลายบุตร
- ผู้ปกครองสามารถดูข้อมูลบุตรหลายคนได้
- คลิกเลือกบุตรแต่ละคนเพื่อดูข้อมูล
- แสดงสถานะการเชื่อมต่อ LINE ของแต่ละคน

### 2. ปุ่ม Logout
- มีปุ่มออกจากระบบที่มุมขวาบน
- ปลอดภัย ป้องกันการเข้าถึงโดยไม่ได้รับอนุญาต

### 3. ข้อมูลจาก Database จริง
- ไม่มี hardcode แล้ว
- ดึงข้อมูลจาก SQLite Database
- Real-time updates

## 🔗 การเชื่อมโยงผู้ปกครอง-นักเรียน

### วิธีที่ 1: ใช้ Python Script
```bash
python add_parent_relation.py
```

แก้ไขโค้ดในไฟล์:
```python
add_relation('parent@school.com', 'STD001', 'parent')
add_relation('parent@school.com', 'STD002', 'parent')  # บุตรคนที่ 2
```

### วิธีที่ 2: ใช้ Python Console
```python
from database import db
db.add_parent_student_relation('parent@school.com', 'STD001', 'parent')
```

### วิธีที่ 3: ใช้ SQL โดยตรง
```sql
INSERT INTO parent_student_relation (parent_username, student_id, relation, created_at)
VALUES ('parent@school.com', 'STD001', 'parent', datetime('now'));
```

## 📊 โครงสร้าง Database

### ตาราง parent_student_relation
```sql
CREATE TABLE parent_student_relation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_username TEXT NOT NULL,
    student_id TEXT NOT NULL,
    relation TEXT,
    created_at TEXT
);
```

### ตัวอย่างข้อมูล
| parent_username | student_id | relation | created_at |
|----------------|------------|----------|------------|
| parent@school.com | STD001 | parent | 2025-01-15 |
| parent@school.com | STD002 | parent | 2025-01-15 |
| parent2@school.com | STD003 | parent | 2025-01-15 |

## 🎯 การใช้งาน

### 1. Login
```
URL: http://localhost:5000/login
Username: parent@school.com
Password: parent123
```

### 2. Dashboard
- แสดงบุตรทั้งหมดที่เชื่อมโยง
- คลิกเลือกบุตรเพื่อดูข้อมูล
- ดูการเข้าเรียน, พฤติกรรม, คะแนน

### 3. LINE OA Integration
- แสดงสถานะการเชื่อมต่อของแต่ละคน
- วิธีเชื่อมต่อ: ส่งรหัสนักเรียนไปที่ LINE OA
- รับการแจ้งเตือนอัตโนมัติ

## 🔐 User Accounts

### ผู้ปกครอง (Parent)
- Username: `parent@school.com`
- Password: `parent123`
- Role: `parent`

### ครู (Teacher)
- Username: `teacher@school.com`
- Password: `teacher123`
- Role: `teacher`

### Admin
- Username: `admin@school.com`
- Password: `admin123`
- Role: `admin`

### Super Admin
- Username: `superadmin@softubon.com`
- Password: `Softubon@2025`
- Role: `super_admin`

## 📱 API Endpoints

### GET /api/student/:student_id
ดึงข้อมูลนักเรียน + การเข้าเรียน + พฤติกรรม

**Response:**
```json
{
  "success": true,
  "student": {...},
  "attendance": [...],
  "behaviors": [...]
}
```

### GET /parent_dashboard
แสดง Dashboard ผู้ปกครอง

**ต้อง Login ก่อน**

## 🚀 Deployment Checklist

- [x] ตาราง parent_student_relation
- [x] ฟังก์ชัน get_parent_students()
- [x] ฟังก์ชัน add_parent_student_relation()
- [x] หน้า parent_dashboard.html (รองรับหลายบุตร)
- [x] ปุ่ม Logout
- [x] ดึงข้อมูลจาก Database จริง
- [x] Push to Git
- [ ] Deploy to Production

## 🐛 Troubleshooting

### ไม่เห็นบุตรใน Dashboard
1. ตรวจสอบว่ามีข้อมูลใน `parent_student_relation`
2. ตรวจสอบ `parent_username` ตรงกับ username ที่ login
3. ตรวจสอบ `student_id` มีอยู่ในตาราง `students`

### ข้อมูลไม่อัพเดท
1. Refresh หน้าเว็บ (F5)
2. Clear Browser Cache
3. ตรวจสอบ Console (F12) หาข้อผิดพลาด

### ไม่สามารถ Logout
1. ตรวจสอบว่ามีปุ่ม Logout ที่มุมขวาบน
2. ตรวจสอบ JavaScript Console
3. ลอง Clear Cookies

## 📞 Support

**SOFTUBON CO.,LTD.**
- GitHub: [Yanperm/hikvission_student_care](https://github.com/Yanperm/hikvission_student_care)
- Email: support@softubon.com

---

© 2025 SOFTUBON CO.,LTD. All rights reserved.
