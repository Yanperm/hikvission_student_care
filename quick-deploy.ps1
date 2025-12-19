# Quick Deploy - No S3 needed
# Deploy directly via SSH

Write-Host "🚀 Quick Deploy to EC2..." -ForegroundColor Green

# 1. Create zip
Write-Host "📦 Creating package..." -ForegroundColor Yellow
Compress-Archive -Path * -DestinationPath student-care.zip -Force

# 2. Copy to EC2
Write-Host "📤 Uploading to EC2..." -ForegroundColor Yellow
scp -i "studentcare.pem" student-care.zip ubuntu@43.210.87.220:/home/ubuntu/

# 3. Deploy on EC2
Write-Host "🖥️ Installing on EC2..." -ForegroundColor Yellow
ssh -i "studentcare.pem" ubuntu@43.210.87.220 @"
cd /home/ubuntu
rm -rf hikvission_student_care
unzip -o student-care.zip -d hikvission_student_care
cd hikvission_student_care
mkdir -p data/students
pkill -f gunicorn
nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &
sleep 3
ps aux | grep gunicorn
curl http://localhost:5000
"@

Write-Host "🎉 Done! Access at: http://43.210.87.220:5000" -ForegroundColor Green
