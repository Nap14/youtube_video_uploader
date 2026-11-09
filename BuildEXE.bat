@echo off
echo [INFO] Building EXE for Windows...
call venv\Scripts\activate.bat
pip install pyinstaller
pyinstaller --onefile --noconsole --name "ZoomUploader" --clean ^
    --collect-all customtkinter ^
    --collect-all googleapiclient ^
    --collect-all google_auth_oauthlib ^
    --collect-all pydantic ^
    --hidden-import darkdetect ^
    --add-data "assets;assets" ^
    main.py

echo [INFO] Preparing runtime folders in dist...
if not exist "dist\configs" mkdir dist\configs
if not exist "dist\thumbnails" mkdir dist\thumbnails
if not exist "dist\reports" mkdir dist\reports
xcopy /E /I /Y assets dist\assets >nul 2>&1

echo [INFO] Done! Executable is ready at: dist\ZoomUploader.exe
pause
