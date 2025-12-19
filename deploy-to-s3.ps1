# Deploy to S3 and EC2 Script
# Run this on Windows

Write-Host "🚀 Starting deployment..." -ForegroundColor Green

# 1. Create zip file
Write-Host "📦 Creating zip file..." -ForegroundColor Yellow
$exclude = @('venv', '__pycache__', '*.pyc', '*.db', 'data/students/*.jpg', '.git', 'studentcare.pem')
Compress-Archive -Path * -DestinationPath student-care.zip -Force -Exclude $exclude

# 2. Upload to S3
Write-Host "📤 Uploading to S3..." -ForegroundColor Yellow
$bucketName = "softubon-deployments"  # เปลี่ยนเป็น bucket ของคุณ
aws s3 cp student-care.zip s3://$bucketName/student-care/student-care.zip --acl public-read

# 3. Get S3 URL
$s3Url = "https://$bucketName.s3.ap-southeast-7.amazonaws.com/student-care/student-care.zip"
Write-Host "✅ Uploaded to: $s3Url" -ForegroundColor Green

# 4. Deploy to EC2
Write-Host "🖥️ Deploying to EC2..." -ForegroundColor Yellow
$deployScript = @"
cd /home/ubuntu
rm -rf hikvission_student_care
wget -O student-care.zip '$s3Url'
unzip -o student-care.zip -d hikvission_student_care
cd hikvission_student_care
mkdir -p data/students
pkill -f gunicorn
nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &
sleep 3
curl http://localhost:5000
echo '✅ Deployment complete!'
"@

ssh -i "studentcare.pem" ubuntu@43.210.87.220 $deployScript

Write-Host "🎉 Done! Access at: http://43.210.87.220:5000" -ForegroundColor Green
