# 🚀 Deploy บน AWS EC2

## วิธีที่ 1: SSH + Deploy Script (แนะนำ)

### ขั้นตอน:

```bash
# 1. SSH เข้า EC2
ssh -i your-key.pem ubuntu@43.210.87.220

# 2. รัน deploy script
curl -sSL https://raw.githubusercontent.com/Yanperm/hikvission_student_care/main/deploy_aws_new.sh | bash
```

---

## วิธีที่ 2: Manual Deploy

### 1. SSH เข้า EC2
```bash
ssh -i your-key.pem ubuntu@43.210.87.220
```

### 2. Clone/Update Code
```bash
# ถ้ายังไม่มี
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

# ถ้ามีแล้ว
cd hikvission_student_care
git pull
```

### 3. Setup Environment
```bash
# สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

### 4. สร้าง .env file
```bash
cat > .env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DEBUG=False
PORT=8080
CLOUD_API_URL=http://43.210.87.220:8080
SUPER_ADMIN_USER=admin@softubon.com
SUPER_ADMIN_PASS=Admin@2025
EOF
```

### 5. สร้าง directories
```bash
mkdir -p data/students logs
```

### 6. Stop existing process
```bash
pkill -f "python.*local_app.py" || true
```

### 7. Start application
```bash
nohup python3 local_app.py > logs/app.log 2>&1 &
```

### 8. ตรวจสอบสถานะ
```bash
# ดู process
ps aux | grep local_app.py

# ดู logs
tail -f logs/app.log
```

---

## วิธีที่ 3: Deploy จาก Windows

### ถ้ามี PEM file:

```batch
# รัน
deploy_from_local.bat
```

---

## 🔧 คำสั่งที่มีประโยชน์

### ดู Logs
```bash
tail -f logs/app.log
```

### Restart Application
```bash
pkill -f "python.*local_app.py"
cd hikvission_student_care
source venv/bin/activate
nohup python3 local_app.py > logs/app.log 2>&1 &
```

### ตรวจสอบ Port
```bash
sudo netstat -tulpn | grep 8080
```

### ดู Process
```bash
ps aux | grep python
```

---

## 🌐 เข้าถึงระบบ

- **URL:** http://43.210.87.220:8080
- **Admin:** admin@softubon.com
- **Password:** Admin@2025

---

## 🔒 Security Checklist

- [ ] เปลี่ยน SUPER_ADMIN_PASSWORD
- [ ] ตั้งค่า Security Group (Port 8080)
- [ ] ใช้ HTTPS (ถ้าเป็น Production)
- [ ] Backup database เป็นประจำ
- [ ] Monitor logs

---

## 🆘 แก้ไขปัญหา

### Application ไม่ทำงาน
```bash
# ดู logs
tail -f logs/app.log

# ตรวจสอบ Python
which python3
python3 --version

# ตรวจสอบ dependencies
pip list
```

### Port ถูกใช้งาน
```bash
# หา process ที่ใช้ port 8080
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>
```

### Permission denied
```bash
# แก้ไข permissions
chmod +x deploy_aws_new.sh
chmod -R 755 data/
```

---

© 2025 SOFTUBON CO.,LTD.
