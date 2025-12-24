# 🔧 คู่มือแก้ไขปัญหาและกู้คืนระบบ

## 🚨 เมื่อระบบมีปัญหา

### วิธีที่ 1: Rollback ด้วย Git
```bash
cd ~/hikvission_student_care
git log --oneline -10  # ดู commit ล่าสุด
git reset --hard <commit-hash>  # กลับไปยัง commit ที่ทำงานได้
pkill -9 python3
nohup python3 local_app.py > /tmp/app.log 2>&1 &
```

### วิธีที่ 2: ใช้ Backup Script
```bash
cd ~/hikvission_student_care
bash rollback.sh
```

### วิธีที่ 3: Clone ใหม่ทั้งหมด
```bash
cd ~
mv hikvission_student_care hikvission_student_care_old
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care
pip3 install -r requirements.txt
nohup python3 local_app.py > /tmp/app.log 2>&1 &
```

## 📅 ตั้งค่า Auto Backup (ทำครั้งเดียว)

```bash
# เพิ่ม cron job สำหรับ backup ทุกวัน เวลา 02:00
crontab -e

# เพิ่มบรรทัดนี้:
0 2 * * * /home/ubuntu/hikvission_student_care/auto_backup.sh
```

## 🔍 ตรวจสอบสถานะระบบ

```bash
# ดู log
tail -f /tmp/app.log

# ตรวจสอบ process
ps aux | grep python3

# ทดสอบ API
curl http://localhost:5000/api/students
```

## 📞 ติดต่อ
- GitHub: https://github.com/Yanperm/hikvission_student_care
- Email: support@softubon.com

## 🔑 Commit ที่สำคัญ (ทำงานได้ดี)
- `303a39a` - Fix API test textarea with valid JSON
- `99b59ee` - Fix syntax error at line 820
- `4d480c1` - Add Sidebar Layout to Dashboard

หากมีปัญหา ให้ rollback ไปยัง commit เหล่านี้
