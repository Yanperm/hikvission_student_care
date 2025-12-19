@echo off
chcp 65001 >nul
cls

echo ==========================================
echo   📤 Push to GitHub
echo   © 2025 SOFTUBON CO.,LTD.
echo ==========================================
echo.

echo 📝 Adding all files...
git add .

echo.
echo 💬 Committing changes...
git commit -m "Update: Complete Student Care System with 21 features"

echo.
echo 📤 Pushing to GitHub...
git push origin main

echo.
if %errorlevel% equ 0 (
    echo ✅ Successfully pushed to GitHub!
    echo 🌐 https://github.com/Yanperm/hikvission_student_care
) else (
    echo ❌ Failed to push. Please check your connection.
)

echo.
pause
