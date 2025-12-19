# 🎓 Student Care System

ระบบดูแลนักเรียนอัจฉริยะด้วย AI และ Face Recognition

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Cloud](https://img.shields.io/badge/Cloud-AWS-orange.svg)](http://43.210.87.220:8080)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care
```

### 2. ติดตั้ง (เลือก 1 วิธี)

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

**หรือติดตั้งด้วยตนเอง:**
```bash
pip install -r requirements.txt
```

### 3. รันระบบ (เลือก 1 วิธี)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**หรือรันด้วยตนเอง:**
```bash
python local_app.py
```

### 4. เปิดเบราว์เซอร์
```
http://localhost:5000
```

## ✨ ฟีเจอร์ทั้งหมด (21 ฟีเจอร์)

### 🎯 ฟีเจอร์หลัก
- 📸 ลงทะเบียนนักเรียน
- 📚 กล้องในห้องเรียน (เช็คชื่ออัตโนมัติ)
- 👁️ ตรวจจับพฤติกรรม
- ✅ เช็คชื่อด้วยตนเอง
- 📊 Dashboard Admin
- 👤 โปรไฟล์นักเรียน

### 📊 รายงานและวิเคราะห์
- 👨👩👧 Dashboard ผู้ปกครอง
- 📈 รายงานขั้นสูง (กราฟ, Export PDF/Excel)
- 🎓 คะแนนความประพฤติ

### 🤖 AI และเทคโนโลジี
- 🤖 AI Face Recognition (99.6% accuracy)
- 🎯 ตรวจจับอารมณ์
- 📷 กล้องหลายจุด

### 💚 ดูแลนักเรียน
- 💚 ดูแลสุขภาพจิต
- 📚 วิเคราะห์การเรียนรู้ (AI Prediction)
- 🛡️ ป้องกันการกลั่นแกล้ง

### 🔔 การแจ้งเตือน
- 🔔 ระบบแจ้งเตือน Real-time
- 📧 แจ้งเตือนผู้ปกครอง (Email/SMS)
- 🔐 จัดการผู้ใช้หลายระดับ

### 📱 Mobile & Cloud
- 📱 Progressive Web App (PWA)
- ☁️ Cloud Sync (อัตโนมัติ)
- 🔄 Hybrid Architecture

## 🌐 Cloud Sync

ระบบซิงค์ข้อมูลไปยัง AWS Cloud อัตโนมัติ:
- **URL:** `http://43.210.87.220:8080` (Demo Server)
- **ข้อมูลที่ซิงค์:** นักเรียน, การเข้าเรียน, พฤติกรรม
- **ไม่ต้องตั้งค่า:** ทำงานอัตโนมัติ
- **หมายเหตุ:** สำหรับ Production ควรใช้ HTTPS และตั้งค่า Environment Variables

## 📋 ความต้องการของระบบ

- Python 3.7+
- RAM 4GB+ (แนะนำ 8GB+)
- Webcam หรือ Hikvision Camera
- Internet (สำหรับ Cloud Sync)

## 🔒 Security Notice

⚠️ **สำคัญ:** Repository นี้เป็น Demo/Educational Purpose
- ไม่มีข้อมูลส่วนตัวจริง (ใช้ข้อมูลทดสอบ)
- ไม่มี credentials ที่ใช้งานได้จริง
- สำหรับ Production: อ่าน [SECURITY.md](SECURITY.md)
- ต้องสร้างไฟล์ `.env`, `firebase_credentials.json`, `config.json` เอง
- อย่า commit API keys, passwords, หรือข้อมูลลับใดๆ

## 📁 โครงสร้างโปรเจค

```
hikvission_student_care/
├── local_app.py              # แอปพลิเคชันหลัก
├── local_client.py           # Cloud Sync Client
├── requirements.txt          # Dependencies
├── install.bat / install.sh  # Auto Installer
├── start.bat / start.sh      # Quick Start
├── templates/                # 21 HTML Templates
├── static/                   # CSS, JS, PWA
└── data/                     # ข้อมูลนักเรียน (Local)
```

## 🔧 การติดตั้งบนเครื่องอื่น

### วิธีที่ 1: Clone จาก GitHub (แนะนำ)
```bash
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care
./install.sh  # หรือ install.bat
./start.sh    # หรือ start.bat
```

### วิธีที่ 2: Download ZIP
1. Download ZIP จาก GitHub
2. แตกไฟล์
3. รัน `install.bat` (Windows) หรือ `install.sh` (Linux/Mac)
4. รัน `start.bat` หรือ `start.sh`

## 🌐 เข้าถึงจากเครื่องอื่นในเครือข่าย

1. หา IP Address:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. เครื่องอื่นเปิดเบราว์เซอร์:
   ```
   http://[IP-ADDRESS]:5000
   ```

## 📱 ติดตั้ง PWA บนมือถือ

1. เปิดเบราว์เซอร์บนมือถือ
2. ไปที่ `http://[IP]:5000/pwa_mobile`
3. คลิก "เพิ่มไปยังหน้าจอหลัก"
4. ใช้งานแบบ Native App

## 📚 เอกสารเพิ่มเติม

- [INSTALLATION.md](INSTALLATION.md) - คู่มือติดตั้งแบบละเอียด
- [QUICK_START.md](QUICK_START.md) - เริ่มใช้งานด่วน

## 🆘 แก้ไขปัญหา

### ไม่สามารถเชื่อมต่อ Cloud
- ตรวจสอบอินเทอร์เน็ต
- ระบบทำงาน Offline ได้ปกติ
- ข้อมูลจะซิงค์เมื่อกลับมาออนไลน์

### กล้องไม่ทำงาน
- ตรวจสอบสิทธิ์การเข้าถึงกล้อง
- ใช้ HTTPS หรือ localhost
- ลองเปิดเบราว์เซอร์ใหม่

### Port 5000 ถูกใช้งาน
แก้ไขใน `local_app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 📄 License

MIT License

## 📞 ติดต่อ

**SOFTUBON CO.,LTD.**
- GitHub: [Yanperm/hikvission_student_care](https://github.com/Yanperm/hikvission_student_care)
- Email: support@softubon.com

---

© 2025 SOFTUBON CO.,LTD. (Student Care System.) All rights reserved.
