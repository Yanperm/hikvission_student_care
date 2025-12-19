#!/bin/bash

echo "========================================"
echo "  Student Care - ติดตั้งระบบอัตโนมัติ"
echo "========================================"
echo ""

# Check Python
echo "[1/4] ตรวจสอบ Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ ไม่พบ Python3 กรุณาติดตั้งก่อน"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi
echo "✅ พบ Python แล้ว"

# Install packages
echo ""
echo "[2/4] ติดตั้ง Python packages..."
pip3 install Flask opencv-python-headless Pillow requests flask-cors numpy -q
if [ $? -ne 0 ]; then
    echo "❌ ติดตั้ง packages ล้มเหลว"
    exit 1
fi
echo "✅ ติดตั้ง packages สำเร็จ"

# Create directories
echo ""
echo "[3/4] สร้างโฟลเดอร์ที่จำเป็น..."
mkdir -p data/students logs
echo "✅ สร้างโฟลเดอร์สำเร็จ"

# Create .env
echo ""
echo "[4/4] สร้างไฟล์ config..."
if [ ! -f .env ]; then
    echo "CLOUD_API_URL=http://43.210.87.220:8080" > .env
    echo "✅ สร้างไฟล์ .env สำเร็จ"
else
    echo "⚠️  ไฟล์ .env มีอยู่แล้ว"
fi

echo ""
echo "========================================"
echo "  ✅ ติดตั้งเสร็จสมบูรณ์!"
echo "========================================"
echo ""
echo "วิธีใช้งาน:"
echo "  1. รันระบบ: ./start.sh"
echo "  2. เปิดเว็บ: http://localhost:5000"
echo ""
