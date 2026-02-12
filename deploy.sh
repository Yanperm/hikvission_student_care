#!/bin/bash
# Deploy to AWS EC2
# Usage: ./deploy.sh

SERVER="ubuntu@43.210.87.220"
REMOTE_DIR="/home/ubuntu/hikvission_student_care"

echo "🚀 Starting deployment to AWS..."

# 1. Create deployment package
echo "📦 Creating deployment package..."
tar -czf deploy.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='deploy.tar.gz' \
    .

# 2. Upload to server
echo "📤 Uploading to server..."
scp deploy.tar.gz $SERVER:~

# 3. Deploy on server
echo "🔧 Deploying on server..."
ssh $SERVER << 'EOF'
    # Stop current service
    sudo systemctl stop student-care || true
    
    # Backup current version
    if [ -d "$REMOTE_DIR" ]; then
        sudo mv $REMOTE_DIR ${REMOTE_DIR}_backup_$(date +%Y%m%d_%H%M%S)
    fi
    
    # Extract new version
    mkdir -p $REMOTE_DIR
    tar -xzf ~/deploy.tar.gz -C $REMOTE_DIR
    cd $REMOTE_DIR
    
    # Install dependencies
    pip3 install -r requirements.txt
    
    # Set permissions
    chmod +x start.sh
    
    # Start service
    sudo systemctl start student-care
    sudo systemctl enable student-care
    
    # Cleanup
    rm ~/deploy.tar.gz
    
    echo "✅ Deployment completed!"
EOF

# 4. Cleanup local
rm deploy.tar.gz

echo "🎉 Deployment finished!"
echo "🌐 Access at: http://43.210.87.220:8080"
echo "🔗 Webhook URL: http://43.210.87.220:8080/webhook/line"
