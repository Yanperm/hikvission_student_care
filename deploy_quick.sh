#!/bin/bash
# Quick Deploy Script for AWS EC2
# © 2025 SOFTUBON CO.,LTD.

echo "🚀 Starting deployment..."

# Update code
echo "📥 Pulling latest code..."
git pull

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Restart application
echo "🔄 Restarting application..."
sudo supervisorctl restart student-care

# Check status
echo "✅ Checking status..."
sudo supervisorctl status student-care

echo "🎉 Deployment complete!"
echo "🌐 Access: http://43.210.87.220:8080"
