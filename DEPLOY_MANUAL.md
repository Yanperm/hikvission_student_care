# 🚀 Deploy Manual (ระบบอยู่บน S3 แล้ว)

## ✅ ไฟล์บน S3:
- `s3://student-care-deploy-2025/student-care-system.zip`
- `s3://student-care-deploy-2025/deploy_from_s3.sh`

## 📋 วิธี Deploy (เลือก 1 วิธี)

### วิธีที่ 1: AWS Console → Session Manager
1. เข้า https://console.aws.amazon.com/ec2
2. เลือก Instance (IP: 43.210.87.220)
3. คลิก **Connect** → **Session Manager** → **Connect**
4. Copy-Paste คำสั่งนี้:

```bash
cd /home/ubuntu
aws s3 cp s3://student-care-deploy-2025/deploy_from_s3.sh .
chmod +x deploy_from_s3.sh
./deploy_from_s3.sh
```

### วิธีที่ 2: Git Bash
```bash
ssh -i studentcare.pem ubuntu@43.210.87.220
cd /home/ubuntu
aws s3 cp s3://student-care-deploy-2025/deploy_from_s3.sh .
chmod +x deploy_from_s3.sh
./deploy_from_s3.sh
```

### วิธีที่ 3: Manual Commands
```bash
# SSH เข้า EC2
cd /home/ubuntu
aws s3 cp s3://student-care-deploy-2025/student-care-system.zip .
unzip -o student-care-system.zip -d hikvission_student_care
cd hikvission_student_care
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 wsgi:app
```

## 🎯 ทดสอบ
```
http://43.210.87.220:8080
```

**ใช้ AWS Console → Session Manager ง่ายที่สุดครับ!** 🎉
