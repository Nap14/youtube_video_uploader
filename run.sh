#!/bin/bash

# Переходимо в директорію скрипта
cd "$(dirname "$0")"

echo "[INFO] Checking environment..."

# Перевірка venv
if [ ! -d "venv" ]; then
    echo "[INFO] Virtual environment not found. Creating one..."
    python3 -m venv venv
    
    echo "[INFO] Installing requirements..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "[INFO] Starting YouTube Uploader..."
python3 main.py
