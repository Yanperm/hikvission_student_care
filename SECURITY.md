# 🔒 Security Guidelines

## ⚠️ สำคัญ: ไฟล์ที่ต้องตั้งค่าก่อนใช้งาน

Repository นี้เป็น **Demo/Educational Purpose** - ไม่มีข้อมูลจริงหรือ credentials ที่ใช้งานได้

### 📋 ไฟล์ที่ต้องสร้างเอง (ไม่รวมใน Git)

1. **`.env`** - Environment Variables
```bash
SECRET_KEY=your-random-secret-key-here
CLOUD_API_URL=http://your-server:8080
SUPER_ADMIN_USER=admin@yourschool.com
SUPER_ADMIN_PASS=your-secure-password
LINE_CHANNEL_ACCESS_TOKEN=your-line-token
LINE_CHANNEL_SECRET=your-line-secret
```

2. **`firebase_credentials.json`** - Firebase Service Account
   - ดาวน์โหลดจาก Firebase Console
   - ใช้ `firebase_credentials.json.example` เป็นแม่แบบ

3. **`config.json`** - Firebase Config
   - คัดลอกจาก Firebase Project Settings
   - ใช้ `config.json.example` เป็นแม่แบบ

4. **`*.pem`** - AWS/SSH Private Keys
   - สร้างใหม่สำหรับ production
   - **ห้าม** commit เข้า Git

## 🛡️ Best Practices

### สำหรับ Development
- ใช้ `.env` file สำหรับ local development
- ใช้ค่า default ที่ปลอดภัย (ไม่ใช่ password จริง)
- Test ด้วยข้อมูลปลอม

### สำหรับ Production
- ใช้ Environment Variables จาก hosting platform
- ใช้ AWS Secrets Manager / Parameter Store
- Enable HTTPS
- เปลี่ยน default passwords ทั้งหมด
- ใช้ strong random SECRET_KEY

## 🚫 ห้ามทำ

- ❌ Commit API keys, passwords, tokens
- ❌ Commit `.pem`, `.key` files
- ❌ Commit `firebase_credentials.json`
- ❌ ใช้ default passwords ใน production
- ❌ Hardcode credentials ในโค้ด

## ✅ ควรทำ

- ✅ ใช้ `.gitignore` ป้องกันไฟล์ลับ
- ✅ ใช้ environment variables
- ✅ สร้าง `.example` files เป็นแม่แบบ
- ✅ เปลี่ยน passwords เป็นประจำ
- ✅ Review code ก่อน commit

## 📞 พบปัญหาด้านความปลอดภัย?

กรุณาแจ้งที่: security@softubon.com

---

© 2025 SOFTUBON CO.,LTD.
