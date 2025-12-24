@echo off
echo ========================================
echo Auto Deploy to AWS EC2
echo ========================================

echo.
echo [1/4] Adding changes to git...
git add .

echo.
echo [2/4] Committing changes...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update system

git commit -m "%commit_msg%"

echo.
echo [3/4] Pushing to GitHub...
git push

echo.
echo [4/4] Deploying to AWS...
ssh -i studentcare.pem ubuntu@43.210.87.220 "cd ~/hikvission_student_care && git pull && pkill -9 python3 && nohup python3 local_app.py > /tmp/app.log 2>&1 &"

echo.
echo ========================================
echo Deploy Complete!
echo ========================================
echo.
echo Test at: http://43.210.87.220:8080
echo.
pause
