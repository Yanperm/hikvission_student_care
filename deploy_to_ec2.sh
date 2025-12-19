#!/bin/bash
# Complete EC2 Deployment Script
# © 2025 SOFTUBON CO.,LTD.

set -e

echo "🚀 Student Care System - EC2 Deployment"
echo "========================================"

# Variables
APP_DIR="/home/ubuntu/hikvission_student_care"
REPO_URL="https://github.com/Yanperm/hikvission_student_care.git"
PORT=8080

# Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv git nginx

# Clone or update repository
if [ -d "$APP_DIR" ]; then
    echo "📥 Updating repository..."
    cd $APP_DIR
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# Setup virtual environment
echo "🐍 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data/students

# Setup systemd service
echo "⚙️ Setting up systemd service..."
sudo tee /etc/systemd/system/student-care.service > /dev/null <<EOF
[Unit]
Description=Student Care System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload and start service
echo "🔄 Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable student-care
sudo systemctl restart student-care

# Wait for service to start
sleep 3

# Check status
echo "✅ Checking service status..."
sudo systemctl status student-care --no-pager

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow $PORT/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo ""
echo "🎉 Deployment Complete!"
echo "========================================"
echo "🌐 Access: http://$(curl -s ifconfig.me):$PORT"
echo "📊 Status: sudo systemctl status student-care"
echo "📝 Logs: sudo journalctl -u student-care -f"
echo "========================================"
