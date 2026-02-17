#!/bin/bash
# Fix 502 Bad Gateway - รันบน AWS Server

echo "=== ตรวจสอบ Backend ==="
ps aux | grep python | grep -v grep

echo -e "\n=== ตรวจสอบ Port ==="
netstat -tlnp | grep :5000

echo -e "\n=== ตรวจสอบ Systemd Service ==="
systemctl status student-care 2>/dev/null || echo "ไม่มี service student-care"

echo -e "\n=== Restart Backend ==="
pkill -f local_app.py
cd /home/ubuntu/hikvission_student_care || cd /opt/student_care || cd ~
nohup python3 local_app.py > app.log 2>&1 &
sleep 3

echo -e "\n=== ตรวจสอบ Backend ทำงานหรือไม่ ==="
curl -I http://localhost:5000 2>&1 | head -5

echo -e "\n=== Restart Nginx ==="
sudo systemctl restart nginx
sudo systemctl status nginx | head -10

echo -e "\n=== ตรวจสอบ Nginx Config ==="
sudo nginx -t

echo -e "\n=== ดู Error Log ==="
sudo tail -20 /var/log/nginx/error.log

echo -e "\n✅ เสร็จสิ้น - ลองเข้า http://43.210.87.220:8080"
