#!/bin/bash
# AWS EC2 Deployment Script
# © 2025 SOFTUBON CO.,LTD.

echo "🚀 Starting deployment to AWS EC2..."

# Variables
EC2_IP="43.210.87.220"
EC2_USER="ubuntu"
PEM_FILE="studentcare.pem"
APP_DIR="/home/ubuntu/hikvission_student_care"
REPO_URL="https://github.com/Yanperm/hikvission_student_care.git"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Deployment Configuration:${NC}"
echo "   EC2 IP: $EC2_IP"
echo "   User: $EC2_USER"
echo "   App Dir: $APP_DIR"
echo ""

# Check if PEM file exists
if [ ! -f "$PEM_FILE" ]; then
    echo -e "${RED}❌ Error: $PEM_FILE not found!${NC}"
    echo "   Please place your PEM file in the current directory"
    exit 1
fi

# Set PEM file permissions
chmod 400 $PEM_FILE

echo -e "${GREEN}✅ Step 1: Connecting to EC2...${NC}"

# Deploy commands
ssh -i $PEM_FILE -o StrictHostKeyChecking=no $EC2_USER@$EC2_IP << 'ENDSSH'

echo "🔄 Step 2: Stopping current application..."
pkill -f gunicorn || true
pkill -f "python.*local_app" || true

echo "📥 Step 3: Pulling latest code from GitHub..."
cd /home/ubuntu

# Remove old directory if exists
if [ -d "hikvission_student_care" ]; then
    echo "   Backing up old version..."
    mv hikvission_student_care hikvission_student_care_backup_$(date +%Y%m%d_%H%M%S)
fi

# Clone fresh copy
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

echo "📦 Step 4: Installing dependencies..."
pip3 install -r requirements.txt
pip3 install python-dotenv gunicorn

echo "⚙️ Step 5: Setting up environment..."
# Create .env file
cat > .env << 'EOF'
USE_RDS=false
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
PORT=5000
CLOUD_API_URL=http://43.210.87.220:8080
EOF

echo "🗄️ Step 6: Setting up database..."
# Create data directory
mkdir -p data/students

# Initialize database
python3 -c "from database import db; print('Database initialized')"

echo "🚀 Step 7: Starting application..."
# Start with Gunicorn
nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &

# Wait a bit
sleep 3

# Check if running
if pgrep -f gunicorn > /dev/null; then
    echo "✅ Application started successfully!"
    echo "📊 Process info:"
    ps aux | grep gunicorn | grep -v grep
else
    echo "❌ Failed to start application"
    echo "📋 Last 20 lines of log:"
    tail -20 student-care.log
    exit 1
fi

echo ""
echo "🎉 Deployment completed!"
echo "🌐 Access at: http://43.210.87.220:5000"
echo ""
echo "📝 Useful commands:"
echo "   View logs: tail -f ~/hikvission_student_care/student-care.log"
echo "   Restart: pkill -f gunicorn && cd ~/hikvission_student_care && nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &"
echo "   Stop: pkill -f gunicorn"

ENDSSH

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${YELLOW}🌐 Your application is now running at:${NC}"
echo -e "   ${GREEN}http://43.210.87.220:5000${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "   1. Test the application"
echo "   2. Check logs if needed: ssh -i $PEM_FILE $EC2_USER@$EC2_IP 'tail -f ~/hikvission_student_care/student-care.log'"
echo "   3. Set up SSL (optional)"
echo ""
