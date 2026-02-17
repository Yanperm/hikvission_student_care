# 🔌 RDS Connection Guide

## ✅ การเชื่อมต่อ RDS PostgreSQL

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements_rds.txt
```

### 2. ตั้งค่า .env
ไฟล์ `.env` ของคุณมีการตั้งค่าแล้ว:
```env
DB_TYPE=postgresql
USE_POSTGRES=true
DB_HOST=your-rds-host
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_NAME=postgres
DB_PORT=5432
```

### 3. ทดสอบการเชื่อมต่อ
```bash
python test_rds.py
```

**ผลลัพธ์ที่คาดหวัง:**
```
✅ Database type: postgresql
✅ PostgreSQL version: PostgreSQL 15.x...
✅ Users in database: X
✅ Students in database: X
✅ Schools in database: X
✅ Connection successful!
```

### 4. รันแอปพลิเคชัน
```bash
python local_app.py
```

---

## 🔄 ระบบ Universal Database

ไฟล์ `database_universal.py` รองรับทั้ง:
- ✅ **SQLite** (Local Development)
- ✅ **PostgreSQL RDS** (Production)

### Auto-Detection
ระบบจะตรวจสอบ environment variables อัตโนมัติ:
- ถ้า `USE_POSTGRES=true` → ใช้ PostgreSQL RDS
- ถ้าไม่มี → ใช้ SQLite

---

## 🔐 Security Features

### Password Hashing
- ✅ ทุก password ถูก hash ด้วย `pbkdf2:sha256`
- ✅ ไม่มี plain text passwords
- ✅ รองรับทั้ง SQLite และ PostgreSQL

### Database Indexes
- ✅ `students.school_id`
- ✅ `attendance.student_id`
- ✅ `attendance.timestamp`

---

## 📊 Database Schema

### Tables Created
1. **schools** - ข้อมูลโรงเรียน
2. **users** - ผู้ใช้งาน (hashed passwords)
3. **students** - นักเรียน
4. **attendance** - การเข้าเรียน
5. **behavior** - พฤติกรรม
6. **notifications** - การแจ้งเตือน

### Demo Data
- ✅ Super Admin: `superadmin` / `admin123`
- ✅ School: `SCH001` (โรงเรียนสาธิต)

---

## 🔧 Troubleshooting

### ❌ Connection Failed

#### 1. Check RDS Security Group
```bash
# ต้องเปิด Port 5432 สำหรับ IP ของคุณ
# AWS Console → RDS → Security Groups → Inbound Rules
```

#### 2. Check Credentials
```bash
# ทดสอบด้วย psql
psql -h your-rds-host \
     -U postgres -d postgres -p 5432
```

#### 3. Install psycopg2
```bash
pip install psycopg2-binary
```

#### 4. Check .env File
```bash
cat .env | grep DB_
```

### ❌ Import Error

```bash
# ติดตั้ง dependencies ทั้งหมด
pip install -r requirements_rds.txt
```

### ❌ Table Not Found

```bash
# ลบและสร้างใหม่
python -c "from database_universal import db; print('Tables created')"
```

---

## 🚀 Deployment

### Local Development (SQLite)
```bash
# ปิด PostgreSQL ใน .env
USE_POSTGRES=false

python local_app.py
```

### Production (RDS)
```bash
# เปิด PostgreSQL ใน .env
USE_POSTGRES=true

gunicorn local_app:app -w 4 -b 0.0.0.0:5000
```

---

## 📈 Performance

### SQLite vs PostgreSQL

| Feature | SQLite | PostgreSQL RDS |
|---------|--------|----------------|
| Concurrent Users | 1-10 | 100+ |
| Data Size | < 1GB | Unlimited |
| Backup | File copy | Automated |
| Scalability | Low | High |
| Cost | Free | ~$15/month |

---

## 🔄 Migration

### SQLite → PostgreSQL

```python
# 1. Export from SQLite
import sqlite3
import json

conn = sqlite3.connect('data/database.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM students')
students = cursor.fetchall()

with open('students_export.json', 'w') as f:
    json.dump(students, f)

# 2. Import to PostgreSQL
from database_universal import db

for student in students:
    db.add_student(...)
```

---

## 📝 API Compatibility

ทุก API ทำงานเหมือนเดิม:
- ✅ `db.get_students(school_id)`
- ✅ `db.add_student(...)`
- ✅ `db.get_user(username)`
- ✅ `db.add_attendance(...)`

**ไม่ต้องแก้โค้ดเดิม!**

---

## 🎯 Next Steps

1. ✅ ทดสอบการเชื่อมต่อ: `python test_rds.py`
2. ✅ รันแอป: `python local_app.py`
3. ✅ ตรวจสอบข้อมูล: เข้า http://localhost:5000
4. ✅ Deploy to production

---

## 📞 Support

หากมีปัญหา:
1. ตรวจสอบ RDS Security Group
2. ตรวจสอบ credentials ใน .env
3. ดู logs: `python test_rds.py`

---

© 2025 SOFTUBON CO.,LTD. - RDS Ready
