# 🎥 Hikvision Face Recognition API Integration

## ✨ ฟีเจอร์

- ✅ เชื่อมต่อกล้อง Hikvision โดยตรง
- ✅ ใช้ Face Recognition ของกล้อง (ความแม่นยำ 99%+)
- ✅ Real-time Event Notification
- ✅ RTSP Video Stream
- ✅ เพิ่ม/ลบ/ดูรายการใบหน้า
- ✅ Sync นักเรียนทั้งหมดอัตโนมัติ

## 📋 ความต้องการ

### 1. กล้อง Hikvision ที่รองรับ
- รุ่นที่มี Face Recognition (เช่น DS-2CD2x43G0-IWS, DS-K1T671M)
- Firmware version ล่าสุด
- เปิดใช้งาน Face Recognition ในกล้อง

### 2. Python Libraries
```bash
pip install requests
```

### 3. Network
- กล้องและ Server ต้องอยู่ใน Network เดียวกัน (LAN)
- หรือเปิด Port Forward ถ้าต้องการเข้าถึงจากภายนอก

## 🚀 Quick Start

### 1. ตั้งค่ากล้อง

เข้าเว็บกล้อง: `http://192.168.1.64`

**Configuration → Face Recognition:**
- เปิดใช้งาน Face Recognition
- ตั้งค่า Face Library
- เปิด Event Notification

### 2. ใช้งานใน Python

```python
from hikvision_face_api import init_hikvision

# เชื่อมต่อกล้อง
camera = init_hikvision(
    ip='192.168.1.64',
    username='admin',
    password='your_password'
)

# ทดสอบการเชื่อมต่อ
if camera.test_connection():
    print("✅ เชื่อมต่อสำเร็จ!")

# เพิ่มใบหน้า
camera.add_face(
    student_id='STD001',
    name='สมชาย ใจดี',
    image_path='data/students/STD001.jpg'
)

# รับ Event แบบ Real-time
def on_face_detected(result):
    print(f"จับใบหน้า: {result['name']} ({result['confidence']*100:.1f}%)")

camera.get_face_detection_events(callback=on_face_detected)
```

## 🔧 Integration กับระบบปัจจุบัน

### แก้ไข `local_app.py`:

```python
from hikvision_face_api import init_hikvision

# เพิ่มการตั้งค่ากล้อง
CAMERA_IP = os.environ.get('CAMERA_IP', '192.168.1.64')
CAMERA_USER = os.environ.get('CAMERA_USER', 'admin')
CAMERA_PASS = os.environ.get('CAMERA_PASS', 'admin')

# เชื่อมต่อกล้อง
hikvision_camera = init_hikvision(CAMERA_IP, CAMERA_USER, CAMERA_PASS)

# เมื่อเพิ่มนักเรียน → Sync ไปกล้อง
@app.route('/add_student', methods=['POST'])
def add_student():
    # ... บันทึกลง database ...
    
    # Sync ไปกล้อง
    hikvision_camera.add_face(
        student_id=student_id,
        name=name,
        image_path=image_path
    )
    
    return jsonify({'success': True})

# รับ Event จากกล้อง
def handle_face_detection(result):
    # บันทึกการเข้าเรียน
    db.add_attendance(
        result['student_id'],
        result['name'],
        school_id,
        'hikvision_camera'
    )
    
    # ส่งแจ้งเตือน LINE
    line_notification.send_attendance(result['student_id'], result['name'])

# เริ่มรับ Event (รันใน Thread แยก)
import threading
thread = threading.Thread(
    target=hikvision_camera.get_face_detection_events,
    args=(handle_face_detection,)
)
thread.daemon = True
thread.start()
```

## 📊 เปรียบเทียบ

| ฟีเจอร์ | OpenCV (เดิม) | Hikvision API (ใหม่) |
|---------|---------------|----------------------|
| ความแม่นยำ | 60-70% | 99%+ |
| ความเร็ว | ช้า (ประมวลผลเอง) | เร็วมาก (กล้องประมวลผล) |
| Real-time | ไม่มี | มี |
| CPU Usage | สูง | ต่ำ |
| ระยะจับ | 1-2 เมตร | 3-5 เมตร |

## 🔐 Security

### ตั้งค่า Environment Variables:

```bash
# .env
CAMERA_IP=192.168.1.64
CAMERA_USER=admin
CAMERA_PASS=your_secure_password
```

### ใช้ HTTPS (Production):
```python
camera = init_hikvision(
    ip='192.168.1.64',
    username='admin',
    password='password',
    use_https=True  # เพิ่มในอนาคต
)
```

## 🐛 Troubleshooting

### ❌ Connection Error
```
ตรวจสอบ:
1. IP Address ถูกต้องหรือไม่
2. Username/Password ถูกต้องหรือไม่
3. กล้องเปิดอยู่หรือไม่
4. Network เชื่อมต่อได้หรือไม่
```

### ❌ Face Not Detected
```
ตรวจสอบ:
1. เปิดใช้งาน Face Recognition ในกล้องหรือยัง
2. รูปภาพชัดเจนหรือไม่
3. แสงเพียงพอหรือไม่
4. ระยะห่างเหมาะสมหรือไม่ (1-3 เมตร)
```

### ❌ Event Not Received
```
ตรวจสอบ:
1. เปิด Event Notification ในกล้องหรือยัง
2. Network Firewall บล็อคหรือไม่
3. กล้อง Firmware เวอร์ชันล่าสุดหรือไม่
```

## 📚 API Reference

### `init_hikvision(ip, username, password)`
เชื่อมต่อกล้อง Hikvision

### `camera.test_connection()`
ทดสอบการเชื่อมต่อ

### `camera.add_face(student_id, name, image_path)`
เพิ่มใบหน้าเข้ากล้อง

### `camera.delete_face(student_id)`
ลบใบหน้าออกจากกล้อง

### `camera.get_face_list()`
ดูรายการใบหน้าทั้งหมด

### `camera.get_face_detection_events(callback)`
รับ Event การจับใบหน้าแบบ Real-time

### `camera.sync_all_students(students)`
Sync นักเรียนทั้งหมดเข้ากล้อง

### `camera.get_rtsp_url()`
ดึง RTSP URL สำหรับ Video Stream

## 📞 Support

- GitHub: [Yanperm/hikvission_student_care](https://github.com/Yanperm/hikvission_student_care)
- Email: support@softubon.com

---

© 2025 SOFTUBON CO.,LTD. All rights reserved.
