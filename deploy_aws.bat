@echo off
REM AWS EC2 Deployment Script for Windows
REM © 2025 SOFTUBON CO.,LTD.

echo ========================================
echo   AWS EC2 Deployment Script
echo   Student Care System
echo ========================================
echo.

REM Variables
set EC2_IP=43.210.87.220
set EC2_USER=ubuntu
set PEM_FILE=studentcare.pem
set APP_DIR=/home/ubuntu/hikvission_student_care

echo [1/8] Checking PEM file...
if not exist "%PEM_FILE%" (
    echo ERROR: %PEM_FILE% not found!
    echo Please place your PEM file in the current directory
    pause
    exit /b 1
)
echo OK: PEM file found

echo.
echo [2/8] Pushing to GitHub...
git add .
git commit -m "Deploy: Update %date% %time%"
git push origin main
if errorlevel 1 (
    echo WARNING: Git push failed or no changes to commit
    echo Continuing with deployment...
)

echo.
echo [3/8] Connecting to EC2...
echo Deploying to: %EC2_USER%@%EC2_IP%

REM Create deployment commands file
echo cd /home/ubuntu > deploy_commands.txt
echo echo "Stopping current application..." >> deploy_commands.txt
echo pkill -f gunicorn ^|^| true >> deploy_commands.txt
echo pkill -f "python.*local_app" ^|^| true >> deploy_commands.txt
echo echo "Removing old directory..." >> deploy_commands.txt
echo rm -rf hikvission_student_care >> deploy_commands.txt
echo echo "Cloning from GitHub..." >> deploy_commands.txt
echo git clone https://github.com/Yanperm/hikvission_student_care.git >> deploy_commands.txt
echo cd hikvission_student_care >> deploy_commands.txt
echo echo "Installing dependencies..." >> deploy_commands.txt
echo pip3 install -r requirements.txt >> deploy_commands.txt
echo pip3 install python-dotenv gunicorn >> deploy_commands.txt
echo echo "Creating .env file..." >> deploy_commands.txt
echo echo "USE_RDS=false" ^> .env >> deploy_commands.txt
echo echo "DEBUG=False" ^>^> .env >> deploy_commands.txt
echo echo "PORT=5000" ^>^> .env >> deploy_commands.txt
echo echo "Setting up database..." >> deploy_commands.txt
echo mkdir -p data/students >> deploy_commands.txt
echo python3 -c "from database import db; print('Database initialized')" >> deploy_commands.txt
echo echo "Starting application..." >> deploy_commands.txt
echo nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app ^> student-care.log 2^>^&1 ^& >> deploy_commands.txt
echo sleep 3 >> deploy_commands.txt
echo echo "Checking status..." >> deploy_commands.txt
echo ps aux ^| grep gunicorn ^| grep -v grep >> deploy_commands.txt
echo echo "Deployment completed!" >> deploy_commands.txt

REM Execute deployment
ssh -i %PEM_FILE% -o StrictHostKeyChecking=no %EC2_USER%@%EC2_IP% "bash -s" < deploy_commands.txt

REM Cleanup
del deploy_commands.txt

echo.
echo ========================================
echo   Deployment Completed!
echo ========================================
echo.
echo Application URL: http://%EC2_IP%:5000
echo.
echo Useful commands:
echo   View logs: ssh -i %PEM_FILE% %EC2_USER%@%EC2_IP% "tail -f ~/hikvission_student_care/student-care.log"
echo   Restart: ssh -i %PEM_FILE% %EC2_USER%@%EC2_IP% "pkill -f gunicorn && cd ~/hikvission_student_care && nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &"
echo.
pause
