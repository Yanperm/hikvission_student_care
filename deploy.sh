#!/bin/bash
# Deploy to AWS EC2

echo "🚀 Deploying to AWS EC2..."

# SSH และ deploy
ssh -i studentcare.pem ubuntu@43.210.87.220 << 'EOF'
    cd ~/hikvission_student_care
    
    echo "📥 Pulling latest code..."
    git pull
    
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    
    echo "🛑 Stopping old process..."
    pkill -9 python3
    
    echo "🔄 Starting new process..."
    nohup python3 local_app.py > /tmp/app.log 2>&1 &
    
    echo "✅ Deployment complete!"
    echo "📊 Check logs: tail -f /tmp/app.log"
EOF

echo "🎉 Done! App running at http://43.210.87.220:5000"
