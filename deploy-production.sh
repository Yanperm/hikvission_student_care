#!/bin/bash
# Production Deployment Script

echo "🚀 Deploying to Production..."

# Set environment variables
export USE_RDS=true
export DB_HOST="your-rds-endpoint.rds.amazonaws.com"
export DB_NAME="studentcare"
export DB_USER="postgres"
export DB_PASSWORD="your-password"
export DB_PORT="5432"
export S3_BUCKET="studentcare-files-xxxxx"
export SECRET_KEY="$(openssl rand -hex 32)"

# Save to .env file
cat > /home/ubuntu/.env << EOF
USE_RDS=true
DB_HOST=$DB_HOST
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_PORT=$DB_PORT
S3_BUCKET=$S3_BUCKET
SECRET_KEY=$SECRET_KEY
EOF

# Deploy code
cd /home/ubuntu
rm -rf hikvission_student_care
unzip -o student-care.zip -d hikvission_student_care
cd hikvission_student_care

# Install dependencies
pip install -r requirements-production.txt

# Initialize database
python3 -c "from database_rds import db; print('✅ Database initialized')"

# Restart application
pkill -f gunicorn
nohup gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &

sleep 3
ps aux | grep gunicorn

echo "✅ Production deployment complete!"
echo "🌐 Access at: http://43.210.87.220:5000"
