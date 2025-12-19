@echo off
echo ===================================
echo   Building Voice Control App EXE
echo ===================================

:: Check if python is installed
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3 and try again.
    pause
    exit /b 1
)

echo.
echo Found Python installation.
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo.
echo Activating virtual environment...
call venv\\Scripts\\activate

echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ===================================
echo      Running PyInstaller
echo ===================================
echo.

pyinstaller --name VoiceControlApp --onefile --windowed --clean --noconfirm src/main_app.py

echo.
echo ===================================
echo       Build process complete!
echo ===================================
echo.
echo You can find the single-file executable in the 'dist' folder.
echo.

deactivate
pause
