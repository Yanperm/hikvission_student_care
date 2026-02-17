@echo off
echo ========================================
echo   DEPLOY TO AWS EC2 - QUICK
echo ========================================
echo.

echo [1/3] Push code to GitHub...
git add .
git commit -m "Fix: student image placeholder"
git push origin main

echo.
echo [2/3] SSH to EC2 and deploy...
echo Run this on EC2:
echo.
echo   cd /home/ubuntu/hikvission_student_care
echo   git pull origin main
echo   sudo systemctl restart student-care
echo.

echo [3/3] Done!
echo Server URL: http://43.210.87.220:8080
pause
