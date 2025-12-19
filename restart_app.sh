#!/bin/bash
# Restart app script
cd ~/hikvission_student_care
git pull
sudo pkill -f "python.*local_app"
sleep 2
nohup python3 local_app.py > logs/app.log 2>&1 &
sleep 3
curl -s http://localhost:5000/ | grep -q "Student" && echo "✅ App running" || echo "❌ App failed"
