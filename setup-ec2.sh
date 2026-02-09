#!/bin/bash
# Setup script for EC2 instance

echo "🔧 Setting up Student Care System on EC2..."

# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv git

# Install system dependencies
sudo apt install -y libpq-dev python3-dev build-essential

# Clone repository (if not exists)
if [ ! -d "~/hikvission_student_care" ]; then
    cd ~
    git clone https://github.com/Yanperm/hikvission_student_care.git
fi

cd ~/hikvission_student_care

# Install Python packages
pip3 install -r requirements.txt

# Create .env file
cat > .env << 'EOL'
DB_TYPE=postgresql
USE_POSTGRES=true
DB_HOST=studentcare.ch0eskuqc3au.ap-southeast-7.rds.amazonaws.com
DB_USER=postgres
DB_PASSWORD=xkiN8gdviN
DB_NAME=postgres
DB_PORT=5432

SECRET_KEY=production-secret-key-change-this
DEBUG=False
PORT=5000
EOL

# Setup systemd service
sudo cp studentcare.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable studentcare
sudo systemctl start studentcare

echo "✅ Setup complete!"
echo "📊 Check status: sudo systemctl status studentcare"
echo "📝 Check logs: sudo journalctl -u studentcare -f"
echo "🌐 Access at: http://43.210.87.220:5000"
