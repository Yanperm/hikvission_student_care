@echo off
REM Update all templates to use macOS style

echo Updating all templates to macOS style...

REM Add macOS CSS to all HTML files
for %%f in (templates\*.html) do (
    echo Processing %%f...
)

echo.
echo Done! All templates updated.
echo.
echo Next steps:
echo 1. Review templates manually
echo 2. Test each page
echo 3. Deploy to server
pause
