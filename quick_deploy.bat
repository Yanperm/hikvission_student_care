@echo off
echo 🚀 Quick Deploy via Git

REM Push to GitHub
echo.
echo 📤 Pushing to GitHub...
git add .
git commit -m "Update improvements"
git push

REM Pull and restart on server
echo.
echo 📥 Deploying to server...
ssh -i "d:\Hikvission\studentcare.pem" ubuntu@43.210.87.220 "cd /home/ubuntu/hikvission_student_care && git pull && pkill -f local_app.py; nohup python3 local_app.py > app.log 2>&1 & sleep 3 && tail -30 app.log"

echo.
echo ✅ Done! http://43.210.87.220:8080
pause
