@echo off
REM Finance Tracker - Quick Start Script
REM This script installs dependencies and runs the Flask web app

echo.
echo ========================================
echo   Finance Tracker Web App
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Starting Finance Tracker Web App...
echo ========================================
echo.
echo Open your browser and go to:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
pause
