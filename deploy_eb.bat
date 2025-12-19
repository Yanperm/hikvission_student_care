@echo off
echo Deploying to AWS Elastic Beanstalk...

REM Initialize EB
python -m ebcli.core.ebcore init -p python-3.9 hikvision-student-care --region ap-southeast-1

REM Create environment
python -m ebcli.core.ebcore create hikvision-prod --instance-type t3.medium --envvars FLASK_SECRET_KEY=your_secret_key_here,ADMIN_USERNAME=admin,ADMIN_PASSWORD=admin123

REM Open application
python -m ebcli.core.ebcore open

echo Deployment complete!
pause
