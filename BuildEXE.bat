@echo off
echo [INFO] Building EXE...
call venv\Scripts\activate.bat
pip install pyinstaller
pyinstaller --onefile --name "ZoomUploader" main.py
echo [INFO] Done! The EXE is in the 'dist' folder.
pause
