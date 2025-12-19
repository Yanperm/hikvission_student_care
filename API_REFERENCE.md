# 🔌 API Reference - Student Care System

## Base URL
```
http://localhost:5000
```

---

## 🔐 Authentication

All API endpoints (except `/login` and `/`) require authentication via session.

### Login
```http
POST /api/login
Content-Type: application/json

{
  "username": "admin@school.com",
  "password": "admin123"
}

Response:
{
  "success": true,
  "redirect": "/admin"
}
```

### Logout
```http
GET /logout

Response: Redirect to /
```

---

## 🏫 Schools API (Super Admin Only)

### Get All Schools
```http
GET /api/schools

Response:
{
  "success": true,
  "schools": [
    {
      "id": 1,
      "school_id": "SCH001",
      "name": "โรงเรียนสาธิต",
      "province": "กรุงเทพฯ",
      "package": "Professional",
      "max_students": 500,
      "expire_date": "2025-12-31",
      "status": "active",
      "features": ["face_recognition", "behavior_tracking", ...]
    }
  ]
}
```

### Create School
```http
POST /api/schools
Content-Type: application/json

{
  "name": "โรงเรียนสาธิต",
  "province": "กรุงเทพฯ",
  "address": "123 ถนนสุขุมวิท",
  "package": "Professional",
  "max_students": 500,
  "expire_date": "2025-12-31",
  "admin_username": "admin@demo.com",
  "admin_password": "demo123"
}

Response:
{
  "success": true,
  "school_id": "SCH001",
  "message": "สร้างโรงเรียนสำเร็จ!"
}
```

### Update School
```http
PUT /api/schools/{school_id}
Content-Type: application/json

{
  "name": "โรงเรียนสาธิต (แก้ไข)",
  "province": "กรุงเทพฯ",
  "address": "456 ถนนสุขุมวิท",
  "package": "Business",
  "max_students": 1000,
  "expire_date": "2026-12-31",
  "status": "active"
}

Response:
{
  "success": true,
  "message": "อัพเดทข้อมูลสำเร็จ!"
}
```

### Delete School
```http
DELETE /api/schools/{school_id}

Response:
{
  "success": true,
  "message": "ลบโรงเรียนสำเร็จ!"
}
```

### Get Stats
```http
GET /api/stats

Response:
{
  "success": true,
  "stats": {
    "total_schools": 5,
    "total_capacity": 2500,
    "expiring_soon": 2
  }
}
```

---

## 👨‍🎓 Students API

### Get All Students
```http
GET /api/students

Response:
{
  "success": true,
  "students": [
    {
      "id": 1,
      "student_id": "1001",
      "name": "สมชาย ใจดี",
      "class_name": "ม.1/1",
      "school_id": "SCH001",
      "image_path": "data/students/1001.jpg",
      "created_at": "2025-01-19T10:30:00"
    }
  ]
}
```

### Add Student
```http
POST /add_student
Content-Type: multipart/form-data

student_id: "1001"
name: "สมชาย ใจดี"
class_name: "ม.1/1"
image_data: "data:image/jpeg;base64,..."

Response:
{
  "success": true,
  "message": "เพิ่มนักเรียน สมชาย ใจดี สำเร็จ"
}
```

### Delete Student
```http
DELETE /delete_student/{student_id}

Response:
{
  "success": true,
  "message": "ลบนักเรียนสำเร็จ"
}
```

### Get Student Detail
```http
GET /api/student/{student_id}

Response:
{
  "success": true,
  "student": {
    "student_id": "1001",
    "name": "สมชาย ใจดี",
    "class_name": "ม.1/1",
    ...
  },
  "attendance": [...],
  "behaviors": [...]
}
```

---

## 📊 Attendance API

### Get Attendance
```http
GET /api/attendance
GET /api/attendance?date=2025-01-19

Response:
{
  "success": true,
  "attendance": [
    {
      "id": 1,
      "student_id": "1001",
      "student_name": "สมชาย ใจดี",
      "school_id": "SCH001",
      "camera_type": "classroom",
      "timestamp": "2025-01-19T08:30:00",
      "status": "present"
    }
  ]
}
```

### Add Attendance
```http
POST /api/attendance
Content-Type: application/json

{
  "student_id": "1001",
  "student_name": "สมชาย ใจดี",
  "camera_type": "classroom"
}

Response:
{
  "success": true,
  "message": "บันทึกการเข้าเรียนสำเร็จ"
}
```

### Manual Check-in
```http
POST /manual_checkin
Content-Type: application/json

{
  "student_id": "1001",
  "camera_type": "general"
}

Response:
{
  "success": true,
  "message": "เช็คชื่อสำเร็จ"
}
```

### Face Recognition Check-in
```http
POST /recognize_face
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,...",
  "camera_type": "classroom"
}

Response:
{
  "success": true,
  "student_id": "1001",
  "student_name": "สมชาย ใจดี",
  "class_name": "ม.1/1",
  "camera_type": "classroom"
}
```

---

## 👁️ Behavior API

### Get Behavior
```http
GET /api/behavior
GET /api/behavior?student_id=1001

Response:
{
  "success": true,
  "behaviors": [
    {
      "id": 1,
      "student_id": "1001",
      "student_name": "สมชาย ใจดี",
      "school_id": "SCH001",
      "behavior": "ช่วยเหลือเพื่อน",
      "severity": "normal",
      "timestamp": "2025-01-19T10:00:00"
    }
  ]
}
```

### Add Behavior
```http
POST /api/behavior
Content-Type: application/json

{
  "student_id": "1001",
  "student_name": "สมชาย ใจดี",
  "behavior": "ช่วยเหลือเพื่อน",
  "severity": "normal"
}

Response:
{
  "success": true,
  "message": "บันทึกพฤติกรรมสำเร็จ"
}
```

