@echo off
setlocal
cd /d "%~dp0"

echo [INFO] Checking environment...

:: Check if venv exists
if not exist "venv" (
    echo [INFO] Virtual environment not found. Creating one...
    py -3.13 -m venv venv
    if errorlevel 1 (
        echo [WARNING] Python 3.13 not found via 'py'. Trying 'python'...
        python -m venv venv
    )
    
    echo [INFO] Installing requirements...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo [INFO] Starting YouTube Uploader...
python main.py
pause
