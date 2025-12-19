#!/bin/bash
# Deploy script that keeps data

cd /home/ubuntu

# Create permanent data folder
mkdir -p /home/ubuntu/student-care-data/students

# Backup existing data
if [ -d hikvission_student_care/data ]; then
  cp -r hikvission_student_care/data/database.db /home/ubuntu/student-care-data/ 2>/dev/null || true
  cp -r hikvission_student_care/data/students/* /home/ubuntu/student-care-data/students/ 2>/dev/null || true
fi

# Deploy new code
rm -rf hikvission_student_care
unzip -o student-care.zip -d hikvission_student_care
cd hikvission_student_care

# Remove old data folder and create symbolic link
rm -rf data
ln -s /home/ubuntu/student-care-data data

# Restart
pkill -f gunicorn
nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &

sleep 3
ps aux | grep gunicorn
echo "✅ Deploy complete! Data preserved at /home/ubuntu/student-care-data"
