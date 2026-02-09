@echo off
echo Deploying to AWS EC2...

ssh -i studentcare.pem ubuntu@43.210.87.220 "cd ~/hikvission_student_care && git pull && pip3 install -r requirements.txt && pkill -9 python3 && nohup python3 local_app.py > /tmp/app.log 2>&1 &"

echo.
echo Deployment complete!
echo App running at: http://43.210.87.220:5000
echo Check logs: ssh -i studentcare.pem ubuntu@43.210.87.220 "tail -f /tmp/app.log"
pause
