# 🔑 วิธีหา PEM File

## ถ้าคุณเป็นคนสร้าง EC2:

1. ไปที่ AWS Console → EC2
2. คลิก Key Pairs (ด้านซ้าย)
3. ถ้ามี key อยู่แล้ว → ดาวน์โหลดไม่ได้ (AWS ไม่เก็บ)
4. ต้องสร้าง key ใหม่:
   - คลิก "Create key pair"
   - ตั้งชื่อ: `studentcare-new`
   - Type: RSA
   - Format: .pem
   - คลิก Create → จะดาวน์โหลดทันที

5. แนบ key ใหม่กับ EC2:
   - เลือก EC2 instance
   - Actions → Security → Modify IAM role
   - หรือใช้ AWS Systems Manager (ไม่ต้องใช้ PEM)

## ถ้าไม่มี PEM file เลย:

### ใช้ AWS Systems Manager Session Manager (แนะนำ)

ไม่ต้องใช้ PEM file เลย!

1. ไปที่ AWS Console → EC2
2. เลือก instance ของคุณ
3. คลิก "Connect"
4. เลือกแท็บ "Session Manager"
5. คลิก "Connect"
6. จะเปิด terminal ใน browser

จากนั้นรัน:
```bash
curl -sSL https://raw.githubusercontent.com/Yanperm/hikvission_student_care/main/deploy_aws_new.sh | bash
```

---

© 2025 SOFTUBON CO.,LTD.
