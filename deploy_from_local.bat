@echo off
REM Deploy to AWS EC2 from Windows
echo 🚀 Deploying to AWS EC2...

REM Check if PEM file exists
if not exist "studentcare.pem" (
    echo ❌ Error: studentcare.pem not found!
    echo Please place your AWS PEM file in this directory
    pause
    exit /b 1
)

echo 📤 Uploading deploy script...
scp -i studentcare.pem deploy_aws_new.sh ubuntu@43.210.87.220:~/

echo 🔧 Running deployment...
ssh -i studentcare.pem ubuntu@43.210.87.220 "chmod +x deploy_aws_new.sh && ./deploy_aws_new.sh"

echo ✅ Deployment complete!
echo 🌐 Access: http://43.210.87.220:8080
pause
