@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 Git Pull + Deploy to Server
echo ========================================

set PEM=d:\Hikvission\studentcare.pem
set SERVER=ubuntu@43.210.87.220
set PATH_SERVER=/home/ubuntu/hikvission_student_care

echo.
echo 📤 Pushing to GitHub...
git add .
git commit -m "Update: Improved system with RDS, security, and LINE webhook"
git push origin main

echo.
echo 📥 Pulling on server...
ssh -i "%PEM%" %SERVER% "cd %PATH_SERVER% && git pull"

echo.
echo 📦 Installing dependencies...
ssh -i "%PEM%" %SERVER% "cd %PATH_SERVER% && source venv/bin/activate && pip install -q psycopg2-binary Flask-WTF Flask-Limiter"

echo.
echo 🔄 Restarting application...
ssh -i "%PEM%" %SERVER% "cd %PATH_SERVER% && pkill -f local_app.py; nohup python3 local_app.py > app.log 2>&1 & sleep 3 && tail -30 app.log"

echo.
echo ========================================
echo ✅ Deployment Complete!
echo ========================================
echo.
echo 🌐 URL: http://43.210.87.220:8080
echo 📝 View logs: ssh -i "%PEM%" %SERVER% "tail -f %PATH_SERVER%/app.log"
echo.

pause
