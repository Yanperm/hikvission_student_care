#!/bin/bash
# Deploy from S3 to EC2
# © 2025 SOFTUBON CO.,LTD.

set -e

echo "🚀 Deploying from S3..."

# Download from S3
cd /home/ubuntu
aws s3 cp s3://student-care-deploy-2025/student-care-system.zip .

# Extract
unzip -o student-care-system.zip -d hikvission_student_care
cd hikvission_student_care

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create systemd service
sudo tee /etc/systemd/system/student-care.service > /dev/null <<EOF
[Unit]
Description=Student Care System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/hikvission_student_care
Environment="PATH=/home/ubuntu/hikvission_student_care/venv/bin"
ExecStart=/home/ubuntu/hikvission_student_care/venv/bin/gunicorn -w 4 -b 0.0.0.0:8080 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable student-care
sudo systemctl restart student-care

echo "✅ Deployed! Access: http://43.210.87.220:8080"
