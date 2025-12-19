#!/bin/bash
# AWS EC2 Quick Deploy - Student Care System
# © 2025 SOFTUBON CO.,LTD.

set -e

echo "🚀 Deploying Student Care System to AWS EC2..."

# 1. Update system
echo "📦 Updating system..."
sudo apt update

# 2. Install dependencies
echo "🔧 Installing dependencies..."
sudo apt install -y python3-pip python3-venv git

# 3. Clone/Update repository
if [ -d "hikvission_student_care" ]; then
    echo "📥 Updating code..."
    cd hikvission_student_care
    git pull
else
    echo "📥 Cloning repository..."
    git clone https://github.com/Yanperm/hikvission_student_care.git
    cd hikvission_student_care
fi

# 4. Setup virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Create .env file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DEBUG=False
PORT=8080
CLOUD_API_URL=http://43.210.87.220:8080
SUPER_ADMIN_USER=admin@softubon.com
SUPER_ADMIN_PASS=Admin@2025
EOF
fi

# 7. Create directories
mkdir -p data/students logs

# 8. Stop existing process
echo "🛑 Stopping existing process..."
pkill -f "python.*local_app.py" || true

# 9. Start application
echo "🚀 Starting application..."
nohup python3 local_app.py > logs/app.log 2>&1 &

sleep 3

# 10. Check status
if pgrep -f "python.*local_app.py" > /dev/null; then
    echo "✅ Deployment successful!"
    echo "🌐 Access: http://43.210.87.220:8080"
    echo "📊 Logs: tail -f logs/app.log"
else
    echo "❌ Deployment failed! Check logs/app.log"
    exit 1
fi
