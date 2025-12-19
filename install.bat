@echo off
chcp 65001 >nul
echo ========================================
echo   Student Care - ติดตั้งระบบอัตโนมัติ
echo ========================================
echo.

echo [1/4] ตรวจสอบ Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ไม่พบ Python กรุณาติดตั้ง Python 3.7+ ก่อน
    echo ดาวน์โหลดได้ที่: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ พบ Python แล้ว

echo.
echo [2/4] ติดตั้ง Python packages...
pip install Flask opencv-python-headless Pillow requests flask-cors numpy -q
if errorlevel 1 (
    echo ❌ ติดตั้ง packages ล้มเหลว
    pause
    exit /b 1
)
echo ✅ ติดตั้ง packages สำเร็จ

echo.
echo [3/4] สร้างโฟลเดอร์ที่จำเป็น...
if not exist "data" mkdir data
if not exist "data\students" mkdir data\students
if not exist "logs" mkdir logs
echo ✅ สร้างโฟลเดอร์สำเร็จ

echo.
echo [4/4] สร้างไฟล์ config...
if not exist ".env" (
    echo CLOUD_API_URL=http://43.210.87.220:8080 > .env
    echo ✅ สร้างไฟล์ .env สำเร็จ
) else (
    echo ⚠️  ไฟล์ .env มีอยู่แล้ว
)

echo.
echo ========================================
echo   ✅ ติดตั้งเสร็จสมบูรณ์!
echo ========================================
echo.
echo วิธีใช้งาน:
echo   1. รันระบบ: คลิก start.bat
echo   2. เปิดเว็บ: http://localhost:5000
echo.
pause
