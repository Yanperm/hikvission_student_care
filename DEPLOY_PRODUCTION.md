# 🚀 Production Deployment Guide

## 📋 ขั้นตอนการ Deploy

### 1. เตรียม RDS Database

```bash
# สร้าง RDS MySQL บน AWS
# - Engine: MySQL 8.0
# - Instance: db.t3.micro (Free Tier)
# - Storage: 20GB
# - Public Access: Yes (สำหรับทดสอบ)
# - Security Group: เปิด Port 3306
```

### 2. ตั้งค่า Environment Variables

**คัดลอกไฟล์:**
```bash
cp .env.production .env
```

**แก้ไขค่าใน `.env`:**
```bash
USE_RDS=true
DB_HOST=your-actual-rds-endpoint.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=YourActualPassword
DB_NAME=studentcare
```

### 3. ติดตั้ง Dependencies

```bash
pip install python-dotenv
pip install -r requirements.txt
```

### 4. สร้างตาราง Database

```bash
# ระบบจะสร้างตารางอัตโนมัติเมื่อรันครั้งแรก
python local_app.py
```

### 5. Deploy บน EC2

**Option 1: Manual Deploy**
```bash
# SSH เข้า EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Clone โปรเจค
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

# ติดตั้ง
pip install -r requirements.txt

# สร้างไฟล์ .env
nano .env
# (วางค่า Production)

# รันด้วย Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 local_app:app
```

**Option 2: Docker Deploy**
```bash
# Build
docker build -t studentcare .

# Run
docker run -d -p 5000:5000 --env-file .env studentcare
```

### 6. ตั้งค่า Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 7. ตั้งค่า SSL (HTTPS)

```bash
# ติดตั้ง Certbot
sudo apt install certbot python3-certbot-nginx

# สร้าง SSL Certificate
sudo certbot --nginx -d your-domain.com
```

## 🔄 การเปลี่ยนจาก SQLite เป็น RDS

### ก่อน Deploy (Local - SQLite)
```
USE_RDS=false
```
- ข้อมูลอยู่ที่: `data/database.db`
- เหมาะสำหรับ: ทดสอบ, Demo

### หลัง Deploy (Production - RDS)
```
USE_RDS=true
DB_HOST=xxx.rds.amazonaws.com
```
- ข้อมูลอยู่ที่: AWS RDS
- เหมาะสำหรับ: Production, หลายเครื่อง

## 📊 ตรวจสอบการเชื่อมต่อ RDS

```python
# test_rds.py
import os
from dotenv import load_dotenv
load_dotenv()

if os.environ.get('USE_RDS') == 'true':
    from database_rds import db
    print("✅ ใช้ RDS")
    print(f"Host: {os.environ.get('DB_HOST')}")
else:
    from database import db
    print("✅ ใช้ SQLite")
```

## 🔒 Security Checklist

- [ ] เปลี่ยน SECRET_KEY
- [ ] ตั้ง DEBUG=False
- [ ] ใช้รหัสผ่าน RDS ที่แข็งแรง
- [ ] เปิด HTTPS
- [ ] ตั้งค่า Security Group ให้ถูกต้อง
- [ ] อย่า commit `.env` ลง Git
- [ ] ใช้ IAM Role แทน Access Key (ถ้าทำได้)

## 📝 Environment Variables ที่จำเป็น

### Required (ต้องมี)
```
USE_RDS=true
DB_HOST=xxx
DB_USER=xxx
DB_PASSWORD=xxx
DB_NAME=studentcare
SECRET_KEY=xxx
```

### Optional (ไม่บังคับ)
```
LINE_CHANNEL_ACCESS_TOKEN=xxx
SMTP_USER=xxx
SMS_API_KEY=xxx
```

## 🆘 Troubleshooting

### ไม่สามารถเชื่อมต่อ RDS
```bash
# ทดสอบการเชื่อมต่อ
mysql -h your-rds-endpoint.rds.amazonaws.com -u admin -p

# ตรวจสอบ Security Group
# - Inbound Rules: Port 3306 เปิดให้ EC2 IP
```

### ข้อมูลไม่ขึ้น
```bash
# ตรวจสอบว่าใช้ RDS จริง
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('USE_RDS'))"

# ควรได้: true
```

## 🔄 Migrate ข้อมูลจาก SQLite ไป RDS

```python
# migrate.py
import sqlite3
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# อ่านจาก SQLite
sqlite_conn = sqlite3.connect('data/database.db')
sqlite_conn.row_factory = sqlite3.Row

# เชื่อมต่อ RDS
rds_conn = pymysql.connect(
    host=os.environ.get('DB_HOST'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    database=os.environ.get('DB_NAME')
)

# Migrate ข้อมูล
# ... (ทำตามตาราง)
```

---

© 2025 SOFTUBON CO.,LTD. - Student Care System
