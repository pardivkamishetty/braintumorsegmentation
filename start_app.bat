@echo off
echo ========================================
echo Brain Tumor Detection App Startup
echo ========================================
echo.

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists and has proper structure
if not exist ".venv\Scripts\python.exe" (
    echo Creating new virtual environment...
    rmdir /s /q .venv 2>nul
    py -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment (try multiple methods)
echo Activating virtual environment...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist ".venv\Scripts\Activate.ps1" (
    powershell -ExecutionPolicy Bypass -File .venv\Scripts\Activate.ps1
) else (
    echo Warning: Could not activate virtual environment, using system Python
    echo This may work if packages are installed globally
)

REM Install/update requirements
echo Installing/updating requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: Some packages may have failed to install
    echo Trying with system Python...
    py -m pip install -r requirements.txt
)

echo.
echo ========================================
echo Starting Brain Tumor Detection App...
echo ========================================
echo.
echo App will be available at: http://localhost:8501
echo Press Ctrl+C to stop the application
echo.

REM Start Streamlit app
streamlit run finale.py
if errorlevel 1 (
    echo Error: Failed to start Streamlit
    echo Trying alternative method...
    py -m streamlit run finale.py
)

pause
