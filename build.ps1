# Build script for Zoom Video Automation

Write-Host "Cleaning up previous builds..." -ForegroundColor Cyan
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

Write-Host "Building GUI Application..." -ForegroundColor Cyan
pyinstaller --onefile --noconsole --name "ZoomAutomation_GUI" --clean `
    --icon "assets/icons/main_app_icon.ico" `
    --collect-all googleapiclient `
    --collect-all google_auth_oauthlib `
    --collect-all customtkinter `
    --hidden-import darkdetect `
    main.py

Write-Host "Building CLI Application..." -ForegroundColor Cyan
pyinstaller --onefile --console --name "ZoomAutomation_CLI" --clean `
    --icon "assets/icons/main_app_icon.ico" `
    --collect-all googleapiclient `
    --collect-all google_auth_oauthlib `
    --collect-all customtkinter `
    --hidden-import darkdetect `
    cli.py

Write-Host "`nBuild Completed! Check the 'dist' folder for executables." -ForegroundColor Green
