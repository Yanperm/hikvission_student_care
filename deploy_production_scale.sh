#!/bin/bash
# Production Deployment Script for 30,000+ students

echo "🚀 Deploying Student Care System (Production Scale)"

# Stop old processes
echo "⏹️ Stopping old processes..."
pkill -9 -f local_app
pkill -9 -f gunicorn

# Pull latest code
echo "📥 Pulling latest code..."
cd /home/ubuntu/hikvission_student_care
git pull

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
pip3 install gunicorn gevent psycopg2-binary

# Create logs directory
mkdir -p logs

# Start with Gunicorn (Production)
echo "🚀 Starting Gunicorn..."
gunicorn -c gunicorn_config.py local_app:app &

# Wait for startup
sleep 10

# Test backend
echo "🔍 Testing backend..."
curl -I http://localhost:5000

# Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

# Check status
echo "✅ Deployment complete!"
echo "📊 Status:"
ps aux | grep gunicorn | grep -v grep
sudo systemctl status nginx | head -5

echo ""
echo "🌐 Access: http://43.210.87.220:8080"
