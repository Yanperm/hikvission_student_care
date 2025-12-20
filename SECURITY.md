# 🔒 Security Guide - คู่มือความปลอดภัย

## ⚠️ ไฟล์ที่ห้าม Commit ลง GitHub

### 🚫 ไฟล์เหล่านี้ถูกป้องกันโดย .gitignore แล้ว

```
.env                          ← ข้อมูลการตั้งค่าจริง
.env.local
.env.production
*.pem                         ← SSH Keys
*.key                         ← Private Keys
firebase_credentials.json     ← Firebase Credentials
config.json                   ← Configuration ที่มีรหัสผ่าน
*.sql                         ← Database Backups
data/database.db              ← SQLite Database
```

## ✅ ไฟล์ที่ปลอดภัย (Commit ได้)

```
.env.example                  ← Template ไม่มีข้อมูลจริง
.gitignore                    ← รายการไฟล์ที่ไม่ต้อง commit
README.md                     ← เอกสาร
requirements.txt              ← Dependencies
```

## 🔍 ตรวจสอบก่อน Push

### 1. ตรวจสอบว่าไฟล์อะไรจะถูก commit
```bash
git status
```

### 2. ตรวจสอบว่า .env ไม่อยู่ในรายการ
```bash
git ls-files | grep .env
# ต้องไม่มีผลลัพธ์ หรือเห็นแค่ .env.example
```

### 3. ถ้าเผลอ commit .env ไปแล้ว
```bash
# ลบออกจาก Git (แต่ไฟล์ยังอยู่ในเครื่อง)
git rm --cached .env
git commit -m "Remove .env from repository"
git push

# ⚠️ แต่คนที่ clone ไปแล้วยังเห็นอยู่!
# ต้องเปลี่ยนรหัสผ่านทั้งหมดทันที!
```

## 🛡️ Best Practices

### 1. ใช้ .env.example แทน .env
```bash
# คนอื่นที่ clone ไป
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

# คัดลอกและแก้ไข
cp .env.example .env
nano .env  # กรอกค่าจริง
```

### 2. ตั้งรหัสผ่านที่แข็งแรง
```
❌ DB_PASSWORD=123456
❌ DB_PASSWORD=admin
✅ DB_PASSWORD=Xk9#mP2$vL8@qR5!
```

### 3. ใช้ AWS Secrets Manager (Production)
```python
import boto3

def get_secret():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='studentcare/db')
    return json.loads(response['SecretString'])
```

### 4. Rotate Keys เป็นประจำ
- เปลี่ยนรหัสผ่าน RDS ทุก 90 วัน
- เปลี่ยน SECRET_KEY เมื่อมีปัญหา
- Revoke LINE Token ที่ไม่ใช้แล้ว

## 🚨 ถ้าเผลอ Commit ข้อมูลลับ

### ทำทันที!
1. **เปลี่ยนรหัสผ่านทั้งหมด**
   - RDS Password
   - AWS Access Keys
   - LINE Tokens
   - SMTP Password

2. **ลบออกจาก Git History**
```bash
# ใช้ BFG Repo-Cleaner
git clone --mirror https://github.com/Yanperm/hikvission_student_care.git
bfg --delete-files .env hikvission_student_care.git
cd hikvission_student_care.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

3. **แจ้งทีม**
   - บอกทุกคนให้ pull ใหม่
   - อัปเดตรหัสผ่านใหม่

## 📋 Checklist ก่อน Push

- [ ] ตรวจสอบ `git status`
- [ ] ไม่มี `.env` ในรายการ
- [ ] ไม่มี `*.pem` ในรายการ
- [ ] ไม่มี `firebase_credentials.json`
- [ ] ไม่มี `config.json` ที่มีรหัสผ่าน
- [ ] ไม่มี `database.db`

## 🔗 Resources

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

---

⚠️ **จำไว้**: ถ้าข้อมูลลับขึ้น GitHub แล้ว ถือว่า "ถูกเปิดเผย" แล้ว
ต้องเปลี่ยนรหัสผ่านทันที ไม่ใช่แค่ลบออก!

© 2025 SOFTUBON CO.,LTD. - Student Care System
