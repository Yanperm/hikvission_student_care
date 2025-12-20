# 🚀 Quick Deployment Guide

## 📋 ขั้นตอนการ Deploy

### 1. Push ไป GitHub

```bash
git add .
git commit -m "Update: Mobile responsive and improvements"
git push origin main
```

### 2. Deploy ไป AWS EC2

**Windows:**
```bash
deploy_aws.bat
```

**Linux/Mac:**
```bash
chmod +x deploy_aws.sh
./deploy_aws.sh
```

## ✅ สิ่งที่ Script จะทำ

1. ✅ Push code ไป GitHub
2. ✅ Connect ไป EC2
3. ✅ หยุดแอปเก่า
4. ✅ Clone code ใหม่จาก GitHub
5. ✅ ติดตั้ง dependencies
6. ✅ สร้าง .env
7. ✅ Setup database
8. ✅ Start แอปด้วย Gunicorn

## 🌐 เข้าถึงแอป

```
http://43.210.87.220:5000
```

## 📝 คำสั่งที่มีประโยชน์

### ดู Logs
```bash
ssh -i studentcare.pem ubuntu@43.210.87.220 "tail -f ~/hikvission_student_care/student-care.log"
```

### Restart แอป
```bash
ssh -i studentcare.pem ubuntu@43.210.87.220 "pkill -f gunicorn && cd ~/hikvission_student_care && nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &"
```

### หยุดแอป
```bash
ssh -i studentcare.pem ubuntu@43.210.87.220 "pkill -f gunicorn"
```

### เข้า SSH
```bash
ssh -i studentcare.pem ubuntu@43.210.87.220
```

## 🔧 Troubleshooting

### ปัญหา: Permission denied (PEM file)
```bash
chmod 400 studentcare.pem
```

### ปัญหา: Port 5000 ถูกใช้งาน
```bash
ssh -i studentcare.pem ubuntu@43.210.87.220
sudo lsof -i :5000
sudo kill -9 <PID>
```

### ปัญหา: แอปไม่ทำงาน
```bash
# ดู logs
ssh -i studentcare.pem ubuntu@43.210.87.220 "tail -50 ~/hikvission_student_care/student-care.log"

# ลองรันแบบ debug
ssh -i studentcare.pem ubuntu@43.210.87.220
cd ~/hikvission_student_care
python3 local_app.py
```

## 📊 ตรวจสอบสถานะ

```bash
# ดูว่าแอปทำงานหรือไม่
ssh -i studentcare.pem ubuntu@43.210.87.220 "ps aux | grep gunicorn"

# ดู CPU/Memory
ssh -i studentcare.pem ubuntu@43.210.87.220 "top -n 1 | head -20"

# ดู Disk Space
ssh -i studentcare.pem ubuntu@43.210.87.220 "df -h"
```

## 🔒 Security Checklist

- [ ] PEM file ไม่ถูก commit ลง GitHub
- [ ] .env ไม่ถูก commit ลง GitHub
- [ ] Security Group เปิด Port 5000
- [ ] ใช้ HTTPS (ถ้าเป็น Production)
- [ ] เปลี่ยน SECRET_KEY
- [ ] Backup database เป็นประจำ

## 🎯 Production Checklist

- [ ] ตั้งค่า Nginx Reverse Proxy
- [ ] ติดตั้ง SSL Certificate (Let's Encrypt)
- [ ] ตั้งค่า Auto-restart (systemd)
- [ ] ตั้งค่า Log Rotation
- [ ] ตั้งค่า Monitoring
- [ ] ตั้งค่า Backup อัตโนมัติ

## 📱 ทดสอบหลัง Deploy

1. เปิด http://43.210.87.220:5000
2. ทดสอบ Login
3. ทดสอบลงทะเบียนนักเรียน
4. ทดสอบกล้อง
5. ทดสอบบนมือถือ

## 🆘 ติดต่อ Support

- GitHub Issues: https://github.com/Yanperm/hikvission_student_care/issues
- Email: support@softubon.com

---

© 2025 SOFTUBON CO.,LTD. - Student Care System
