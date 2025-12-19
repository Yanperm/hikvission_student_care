# 🚀 Deploy จาก S3 สำเร็จ!

## ✅ อัปโหลดไปยัง S3 แล้ว

- **Bucket:** `student-care-deploy-2025`
- **Files:**
  - `student-care-system.zip` (ระบบทั้งหมด)
  - `deploy_from_s3.sh` (สคริปต์ Deploy)

## 📋 ขั้นตอนต่อไป

### วิธีที่ 1: ใช้ AWS Systems Manager (แนะนำ)

1. เข้า **AWS Console** → **EC2**
2. เลือก Instance `43.210.87.220`
3. คลิก **Connect** → **Session Manager** → **Connect**
4. รันคำสั่ง:

```bash
cd /home/ubuntu
aws s3 cp s3://student-care-deploy-2025/deploy_from_s3.sh .
chmod +x deploy_from_s3.sh
./deploy_from_s3.sh
```

### วิธีที่ 2: ใช้ AWS CLI จากเครื่องนี้

ต้องรู้ Instance ID ก่อน:

```powershell
# หา Instance ID
aws ec2 describe-instances --filters "Name=ip-address,Values=43.210.87.220" --query "Reservations[].Instances[].InstanceId" --output text

# Deploy
aws ssm send-command --instance-ids <INSTANCE-ID> --document-name "AWS-RunShellScript" --parameters commands="cd /home/ubuntu && aws s3 cp s3://student-care-deploy-2025/deploy_from_s3.sh . && chmod +x deploy_from_s3.sh && ./deploy_from_s3.sh"
```

### วิธีที่ 3: ใช้ Git Bash + SSH

```bash
ssh -i studentcare.pem ubuntu@43.210.87.220
cd /home/ubuntu
aws s3 cp s3://student-care-deploy-2025/deploy_from_s3.sh .
chmod +x deploy_from_s3.sh
./deploy_from_s3.sh
```

## 🎯 หลัง Deploy

เปิดเบราว์เซอร์:
```
http://43.210.87.220:8080
```

Login:
- Username: `parent@school.com`
- Password: `parent123`

## 📦 S3 URLs

- **System:** `s3://student-care-deploy-2025/student-care-system.zip`
- **Deploy Script:** `s3://student-care-deploy-2025/deploy_from_s3.sh`

---

**ระบบอยู่บน S3 แล้ว! เลือกวิธี Deploy ที่สะดวกครับ** 🎉
