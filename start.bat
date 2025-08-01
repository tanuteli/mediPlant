@echo off
echo ========================================
echo      MediPlant Webapp Setup
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Setting up the application...

REM Install required packages
echo Installing dependencies...
pip install -r requirements.txt

REM Initialize database if it doesn't exist
if not exist "database.db" (
    echo Initializing database...
    python -c "from app import init_db; init_db()"
)

REM Create sample data
echo Creating sample data...
python create_sample_data.py

REM Start the application
echo Starting MediPlant webapp...
echo.
echo ========================================
echo   Application will start on:
echo   http://localhost:5000
echo ========================================
echo.
echo Demo Login Credentials:
echo   Admin: admin / admin123
echo   User:  demo / demo123
echo ========================================
echo.
echo Admin Panel: http://localhost:5000/admin
echo Main Site:   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
