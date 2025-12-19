# 🚀 Deploy ทันที - คำสั่งพร้อมใช้

## 📋 ข้อมูล
- **Server:** 43.210.87.220
- **Key File:** studentcare.pem
- **User:** ubuntu
- **Port:** 8080

## 🔑 Step 1: เชื่อมต่อ EC2

### Windows (PowerShell):
```powershell
ssh -i "studentcare.pem" ubuntu@43.210.87.220
```

### Mac/Linux:
```bash
chmod 400 studentcare.pem
ssh -i studentcare.pem ubuntu@43.210.87.220
```

## 🚀 Step 2: Deploy (Auto)

```bash
curl -o deploy.sh https://raw.githubusercontent.com/Yanperm/hikvission_student_care/main/deploy_to_ec2.sh
chmod +x deploy.sh
./deploy.sh
```

## 👨‍👩‍👧 Step 3: เพิ่มข้อมูลผู้ปกครอง

```bash
cd ~/hikvission_student_care
source venv/bin/activate
python add_parent_relation.py
```

## ✅ Step 4: ทดสอบ

เปิดเบราว์เซอร์:
```
http://43.210.87.220:8080
```

Login:
- Username: `parent@school.com`
- Password: `parent123`

---

## 🎯 คำสั่งเดียวจบ (Copy-Paste):

```bash
ssh -i studentcare.pem ubuntu@43.210.87.220 "curl -o deploy.sh https://raw.githubusercontent.com/Yanperm/hikvission_student_care/main/deploy_to_ec2.sh && chmod +x deploy.sh && ./deploy.sh"
```

**เสร็จแล้วเปิด:** http://43.210.87.220:8080 🎉
