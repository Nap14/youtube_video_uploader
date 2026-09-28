#!/bin/bash

# Переходимо в директорію скрипта
cd "$(dirname "$0")"

echo "[INFO] Checking environment..."

# Перевірка venv (якщо папку venv перенесли з Windows або її немає)
if [ ! -f "venv/bin/activate" ]; then
    echo "[INFO] macOS virtual environment not found or invalid. Creating one..."
    rm -rf venv
    python3 -m venv venv
    
    echo "[INFO] Installing requirements..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
    if ! python3 -c "import pydantic" &> /dev/null; then
        echo "[INFO] Installing missing dependencies..."
        pip install -r requirements.txt
    fi
fi

echo "[INFO] Starting YouTube Uploader..."
python3 main.py
