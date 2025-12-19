@echo off
echo ========================================
echo   AWS EC2 Deployment
echo   Student Care System
echo ========================================
echo.

echo [1/3] Uploading deploy script...
scp -i studentcare.pem -o StrictHostKeyChecking=no deploy_aws_new.sh ubuntu@43.210.87.220:~/

echo.
echo [2/3] Running deployment on EC2...
ssh -i studentcare.pem -o StrictHostKeyChecking=no ubuntu@43.210.87.220 "chmod +x deploy_aws_new.sh && ./deploy_aws_new.sh"

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Access: http://43.210.87.220:8080
echo Login: admin@softubon.com / Admin@2025
echo.
pause
