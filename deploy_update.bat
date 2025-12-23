@echo off
echo ========================================
echo   Deploy Update to AWS EC2
echo   Server: 43.210.87.220:8080
echo ========================================
echo.

echo [1/4] Commit changes to Git...
git add .
git commit -m "Update: New pricing with yearly option and reseller packages"
git push origin main

echo.
echo [2/4] Connecting to EC2 and pulling updates...
ssh -i "studentcare.pem" ubuntu@43.210.87.220 "cd ~/hikvission_student_care && git pull origin main"

echo.
echo [3/4] Restarting application...
ssh -i "studentcare.pem" ubuntu@43.210.87.220 "sudo systemctl restart hikvision"

echo.
echo [4/4] Checking status...
ssh -i "studentcare.pem" ubuntu@43.210.87.220 "sudo systemctl status hikvision --no-pager"

echo.
echo ========================================
echo   Deploy Complete!
echo   URL: http://43.210.87.220:8080
echo ========================================
pause
