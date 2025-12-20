#!/bin/bash
# Deploy to existing EC2 - Updated Version
# © 2025 SOFTUBON CO.,LTD.

set -e  # Exit on error

echo "========================================"
echo "  🚀 Student Care System Deployment"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1/8] Stopping old application...${NC}"
pkill -f gunicorn || true
pkill -f "python.*local_app" || true

echo -e "${YELLOW}[2/8] Backing up old version...${NC}"
cd /home/ubuntu
if [ -d "hikvission_student_care" ]; then
    mv hikvission_student_care hikvission_student_care_backup_$(date +%Y%m%d_%H%M%S)
fi

echo -e "${YELLOW}[3/8] Cloning from GitHub...${NC}"
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

echo -e "${YELLOW}[4/8] Installing dependencies...${NC}"
pip3 install -r requirements.txt
pip3 install python-dotenv gunicorn

echo -e "${YELLOW}[5/8] Setting up environment...${NC}"
cat > .env << 'EOF'
USE_RDS=false
SECRET_KEY=change-this-in-production
DEBUG=False
PORT=5000
CLOUD_API_URL=http://43.210.87.220:8080
EOF

echo -e "${YELLOW}[6/8] Setting up database...${NC}"
mkdir -p data/students
python3 -c "from database import db; print('✅ Database initialized')"

echo -e "${YELLOW}[7/8] Starting application...${NC}"
nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &

sleep 3

echo -e "${YELLOW}[8/8] Checking status...${NC}"
if pgrep -f gunicorn > /dev/null; then
    echo -e "${GREEN}✅ Application started successfully!${NC}"
    ps aux | grep gunicorn | grep -v grep
else
    echo "❌ Failed to start application"
    echo "Last 20 lines of log:"
    tail -20 student-care.log
    exit 1
fi

echo ""
echo "========================================"
echo -e "  ${GREEN}✅ Deployment Completed!${NC}"
echo "========================================"
echo ""
echo "🌐 Access at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
echo ""
echo "📝 Useful commands:"
echo "   View logs: tail -f ~/hikvission_student_care/student-care.log"
echo "   Restart: pkill -f gunicorn && cd ~/hikvission_student_care && nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &"
echo "   Stop: pkill -f gunicorn"
echo ""
