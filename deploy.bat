@echo off
echo Deploying to AWS...

REM Push to GitHub first
git add .
git commit -m "Update: Add LINE OA integration and face recognition"
git push origin main

REM Deploy to AWS
ssh -i studentcare.pem ubuntu@43.210.87.220 "cd ~/hikvission_student_care && git pull && pkill -9 python3 && nohup python3 local_app.py > /tmp/app.log 2>&1 &"

echo.
echo ========================================
echo Deployment completed!
echo ========================================
echo Server: http://43.210.87.220:8080
echo Webhook: http://43.210.87.220:8080/webhook/line
echo ========================================
pause
