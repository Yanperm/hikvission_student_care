# 🚀 คำแนะนำ Deploy ไปยัง AWS EC2

## 📋 ข้อมูล Server

- **IP Address:** `43.210.87.220`
- **Port:** `8080`
- **OS:** Ubuntu 20.04/22.04
- **User:** `ubuntu`

## 🔑 Step 1: เชื่อมต่อ EC2

```bash
ssh -i your-key.pem ubuntu@43.210.87.220
```

## 📥 Step 2: Deploy (วิธีที่ 1 - Automatic)

```bash
# Download and run deploy script
curl -o deploy.sh https://raw.githubusercontent.com/Yanperm/hikvission_student_care/main/deploy_to_ec2.sh
chmod +x deploy.sh
./deploy.sh
```

## 📥 Step 2: Deploy (วิธีที่ 2 - Manual)

### 2.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2.2 Install Dependencies
```bash
sudo apt install -y python3 python3-pip python3-venv git
```

### 2.3 Clone Repository
```bash
cd ~
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care
```

### 2.4 Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 2.5 Create Data Directory
```bash
mkdir -p data/students
```

### 2.6 Test Run
```bash
python3 local_app.py
# Press Ctrl+C to stop
```

### 2.7 Setup Systemd Service
```bash
sudo nano /etc/systemd/system/student-care.service
```

Paste:
```ini
[Unit]
Description=Student Care System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/hikvission_student_care
Environment="PATH=/home/ubuntu/hikvission_student_care/venv/bin"
ExecStart=/home/ubuntu/hikvission_student_care/venv/bin/gunicorn -w 4 -b 0.0.0.0:8080 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

### 2.8 Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable student-care
sudo systemctl start student-care
sudo systemctl status student-care
```

### 2.9 Configure Firewall
```bash
sudo ufw allow 8080/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

## ✅ Step 3: Verify Deployment

### 3.1 Check Service Status
```bash
sudo systemctl status student-care
```

### 3.2 Check Logs
```bash
sudo journalctl -u student-care -f
```

### 3.3 Test Access
```bash
curl http://localhost:8080
```

### 3.4 Access from Browser
```
http://43.210.87.220:8080
```

## 👥 Step 4: Setup Parent-Student Relations

```bash
cd ~/hikvission_student_care
source venv/bin/activate
python add_parent_relation.py
```

Edit the file to add relations:
```python
add_relation('parent@school.com', 'STD001', 'parent')
add_relation('parent@school.com', 'STD002', 'parent')
```

## 🔄 Update Deployment

```bash
cd ~/hikvission_student_care
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart student-care
```

Or use quick script:
```bash
./deploy_quick.sh
```

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u student-care -n 50

# Check if port is in use
sudo lsof -i :8080

# Kill process if needed
sudo kill -9 $(sudo lsof -t -i:8080)
```

### Permission denied
```bash
sudo chown -R ubuntu:ubuntu ~/hikvission_student_care
chmod +x deploy_quick.sh
```

### Database issues
```bash
cd ~/hikvission_student_care
rm -rf data/database.db
python3 -c "from database import db; print('Database initialized')"
```

## 📊 Monitoring

### View Logs (Real-time)
```bash
sudo journalctl -u student-care -f
```

### Check Resource Usage
```bash
htop
```

### Check Disk Space
```bash
df -h
```

## 🔐 Security

### Change Default Passwords
```bash
cd ~/hikvission_student_care
python3
```

```python
from database import db
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("UPDATE users SET password='NewPassword123' WHERE username='superadmin@softubon.com'")
conn.commit()
conn.close()
```

### Enable Firewall
```bash
sudo ufw status
sudo ufw enable
```

## 🎯 Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Super Admin | superadmin@softubon.com | Softubon@2025 |
| Admin | admin@school.com | admin123 |
| Teacher | teacher@school.com | teacher123 |
| Parent | parent@school.com | parent123 |

## 📞 Support

**SOFTUBON CO.,LTD.**
- GitHub: https://github.com/Yanperm/hikvission_student_care
- Email: support@softubon.com

---

© 2025 SOFTUBON CO.,LTD. All rights reserved.
