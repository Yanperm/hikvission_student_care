#!/bin/bash
# Setup Auto-Restart System

echo "🔧 Setting up Auto-Restart System..."

# 1. Copy systemd service
echo "📋 Installing systemd service..."
sudo cp student-care-production.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable student-care-production
sudo systemctl start student-care-production

# 2. Setup health check cron
echo "⏰ Setting up health check (every 1 minute)..."
chmod +x health_check.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "* * * * * /home/ubuntu/hikvission_student_care/health_check.sh") | crontab -

# 3. Setup log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/student-care > /dev/null <<EOF
/home/ubuntu/hikvission_student_care/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 ubuntu ubuntu
    sharedscripts
    postrotate
        sudo systemctl reload student-care-production > /dev/null 2>&1 || true
    endscript
}
EOF

# 4. Create logs directory
mkdir -p /home/ubuntu/hikvission_student_care/logs

echo "✅ Setup complete!"
echo ""
echo "📊 Status:"
sudo systemctl status student-care-production --no-pager
echo ""
echo "📝 Logs:"
echo "  - Application: tail -f /home/ubuntu/hikvission_student_care/logs/app.log"
echo "  - Health Check: tail -f /home/ubuntu/hikvission_student_care/logs/health_check.log"
echo ""
echo "🔧 Commands:"
echo "  - Start:   sudo systemctl start student-care-production"
echo "  - Stop:    sudo systemctl stop student-care-production"
echo "  - Restart: sudo systemctl restart student-care-production"
echo "  - Status:  sudo systemctl status student-care-production"
