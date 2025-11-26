@echo off
echo ============================================
echo Local STT Setup
echo ============================================
echo.

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment!
    echo Make sure Python 3.10+ is installed.
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Setup complete!
echo ============================================
echo.
echo To run the app:
echo   1. Activate venv: venv\Scripts\activate
echo   2. Run: python main.py
echo.
echo Or build the executable:
echo   python build.py
echo.
pause
