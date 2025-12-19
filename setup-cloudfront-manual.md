# Setup CloudFront - คู่มือทำเอง (ง่ายกว่า)

## ขั้นตอนที่ 1: Request SSL Certificate

1. ไปที่ **AWS Console** → **Certificate Manager (ACM)**
2. **Region: US East (N. Virginia) us-east-1** ⚠️ สำคัญ! ต้องเป็น us-east-1
3. คลิก **Request certificate**
4. **Certificate type:** Request a public certificate
5. **Domain names:**
   - `yourdomain.com`
   - `www.yourdomain.com`
   - `*.yourdomain.com`
6. **Validation method:** DNS validation
7. คลิก **Request**
8. คลิก **Create records in Route 53** (ถ้าใช้ Route 53)
   - หรือ copy CNAME records ไปใส่ที่ Domain Provider
9. รอ 5-10 นาที จนสถานะเป็น **Issued**

---

## ขั้นตอนที่ 2: Create CloudFront Distribution

1. ไปที่ **AWS Console** → **CloudFront**
2. คลิก **Create Distribution**

### Origin Settings:
```
Origin domain: 43.210.87.220
Protocol: HTTP only
HTTP port: 5000
Name: EC2-StudentCare
```

### Default cache behavior:
```
Path pattern: Default (*)
Compress objects automatically: Yes
Viewer protocol policy: Redirect HTTP to HTTPS
Allowed HTTP methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
Cache policy: CachingDisabled
Origin request policy: AllViewer
```

### Settings:
```
Price class: Use North America, Europe, Asia, Middle East, and Africa
Alternate domain names (CNAMEs):
  - yourdomain.com
  - www.yourdomain.com

Custom SSL certificate: เลือก certificate ที่สร้างไว้

Default root object: (ว่างไว้)
```

3. คลิก **Create distribution**
4. รอ 5-10 นาที จนสถานะเป็น **Enabled**
5. Copy **Distribution domain name** (เช่น d1234abcd.cloudfront.net)

---

## ขั้นตอนที่ 3: ตั้งค่า DNS

ไปที่ **Domain Provider** (Namecheap/GoDaddy/CloudFlare):

### เพิ่ม CNAME Record:
```
Type: CNAME
Name: www
Value: d1234abcd.cloudfront.net (ใส่ CloudFront domain ที่ copy มา)
TTL: Automatic
```

### เพิ่ม A Record (ถ้าทำได้):
```
Type: A
Name: @
Value: ใช้ ALIAS ชี้ไปที่ CloudFront
```

**หรือ redirect @ ไป www:**
```
Type: URL Redirect
Name: @
Value: https://www.yourdomain.com
```

---

## ขั้นตอนที่ 4: ทดสอบ

รอ 15-30 นาที แล้วเปิด:
```
https://www.yourdomain.com
https://yourdomain.com
```

---

## 🔧 Troubleshooting

### ถ้าเจอ 502 Bad Gateway:
```bash
# SSH เข้า EC2
ssh -i "studentcare.pem" ubuntu@43.210.87.220

# เช็คว่า gunicorn รันอยู่
ps aux | grep gunicorn

# ถ้าไม่รัน ให้ start ใหม่
cd /home/ubuntu/hikvission_student_care
nohup python3 -m gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 local_app:app > student-care.log 2>&1 &
```

### ถ้าเจอ SSL Error:
- เช็คว่า Certificate สถานะเป็น **Issued**
- เช็คว่าเลือก Certificate ที่ถูกต้องใน CloudFront
- เช็คว่า Certificate อยู่ใน **us-east-1** region

---

## ✅ เสร็จแล้ว!

ตอนนี้ระบบของคุณ:
- ⚡ เร็วขึ้นด้วย CDN
- 🔒 มี HTTPS (SSL)
- 🌍 เข้าถึงได้ทั่วโลก
- 🛡️ ป้องกัน DDoS

**Architecture:**
```
User → CloudFront (CDN + SSL) → EC2:5000 → RDS PostgreSQL
```
