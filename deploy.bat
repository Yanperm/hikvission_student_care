@echo off
REM Auto Deploy to Server

echo ========================================
echo   Auto Deploy to AWS Server
echo ========================================
echo.

REM 1. Git Add, Commit, Push
echo [1/3] Pushing to GitHub...
git add -A
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"
git push
echo.

REM 2. Deploy to Server
echo [2/3] Deploying to Server...
ssh -i "d:\Hikvission\studentcare.pem" ubuntu@43.210.87.220 "cd /home/ubuntu/hikvission_student_care && git pull && sudo systemctl restart student-care-production"
echo.

REM 3. Wait and Check
echo [3/3] Checking status...
timeout /t 5 /nobreak >nul
ssh -i "d:\Hikvission\studentcare.pem" ubuntu@43.210.87.220 "curl -I http://localhost:5000"
echo.

echo ========================================
echo   Deploy Complete!
echo   URL: http://43.210.87.220:8080
echo ========================================
pause
