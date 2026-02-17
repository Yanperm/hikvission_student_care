@echo off
echo ==================================
echo Deploy to Production Server
echo ==================================

set SERVER_IP=43.210.87.220
set SERVER_USER=ubuntu
set SERVER_PATH=/home/ubuntu/studentcare
set PEM_FILE=studentcare.pem

echo.
echo Preparing files...

echo.
echo Uploading to server...

REM Create directories
ssh -i %PEM_FILE% %SERVER_USER%@%SERVER_IP% "mkdir -p %SERVER_PATH%/security %SERVER_PATH%/routes %SERVER_PATH%/utils"

REM Upload improved files
scp -i %PEM_FILE% database_universal.py %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/
scp -i %PEM_FILE% config.py %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/
scp -i %PEM_FILE% requirements_rds.txt %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/
scp -i %PEM_FILE% .env %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/
scp -i %PEM_FILE% templates\line_setup.html %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/templates/

REM Upload security modules
scp -i %PEM_FILE% security\password_manager.py %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/security/
scp -i %PEM_FILE% security\csrf_protection.py %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/security/
scp -i %PEM_FILE% security\rate_limiter.py %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/security/

REM Upload routes
scp -i %PEM_FILE% routes\auth.py %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/routes/
scp -i %PEM_FILE% routes\students.py %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/routes/

REM Upload utils
scp -i %PEM_FILE% utils\cache.py %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/utils/
scp -i %PEM_FILE% utils\validator.py %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%/utils/

echo.
echo Installing dependencies...
ssh -i %PEM_FILE% %SERVER_USER%@%SERVER_IP% "cd %SERVER_PATH% && source venv/bin/activate && pip install -r requirements_rds.txt"

echo.
echo Restarting application...
ssh -i %PEM_FILE% %SERVER_USER%@%SERVER_IP% "sudo systemctl restart studentcare && sudo systemctl status studentcare --no-pager"

echo.
echo ==================================
echo Deployment Complete!
echo ==================================
echo.
echo Server: http://%SERVER_IP%:8080
echo Check status: sudo systemctl status studentcare
echo View logs: sudo journalctl -u studentcare -f

pause
