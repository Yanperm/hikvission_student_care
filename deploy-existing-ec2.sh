#!/bin/bash
# Deploy to existing EC2

echo "🚀 Deploying Student Care System..."

# Clone project
cd /home/ubuntu
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# Create systemd service
sudo tee /etc/systemd/system/student-care.service > /dev/null <<EOF
[Unit]
Description=Student Care System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/hikvission_student_care
Environment="PATH=/home/ubuntu/hikvission_student_care/venv/bin"
ExecStart=/home/ubuntu/hikvission_student_care/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 local_app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable student-care
sudo systemctl start student-care

# Update Nginx (append to existing config)
sudo tee -a /etc/nginx/sites-available/default > /dev/null <<EOF

# Student Care System
location /student-care {
    rewrite ^/student-care(.*) \$1 break;
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
}
EOF

sudo nginx -t && sudo systemctl reload nginx

echo "✅ Done!"
echo "🌐 Access at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/student-care"
