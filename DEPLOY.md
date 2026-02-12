# 🚀 คู่มือ Deploy ไป AWS

## วิธีที่ 1: ใช้ Script อัตโนมัติ (แนะนำ)

### Windows:
```bash
# ติดตั้ง Git Bash หรือ WSL ก่อน
chmod +x deploy.sh
./deploy.sh
```

### Linux/Mac:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## วิธีที่ 2: Deploy ด้วยตนเอง

### 1. เชื่อมต่อ SSH
```bash
ssh ubuntu@43.210.87.220
```

### 2. Clone หรือ Upload โปรเจค
```bash
# ถ้ามี Git
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

# หรือ Upload ด้วย SCP
# scp -r d:\Hikvission ubuntu@43.210.87.220:~/hikvission_student_care
```

### 3. ติดตั้ง Dependencies
```bash
cd ~/hikvission_student_care
pip3 install -r requirements.txt
```

### 4. ตั้งค่า Environment Variables (ถ้ามี)
```bash
nano .env
# กรอก:
# SECRET_KEY=your-secret-key
# USE_POSTGRES=true
# DATABASE_URL=postgresql://...
```

### 5. ติดตั้ง Systemd Service
```bash
sudo cp student-care.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable student-care
sudo systemctl start student-care
```

### 6. ตรวจสอบสถานะ
```bash
sudo systemctl status student-care
```

### 7. ดู Logs
```bash
sudo journalctl -u student-care -f
```

---

## วิธีที่ 3: รันแบบง่าย (ทดสอบ)

```bash
ssh ubuntu@43.210.87.220
cd ~/hikvission_student_care
python3 local_app.py
```

---

## 🔧 หลัง Deploy เสร็จ

### 1. ตั้งค่า LINE Webhook
- ไปที่: https://developers.line.biz/console/
- Webhook URL: `http://43.210.87.220:8080/webhook/line`
- เปิดใช้งาน Webhook: ON

### 2. ตั้งค่า LINE OA ในระบบ
- เข้า: `http://43.210.87.220:8080/line_setup`
- กรอก Channel Access Token
- กรอก Channel Secret
- กดบันทึก

### 3. ทดสอบระบบ
- เข้า: `http://43.210.87.220:8080`
- Login: admin / admin123
- ทดสอบกล้องหน้าประตู
- ทดสอบส่ง LINE

---

## 🔄 Update โค้ดใหม่

```bash
ssh ubuntu@43.210.87.220
cd ~/hikvission_student_care
git pull  # ถ้าใช้ Git
sudo systemctl restart student-care
```

---

## 🛑 หยุดระบบ

```bash
sudo systemctl stop student-care
```

---

## 📝 Troubleshooting

### ตรวจสอบ Port
```bash
sudo netstat -tulpn | grep 8080
```

### ตรวจสอบ Firewall
```bash
sudo ufw status
sudo ufw allow 8080
```

### ตรวจสอบ Logs
```bash
sudo journalctl -u student-care -n 100
```

---

## 🌐 URLs สำคัญ

- **Web App**: http://43.210.87.220:8080
- **Webhook**: http://43.210.87.220:8080/webhook/line
- **Admin**: http://43.210.87.220:8080/admin
- **Gate Camera**: http://43.210.87.220:8080/camera_gate

---

## 📞 ติดต่อ

หากมีปัญหา ติดต่อ: support@softubon.com
