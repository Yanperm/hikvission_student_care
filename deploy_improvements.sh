#!/bin/bash

echo "=================================="
echo "🚀 Deploy to Production Server"
echo "=================================="

# Configuration
SERVER_IP="43.210.87.220"
SERVER_USER="ubuntu"
SERVER_PATH="/home/ubuntu/studentcare"
PEM_FILE="studentcare.pem"

echo ""
echo "📦 Preparing files..."

# Files to deploy
FILES=(
    "database_universal.py"
    "security/password_manager.py"
    "security/csrf_protection.py"
    "security/rate_limiter.py"
    "routes/auth.py"
    "routes/students.py"
    "utils/cache.py"
    "utils/validator.py"
    "config.py"
    "app_improved.py"
    "requirements_rds.txt"
    "templates/line_setup.html"
    ".env"
)

echo "✅ Files ready"

echo ""
echo "📤 Uploading to server..."

# Create directories on server
ssh -i $PEM_FILE $SERVER_USER@$SERVER_IP "mkdir -p $SERVER_PATH/security $SERVER_PATH/routes $SERVER_PATH/utils"

# Upload files
for file in "${FILES[@]}"; do
    echo "  Uploading $file..."
    scp -i $PEM_FILE "$file" $SERVER_USER@$SERVER_IP:$SERVER_PATH/$file
done

echo ""
echo "🔧 Installing dependencies..."
ssh -i $PEM_FILE $SERVER_USER@$SERVER_IP << 'EOF'
cd /home/ubuntu/studentcare
source venv/bin/activate
pip install -r requirements_rds.txt
EOF

echo ""
echo "🔄 Restarting application..."
ssh -i $PEM_FILE $SERVER_USER@$SERVER_IP << 'EOF'
sudo systemctl restart studentcare
sudo systemctl status studentcare --no-pager
EOF

echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
echo ""
echo "🌐 Server: http://$SERVER_IP:8080"
echo "📊 Check status: sudo systemctl status studentcare"
echo "📝 View logs: sudo journalctl -u studentcare -f"
