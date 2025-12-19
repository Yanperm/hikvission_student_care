#!/bin/bash
# EC2 Deployment Script

echo "=== Hikvision Student Care - EC2 Deployment ==="

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install -y libopencv-dev python3-opencv cmake libgl1-mesa-glx

# Install Git
sudo apt install -y git

# Clone repository
cd ~
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

# Install Python packages
pip3 install -r requirements_aws.txt

# Create .env file
cat > .env << EOF
CAMERA_IP=192.168.1.64
CAMERA_USERNAME=admin
CAMERA_PASSWORD=your_password
FLASK_SECRET_KEY=your_secret_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
EOF

# Create directories
mkdir -p data/students logs

# Install and configure systemd service
sudo cp hikvision.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hikvision
sudo systemctl start hikvision

# Install Nginx
sudo apt install -y nginx
sudo cp nginx.conf /etc/nginx/sites-available/hikvision
sudo ln -s /etc/nginx/sites-available/hikvision /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "=== Deployment Complete ==="
echo "Access your application at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
