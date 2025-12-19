# Production Setup Guide

## 1. สร้าง RDS Database

```bash
# ใน AWS Console
1. ไปที่ RDS → Create database
2. เลือก PostgreSQL (แนะนำ) หรือ MySQL
3. Template: Production
4. DB instance: db.t3.micro (Free Tier) หรือ db.t3.small
5. DB name: studentcare
6. Username: admin
7. Password: (สร้าง strong password)
8. Storage: 20 GB (Auto-scaling enabled)
9. VPC: Same as EC2
10. Public access: No (ใช้ใน VPC เดียวกับ EC2)
11. Security group: เปิด port 5432 (PostgreSQL) หรือ 3306 (MySQL) จาก EC2 security group
```

## 2. สร้าง S3 Bucket สำหรับเก็บรูปนักเรียน

```bash
aws s3 mb s3://studentcare-files --region ap-southeast-7
aws s3api put-bucket-versioning --bucket studentcare-files --versioning-configuration Status=Enabled
```

## 3. สร้าง ElastiCache Redis (Optional - สำหรับ session/cache)

```bash
# ใน AWS Console
1. ไปที่ ElastiCache → Create
2. เลือก Redis
3. Node type: cache.t3.micro
4. Number of replicas: 0 (สำหรับเริ่มต้น)
```

## 4. ติดตั้งบน EC2

```bash
# SSH เข้า EC2
ssh -i "studentcare.pem" ubuntu@43.210.87.220

# ติดตั้ง dependencies
pip install psycopg2-binary boto3 redis

# ตั้งค่า Environment Variables
cat >> ~/.bashrc << EOF
export DB_HOST="your-rds-endpoint.rds.amazonaws.com"
export DB_NAME="studentcare"
export DB_USER="admin"
export DB_PASSWORD="your-password"
export S3_BUCKET="studentcare-files"
export SECRET_KEY="$(openssl rand -hex 32)"
EOF

source ~/.bashrc

# Deploy
cd /home/ubuntu
# ... deploy code ...

# ใช้ database_rds.py แทน database.py
```

## 5. ข้อดีของ Production Setup

✅ **ข้อมูลไม่หาย** - เก็บใน RDS ถาวร
✅ **Backup อัตโนมัติ** - RDS backup ทุกวัน
✅ **Scale ได้** - เพิ่ม EC2 instance ได้หลายตัว
✅ **ปลอดภัย** - Database ไม่เปิดสู่ internet
✅ **รูปภาพปลอดภัย** - เก็บใน S3 มี versioning
✅ **เร็วขึ้น** - ใช้ Redis cache

## 6. ราคาประมาณ (ต่อเดือน)

- EC2 t3.small: ~$15
- RDS db.t3.micro: ~$15 (Free Tier 1 ปีแรก)
- S3: ~$1-5 (ขึ้นกับจำนวนรูป)
- ElastiCache (optional): ~$12

**รวม: ~$30-50/เดือน** (หลัง Free Tier)

## 7. Alternative: ใช้ AWS Lightsail

ถ้าต้องการราคาถูกกว่า:
- Lightsail Instance: $10/เดือน
- Lightsail Database: $15/เดือน
- **รวม: $25/เดือน (ราคาคงที่)**
