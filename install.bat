@echo off
chcp 65001 >nul
cls

echo ==========================================
echo   Student Care System - Auto Installer
echo   © 2025 SOFTUBON CO.,LTD.
echo ==========================================
echo.

echo 🔍 Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.7+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python found: %PYTHON_VERSION%
echo.

echo 📦 Installing dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully!
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo 📁 Creating data directory...
if not exist "data\students" mkdir data\students
echo ✅ Data directory created!

echo.
echo ==========================================
echo   ✅ Installation Complete!
echo ==========================================
echo.
echo 🚀 To start the system, run:
echo    python local_app.py
echo.
echo 🌐 Then open browser:
echo    http://localhost:5000
echo.
echo ☁️  Cloud Sync: Automatic
echo ==========================================
echo.
pause
