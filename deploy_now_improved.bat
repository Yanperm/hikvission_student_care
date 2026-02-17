@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 Deploy Improvements to Server
echo ========================================

set SERVER=ubuntu@43.210.87.220
set PATH_SERVER=/home/ubuntu/studentcare
set PEM=studentcare.pem

echo.
echo 📦 Creating directories...
ssh -i %PEM% %SERVER% "mkdir -p %PATH_SERVER%/security %PATH_SERVER%/routes %PATH_SERVER%/utils"

echo.
echo 📤 Uploading improved files...

echo   → database_universal.py
scp -i %PEM% database_universal.py %SERVER%:%PATH_SERVER%/

echo   → config.py
scp -i %PEM% config.py %SERVER%:%PATH_SERVER%/

echo   → requirements_rds.txt
scp -i %PEM% requirements_rds.txt %SERVER%:%PATH_SERVER%/

echo   → .env
scp -i %PEM% .env %SERVER%:%PATH_SERVER%/

echo   → security modules
scp -i %PEM% security\password_manager.py %SERVER%:%PATH_SERVER%/security/
scp -i %PEM% security\csrf_protection.py %SERVER%:%PATH_SERVER%/security/
scp -i %PEM% security\rate_limiter.py %SERVER%:%PATH_SERVER%/security/

echo   → routes
scp -i %PEM% routes\auth.py %SERVER%:%PATH_SERVER%/routes/
scp -i %PEM% routes\students.py %SERVER%:%PATH_SERVER%/routes/

echo   → utils
scp -i %PEM% utils\cache.py %SERVER%:%PATH_SERVER%/utils/
scp -i %PEM% utils\validator.py %SERVER%:%PATH_SERVER%/utils/

echo   → templates
scp -i %PEM% templates\line_setup.html %SERVER%:%PATH_SERVER%/templates/

echo.
echo 🔧 Installing dependencies...
ssh -i %PEM% %SERVER% "cd %PATH_SERVER% && source venv/bin/activate && pip install -q psycopg2-binary Flask-WTF Flask-Limiter"

echo.
echo 🔄 Restarting service...
ssh -i %PEM% %SERVER% "sudo systemctl restart studentcare"

timeout /t 3 >nul

echo.
echo 📊 Checking status...
ssh -i %PEM% %SERVER% "sudo systemctl status studentcare --no-pager -l"

echo.
echo ========================================
echo ✅ Deployment Complete!
echo ========================================
echo.
echo 🌐 URL: http://43.210.87.220:8080
echo 📝 Logs: ssh -i %PEM% %SERVER% "sudo journalctl -u studentcare -f"
echo.

pause
