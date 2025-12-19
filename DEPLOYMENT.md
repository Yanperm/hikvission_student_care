# 🚀 Production Deployment Guide

## 📋 Pre-Deployment Checklist

- [ ] Python 3.7+ installed
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] SSL certificate ready (for HTTPS)
- [ ] Domain name configured
- [ ] Firewall rules set

## 🔧 Production Setup

### 1. Clone Repository
```bash
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
nano .env  # Edit with your values
```

### 5. Initialize Database
```bash
python -c "import os; os.makedirs('data/students', exist_ok=True)"
```

### 6. Run with Gunicorn (Production)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 local_app:app
```

## 🐳 Docker Deployment (Recommended)

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/students

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "local_app:app"]
```

### Build and Run
```bash
docker build -t student-care .
docker run -d -p 5000:5000 --name student-care-app student-care
```

## ☁️ AWS Deployment

### EC2 Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3-pip python3-venv -y

# Clone and setup
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/student-care.service
```

### Systemd Service File
```ini
[Unit]
Description=Student Care System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/hikvission_student_care
Environment="PATH=/home/ubuntu/hikvission_student_care/venv/bin"
ExecStart=/home/ubuntu/hikvission_student_care/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 local_app:app

[Install]
WantedBy=multi-user.target
```

### Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl start student-care
sudo systemctl enable student-care
sudo systemctl status student-care
```

## 🔒 Nginx Reverse Proxy

### Install Nginx
```bash
sudo apt install nginx -y
```

### Configure Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/hikvission_student_care/static;
    }
}
```

### Enable SSL (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring

### Setup Logs
```bash
mkdir logs
```

### View Logs
```bash
tail -f logs/app.log
sudo journalctl -u student-care -f
```

## 🔐 Security Checklist

- [ ] Change default Super Admin password
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (UFW/Security Groups)
- [ ] Set strong SECRET_KEY
- [ ] Disable DEBUG mode
- [ ] Regular backups configured
- [ ] Update dependencies regularly
- [ ] Monitor logs for suspicious activity

## 💾 Backup Strategy

### Automated Backup Script
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/student-care"
mkdir -p $BACKUP_DIR

# Backup database and files
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz data/

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete
```

### Cron Job (Daily at 2 AM)
```bash
0 2 * * * /path/to/backup.sh
```

## 📈 Performance Optimization

### Gunicorn Workers
```bash
# Formula: (2 x CPU cores) + 1
gunicorn -w 9 -b 0.0.0.0:5000 local_app:app  # For 4 CPU cores
```

### Enable Caching
```python
# Add to local_app.py
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

## 🔄 Update Deployment

```bash
cd hikvission_student_care
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart student-care
```

## 📞 Support

**SOFTUBON CO.,LTD.**
- Email: support@softubon.com
- Phone: 02-xxx-xxxx
- Line: @softubon

---

© 2025 SOFTUBON CO.,LTD. (Student Care System.) All rights reserved.