### Get Behavior Scores
```http
GET /api/behavior_scores
GET /api/behavior_scores?month=2025-01

Response:
{
  "success": true,
  "scores": [
    {
      "id": 1,
      "student_id": "1001",
      "school_id": "SCH001",
      "score": 95,
      "month": "2025-01",
      "updated_at": "2025-01-19T10:00:00"
    }
  ]
}
```

### Update Behavior Score
```http
POST /api/behavior_scores/update
Content-Type: application/json

{
  "student_id": "1001",
  "score": 95,
  "month": "2025-01"
}

Response:
{
  "success": true,
  "message": "อัพเดทคะแนนความประพฤติสำเร็จ"
}
```

---

## 🔔 Notifications API

### Get Notifications
```http
GET /api/notifications

Response:
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "school_id": "SCH001",
      "student_id": "1001",
      "type": "attendance",
      "title": "ขาดเรียน",
      "message": "นักเรียนขาดเรียน 3 วันติดต่อกัน",
      "timestamp": "2025-01-19T10:00:00",
      "read": 0
    }
  ]
}
```

### Mark as Read
```http
POST /api/notifications/mark_read/{notification_id}

Response:
{
  "success": true,
  "message": "ทำเครื่องหมายอ่านแล้ว"
}
```

---

## 📈 Analytics API

### Dashboard Stats
```http
GET /api/dashboard_stats

Response:
{
  "success": true,
  "stats": {
    "total_students": 150,
    "today_attendance": 142,
    "attendance_rate": 94.7,
    "behavior_alerts": 3,
    "unread_notifications": 5
  }
}
```

### Learning Analytics Prediction
```http
POST /api/learning_analytics/predict
Content-Type: application/json

{
  "student_id": "1001"
}

Response:
{
  "success": true,
  "prediction": {
    "attendance_rate": 95.5,
    "behavior_score": 90,
    "learning_prediction": "ดีมาก",
    "recommendations": [
      "การเข้าเรียนดีมาก",
      "พฤติกรรมดีเยี่ยม"
    ]
  }
}
```

### Real-time Status
```http
GET /api/realtime/status

Response:
{
  "success": true,
  "realtime": {
    "recent_attendance": [...],
    "alerts": [...],
    "timestamp": "2025-01-19T10:30:00"
  }
}
```

---

## 💚 Mental Health & Safety API

### Mental Health Check
```http
POST /api/mental_health/check
Content-Type: application/json

{
  "student_id": "1001",
  "student_name": "สมชาย ใจดี",
  "mood": "happy",
  "notes": "รู้สึกดีมาก"
}

Response:
{
  "success": true,
  "message": "บันทึกข้อมูลสุขภาพจิตสำเร็จ"
}
```

### Anti-Bullying Report
```http
POST /api/anti_bullying/report
Content-Type: application/json

{
  "victim_id": "1001",
  "victim_name": "สมชาย ใจดี",
  "description": "ถูกเพื่อนแกล้ง",
  "location": "ห้องเรียน",
  "witness": "ครูประจำชั้น"
}

Response:
{
  "success": true,
  "message": "รายงานถูกส่งไปยังครูที่ปรึกษาแล้ว"
}
```

---

## 📄 Reports API

### Export Report
```http
POST /api/export_report
Content-Type: application/json

{
  "type": "attendance",
  "format": "pdf",
  "date_from": "2025-01-01",
  "date_to": "2025-01-31"
}

Response:
{
  "success": true,
  "message": "ส่งออกรายงาน attendance เป็น pdf สำเร็จ",
  "records_count": 150
}
```

---

## 🔄 Cloud Sync API

### Sync All Students
```http
POST /sync_all_students

Response:
{
  "success": true,
  "message": "Sync 150/150 students"
}
```

---

## 📊 Error Responses

### Unauthorized
```json
{
  "success": false,
  "message": "กรุณา Login ก่อน"
}
```

### Not Found
```json
{
  "success": false,
  "message": "ไม่พบข้อมูล"
}
```

### Validation Error
```json
{
  "success": false,
  "message": "กรุณากรอกข้อมูลให้ครบถ้วน"
}
```

### Server Error
```json
{
  "success": false,
  "message": "เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง"
}
```

---

## 🔑 Severity Levels

### Behavior Severity
- `normal` - พฤติกรรมปกติ/ดี
- `info` - ข้อมูลทั่วไป
- `warning` - ต้องติดตาม
- `danger` - ต้องดำเนินการด่วน

### Notification Types
- `attendance` - การเข้าเรียน
- `behavior` - พฤติกรรม
- `mental_health` - สุขภาพจิต
- `bullying` - การกลั่นแกล้ง
- `test` - ทดสอบระบบ

---

## 📦 Packages

### Starter (ฟรี)
- นักเรียน: 100 คน
- ฟีเจอร์: 5 ฟีเจอร์พื้นฐาน

### Professional (฿2,999/เดือน)
- นักเรียน: 500 คน
- ฟีเจอร์: 15 ฟีเจอร์

### Business (฿5,999/เดือน)
- นักเรียน: 1,000 คน
- ฟีเจอร์: 20 ฟีเจอร์

### Enterprise (ติดต่อ)
- นักเรียน: ไม่จำกัด
- ฟีเจอร์: ทั้งหมด 21 ฟีเจอร์

---

## 🛠️ Development

### Database
```python
from database import db

# Get connection
conn = db.get_connection()
cursor = conn.cursor()

# Query
cursor.execute('SELECT * FROM students')
students = cursor.fetchall()

# Close
conn.close()
```

### Session
```python
from flask import session

# Get current user
username = session.get('user')
role = session.get('role')
school_id = session.get('school_id')
```

---

© 2025 SOFTUBON CO.,LTD.
