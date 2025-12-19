#!/bin/bash
# Deploy Script for AWS EC2

echo "🚀 Starting deployment..."

# Update system
sudo apt update
sudo apt install -y python3-pip python3-venv nginx

# Setup project
cd /home/ubuntu
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-prod.txt

# Create systemd service
sudo tee /etc/systemd/system/student-care.service > /dev/null <<EOF
[Unit]
Description=Student Care System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/hikvission_student_care
Environment="PATH=/home/ubuntu/hikvission_student_care/venv/bin"
ExecStart=/home/ubuntu/hikvission_student_care/venv/bin/gunicorn -w 4 -b 0.0.0.0:8080 local_app:app

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
sudo tee /etc/nginx/sites-available/student-care > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/student-care /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start services
sudo systemctl daemon-reload
sudo systemctl enable student-care
sudo systemctl start student-care
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "🌐 Access at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
