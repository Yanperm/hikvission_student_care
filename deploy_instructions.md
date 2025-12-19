# 🚀 Student Care System - Google Cloud Run Deployment

## ✅ ระบบพร้อม Deploy แล้ว!

### 📋 **ข้อมูลที่ตั้งค่าแล้ว:**
- **Project ID:** solutions-4e649
- **Firebase Config:** ✅ เสร็จแล้ว
- **Database:** Firebase Firestore
- **Region:** asia-southeast1

---

## 🔧 **ขั้นตอนการ Deploy:**

### **1. ติดตั้ง Google Cloud SDK**
```bash
# Download และติดตั้งจาก:
https://cloud.google.com/sdk/docs/install
```

### **2. Login และตั้งค่า Project**
```bash
# Login to Google Cloud
gcloud auth login

# Set project
gcloud config set project solutions-4e649

# Enable APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
```

### **3. สร้าง Service Account Key (สำคัญ!)**
```bash
# ไปที่ Firebase Console:
https://console.firebase.google.com/project/solutions-4e649

# ไป Settings > Service Accounts
# คลิก "Generate new private key"
# Download ไฟล์ JSON
# เปลี่ยนชื่อเป็น "firebase_credentials.json"
# วางในโฟลเดอร์ d:\Hikvission\
```

### **4. Deploy ไป Cloud Run**
```bash
# เปิด Command Prompt ใน d:\Hikvission\
cd d:\Hikvission

# Deploy
gcloud run deploy student-care-system \
    --source . \
    --platform managed \
    --region asia-southeast1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 10 \
    --port 8080
```

### **5. หรือใช้ Script อัตโนมัติ**
```bash
# ทำให้ script executable (ถ้าใช้ Git Bash)
chmod +x deploy.sh

# รัน script
./deploy.sh
```

---

## 🎯 **หลัง Deploy เสร็จ:**

### **URLs ที่จะได้:**
- **Main App:** https://student-care-system-xxx.a.run.app
- **Admin Panel:** https://student-care-system-xxx.a.run.app/admin
- **Features:** https://student-care-system-xxx.a.run.app/features

### **Login Credentials:**
- **Admin:** admin / admin123
- **Teacher:** teacher / teacher123

---

## 📊 **Firebase Firestore Setup:**

### **Collections ที่จะสร้างอัตโนมัติ:**
- `students` - ข้อมูลนักเรียน
- `attendance` - บันทึกการเข้าเรียน
- `system` - การตั้งค่าระบบ

### **ตรวจสอบ Firestore:**
```
https://console.firebase.google.com/project/solutions-4e649/firestore
```

---

## 💡 **Tips:**

### **การ Debug:**
```bash
# ดู logs
gcloud run services logs read student-care-system --region=asia-southeast1

# ดู service details
gcloud run services describe student-care-system --region=asia-southeast1
```

### **การอัปเดต:**
```bash
# Deploy version ใหม่
gcloud run deploy student-care-system --source . --region=asia-southeast1
```

---

## 🔒 **Security Notes:**

1. **Service Account Key** - เก็บไฟล์ JSON ให้ปลอดภัย
2. **Environment Variables** - ใช้ Google Secret Manager ในการผลิต
3. **Authentication** - เปิดใช้ Firebase Auth สำหรับ production

---

## 📞 **Support:**

หากมีปัญหาในการ Deploy:
1. ตรวจสอบ Firebase credentials
2. ตรวจสอบ Google Cloud permissions
3. ดู error logs ใน Cloud Console

**ระบบพร้อม Deploy แล้ว! 🎉**