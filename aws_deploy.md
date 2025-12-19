# Deploy บน AWS

## วิธีที่ 1: AWS Elastic Beanstalk (แนะนำ)

### ติดตั้ง EB CLI
```bash
pip install awsebcli
```

### Deploy
```bash
# 1. เริ่มต้น Elastic Beanstalk
eb init -p python-3.9 hikvision-student-care --region ap-southeast-1

# 2. สร้าง environment และ deploy
eb create hikvision-prod

# 3. เปิดแอปพลิเคชัน
eb open

# 4. ดู logs
eb logs

# 5. Update แอปพลิเคชัน
eb deploy
```

### ตั้งค่า Environment Variables
```bash
eb setenv CAMERA_IP=192.168.1.64 \
  CAMERA_USERNAME=admin \
  CAMERA_PASSWORD=your_password \
  FLASK_SECRET_KEY=your_secret_key \
  ADMIN_USERNAME=admin \
  ADMIN_PASSWORD=admin123
```

---

## วิธีที่ 2: AWS EC2

### 1. สร้าง EC2 Instance
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.medium (แนะนำ) หรือ t3.large
- Security Group: เปิด port 22 (SSH), 80 (HTTP), 5000

### 2. เชื่อมต่อและติดตั้ง
```bash
# SSH เข้า EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# ติดตั้ง Python และ dependencies
sudo apt install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install -y libopencv-dev python3-opencv cmake

# Clone โปรเจค
git clone https://github.com/Yanperm/hikvission_student_care.git
cd hikvission_student_care

# ติดตั้ง Python packages
pip3 install -r requirements.txt

# สร้าง .env file
cp .env.example .env
nano .env  # แก้ไขค่าต่างๆ

# รันแอปพลิเคชัน
python3 main.py
```

### 3. ตั้งค่า Systemd Service (รันอัตโนมัติ)
```bash
sudo nano /etc/systemd/system/hikvision.service
```

เพิ่มเนื้อหา:
```ini
[Unit]
Description=Hikvision Student Care
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/hikvission_student_care
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

เริ่มใช้งาน:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hikvision
sudo systemctl start hikvision
sudo systemctl status hikvision
```

### 4. ติดตั้ง Nginx (Reverse Proxy)
```bash
sudo apt install -y nginx

sudo nano /etc/nginx/sites-available/hikvision
```

เพิ่มเนื้อหา:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /home/ubuntu/hikvission_student_care/static;
    }
}
```

เปิดใช้งาน:
```bash
sudo ln -s /etc/nginx/sites-available/hikvision /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## วิธีที่ 3: AWS ECS (Docker)

### 1. Build และ Push Docker Image
```bash
# Build image
docker build -t hikvision-student-care .

# Tag image
docker tag hikvision-student-care:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com/hikvision-student-care:latest

# Login to ECR
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com

# Push image
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-1.amazonaws.com/hikvision-student-care:latest
```

### 2. สร้าง ECS Task Definition และ Service ผ่าน AWS Console

---

## ค่าใช้จ่ายโดยประมาณ (ap-southeast-1)

| วิธี | ราคา/เดือน | เหมาะกับ |
|------|-----------|---------|
| EC2 t3.medium | ~$30 | Production |
| EC2 t3.small | ~$15 | Development |
| Elastic Beanstalk | ~$30-50 | ง่าย Auto-scale |
| ECS Fargate | ~$40-60 | Container, Scale ดี |

---

## Database Options

### SQLite (ปัจจุบัน)
- ใช้ได้ดีสำหรับ single instance
- ไม่ต้องตั้งค่าเพิ่ม

### AWS RDS (แนะนำสำหรับ Production)
```bash
# ติดตั้ง PostgreSQL driver
pip install psycopg2-binary

# แก้ไข database_manager.py ให้ใช้ PostgreSQL
```

### AWS DynamoDB (NoSQL)
- เหมาะกับ Serverless
- ต้องแก้โค้ดมากกว่า

---

## Storage Options

### Local Storage (ปัจจุบัน)
- ใช้ได้กับ EC2
- ข้อมูลอยู่บน instance

### AWS S3
```bash
# ติดตั้ง boto3
pip install boto3

# อัปโหลดรูปไปที่ S3 แทน local
```

---

## Monitoring

### CloudWatch
```bash
# ติดตั้ง CloudWatch agent บน EC2
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

---

## Security Best Practices

1. ใช้ IAM Roles แทน Access Keys
2. เปิด HTTPS ด้วย AWS Certificate Manager
3. ใช้ Security Groups จำกัด IP
4. เก็บ secrets ใน AWS Secrets Manager
5. Enable CloudWatch Logs
6. ใช้ VPC สำหรับ private network

---

## Troubleshooting

### ปัญหา: face_recognition ติดตั้งไม่ได้
```bash
# ติดตั้ง dlib ก่อน
sudo apt install -y cmake
pip install dlib
pip install face_recognition
```

### ปัญหา: OpenCV import error
```bash
sudo apt install -y libgl1-mesa-glx
```

### ปัญหา: Memory ไม่พอ
- เพิ่ม swap space หรือ
- Upgrade instance type
