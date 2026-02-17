# 🚀 Deployment Guide - Improved System

## 📦 ไฟล์ที่ต้อง Deploy

### Core Files
- ✅ `database_universal.py` - Database with RDS support + pooling
- ✅ `config.py` - Centralized configuration
- ✅ `requirements_rds.txt` - Updated dependencies
- ✅ `.env` - Environment variables (RDS config)

### Security Modules
- ✅ `security/password_manager.py` - Password hashing
- ✅ `security/csrf_protection.py` - CSRF protection
- ✅ `security/rate_limiter.py` - Rate limiting

### Routes (Blueprints)
- ✅ `routes/auth.py` - Authentication routes
- ✅ `routes/students.py` - Student management routes

### Utilities
- ✅ `utils/cache.py` - Caching system
- ✅ `utils/validator.py` - Input validation

### Templates
- ✅ `templates/line_setup.html` - Updated with Webhook URL

---

## 🚀 Quick Deploy

### Windows
```bash
deploy_improvements.bat
```

### Linux/Mac
```bash
chmod +x deploy_improvements.sh
./deploy_improvements.sh
```

---

## 📋 Manual Deployment Steps

### 1. Upload Files
```bash
# Create directories
ssh -i studentcare.pem ubuntu@43.210.87.220 "mkdir -p /home/ubuntu/studentcare/security /home/ubuntu/studentcare/routes /home/ubuntu/studentcare/utils"

# Upload files
scp -i studentcare.pem database_universal.py ubuntu@43.210.87.220:/home/ubuntu/studentcare/
scp -i studentcare.pem config.py ubuntu@43.210.87.220:/home/ubuntu/studentcare/
scp -i studentcare.pem requirements_rds.txt ubuntu@43.210.87.220:/home/ubuntu/studentcare/
scp -i studentcare.pem .env ubuntu@43.210.87.220:/home/ubuntu/studentcare/

# Upload security
scp -i studentcare.pem security/*.py ubuntu@43.210.87.220:/home/ubuntu/studentcare/security/

# Upload routes
scp -i studentcare.pem routes/*.py ubuntu@43.210.87.220:/home/ubuntu/studentcare/routes/

# Upload utils
scp -i studentcare.pem utils/*.py ubuntu@43.210.87.220:/home/ubuntu/studentcare/utils/

# Upload templates
scp -i studentcare.pem templates/line_setup.html ubuntu@43.210.87.220:/home/ubuntu/studentcare/templates/
```

### 2. Install Dependencies
```bash
ssh -i studentcare.pem ubuntu@43.210.87.220
cd /home/ubuntu/studentcare
source venv/bin/activate
pip install -r requirements_rds.txt
```

### 3. Update local_app.py
```bash
# On server
cd /home/ubuntu/studentcare
nano local_app.py

# Replace database import with:
try:
    from database_universal import db
except Exception as e:
    print(f"Database initialization failed: {str(e)}")
    from database import db
```

### 4. Restart Service
```bash
sudo systemctl restart studentcare
sudo systemctl status studentcare
```

---

## 🔍 Verification

### 1. Check Service Status
```bash
ssh -i studentcare.pem ubuntu@43.210.87.220
sudo systemctl status studentcare
```

### 2. Check Logs
```bash
sudo journalctl -u studentcare -f
```

### 3. Test Database Connection
```bash
cd /home/ubuntu/studentcare
source venv/bin/activate
python test_rds.py
```

### 4. Test Application
```bash
curl http://43.210.87.220:8080
```

---

## 🔐 Environment Variables (.env)

ตรวจสอบว่า `.env` บน server มีค่าถูกต้อง:

```env
# Database
DB_TYPE=postgresql
USE_POSTGRES=true
DB_HOST=your-rds-host
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_NAME=postgres
DB_PORT=5432

# Application
SECRET_KEY=production-secret-key-change-this
DEBUG=False
PORT=8080
```

---

## 📊 Post-Deployment Checklist

- [ ] ✅ Files uploaded successfully
- [ ] ✅ Dependencies installed
- [ ] ✅ Database connection working
- [ ] ✅ Service restarted
- [ ] ✅ Application accessible
- [ ] ✅ Login working (password hashing)
- [ ] ✅ LINE OA webhook URL displayed
- [ ] ✅ RDS connection pooling active
- [ ] ✅ No errors in logs

---

## 🔄 Rollback Plan

หากมีปัญหา:

```bash
# 1. Stop service
sudo systemctl stop studentcare

# 2. Restore backup
cd /home/ubuntu/studentcare
cp database.py.backup database.py
cp local_app.py.backup local_app.py

# 3. Restart
sudo systemctl start studentcare
```

---

## 🆘 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u studentcare -n 50

# Check syntax
cd /home/ubuntu/studentcare
source venv/bin/activate
python -m py_compile local_app.py
```

### Database connection failed
```bash
# Test RDS connection
python test_rds.py

# Check .env
cat .env | grep DB_
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements_rds.txt --force-reinstall
```

---

## 📞 Server Info

- **IP**: 43.210.87.220
- **User**: ubuntu
- **Path**: /home/ubuntu/studentcare
- **Service**: studentcare.service
- **Port**: 8080
- **URL**: http://43.210.87.220:8080

---

## 🎯 Expected Improvements

After deployment:

| Feature | Before | After |
|---------|--------|-------|
| Password Security | Plain text | Hashed (pbkdf2) |
| CSRF Protection | ❌ | ✅ |
| Rate Limiting | ❌ | ✅ |
| Connection Pooling | ❌ | ✅ (max 3) |
| Database Indexes | ❌ | ✅ |
| Webhook URL | Manual | Auto-display |

---

© 2025 SOFTUBON CO.,LTD. - Production Deployment
