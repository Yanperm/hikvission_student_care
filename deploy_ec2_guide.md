# 🚀 Deploy to AWS EC2 Guide

## ข้อมูล Server
- **IP:** 43.210.87.220
- **Port:** 8080 (หรือ 80/443)
- **Domain:** http://43.210.87.220:8080

---

## 📋 ขั้นตอนการ Deploy

### 1. เชื่อมต่อ EC2
```bash
ssh -i your-key.pem ubuntu@43.210.87.220
```

### 2. ติดตั้ง Dependencies
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# ติดตั้ง Python 3 และ pip
sudo apt install python3 python3-pip python3-venv -y

# ติดตั้ง Nginx (สำหรับ Reverse Proxy)
sudo apt install nginx -y

# ติดตั้ง Supervisor (สำหรับรัน App ตลอดเวลา)
sudo apt install supervisor -y
```

### 3. Upload โปรเจค
```bash
# บนเครื่อง Local
scp -i your-key.pem -r d:/Hikvission ubuntu@43.210.87.220:~/student-care

# หรือใช้ Git
ssh ubuntu@43.210.87.220
cd ~
git clone https://github.com/Yanperm/hikvission_student_care.git student-care
cd student-care
```

### 4. ติดตั้ง Python Packages
```bash
cd ~/student-care
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. ตั้งค่า Environment Variables
```bash
nano .env
```

เพิ่ม:
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
LINE_CHANNEL_ACCESS_TOKEN=9DsRhDEo5isJbuDHhysjmiLJmA55Gg9c49QxhxcTgno6uxd3VMYO+qv20zanztetA0i67fxzA93KYWFQIzZK+hI8yIv9TYczCN+4VorJiTo+Am+sE5eRfFrl8738DlJgpocP1ayhrChOX0lh3qSEmVGUYhWQfeY8sLGRXgo3xvw=
```

### 6. ตั้งค่า Gunicorn (Production Server)
```bash
pip install gunicorn
```

สร้างไฟล์ `wsgi.py`:
```python
from local_app import app

if __name__ == "__main__":
    app.run()
```

### 7. ตั้งค่า Supervisor
```bash
sudo nano /etc/supervisor/conf.d/student-care.conf
```

เพิ่ม:
```ini
[program:student-care]
directory=/home/ubuntu/student-care
command=/home/ubuntu/student-care/venv/bin/gunicorn -w 4 -b 0.0.0.0:8080 wsgi:app
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/student-care.err.log
stdout_logfile=/var/log/student-care.out.log
```

รีโหลด Supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start student-care
sudo supervisorctl status
```

### 8. ตั้งค่า Nginx (Optional - สำหรับ HTTPS)
```bash
sudo nano /etc/nginx/sites-available/student-care
```

เพิ่ม:
```nginx
server {
    listen 80;
    server_name 43.210.87.220;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/student-care /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. เปิด Firewall
```bash
sudo ufw allow 8080
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 10. ตั้งค่า LINE Webhook
ไปที่ LINE Developers Console:
- Webhook URL: `http://43.210.87.220:8080/webhook/line`
- เปิด "Use webhook"
- Verify

---

## 🔄 คำสั่งที่ใช้บ่อย

### ดู Log
```bash
sudo tail -f /var/log/student-care.out.log
sudo tail -f /var/log/student-care.err.log
```

### รีสตาร์ท App
```bash
sudo supervisorctl restart student-care
```

### อัพเดทโค้ด
```bash
cd ~/student-care
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart student-care
```

### ตรวจสอบสถานะ
```bash
sudo supervisorctl status
sudo systemctl status nginx
```

---

## 🔒 Security (สำคัญ!)

### 1. ตั้งค่า HTTPS (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

### 2. เปลี่ยน Secret Key
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. ตั้งค่า Database Backup
```bash
# สร้าง cron job
crontab -e

# เพิ่ม (backup ทุกวันเวลา 2:00)
0 2 * * * cd ~/student-care && tar -czf backup-$(date +\%Y\%m\%d).tar.gz data/
```

---

## ✅ ทดสอบ

1. เปิดเบราว์เซอร์: `http://43.210.87.220:8080`
2. ทดสอบ Webhook: ส่งข้อความไปที่ LINE OA
3. ตรวจสอบ Log: `sudo tail -f /var/log/student-care.out.log`

---

## 🆘 แก้ไขปัญหา

### App ไม่ทำงาน
```bash
sudo supervisorctl status
sudo supervisorctl restart student-care
sudo tail -f /var/log/student-care.err.log
```

### Webhook ไม่ทำงาน
- ตรวจสอบ Firewall: `sudo ufw status`
- ตรวจสอบ Log: `sudo tail -f /var/log/student-care.out.log`
- ทดสอบ: `curl http://43.210.87.220:8080/webhook/line`

### Database Error
```bash
cd ~/student-care
source venv/bin/activate
python3 -c "from database import db; print('Database OK')"
```

---

© 2025 SOFTUBON CO.,LTD.
