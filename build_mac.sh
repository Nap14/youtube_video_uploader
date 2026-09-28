#!/bin/bash
set -e

# Переходимо в директорію скрипта
cd "$(dirname "$0")"

echo "=========================================="
echo "  Збірка Zoom Video Automation для macOS  "
echo "=========================================="

# 1. Перевірка та ініціалізація віртуального середовища
if [ ! -f "venv/bin/activate" ]; then
    echo "[1/4] Створення macOS віртуального оточення (venv)..."
    rm -rf venv
    python3 -m venv venv
fi

echo "[1/4] Активація віртуального оточення та встановлення залежностей..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Переконуємось, що pyinstaller встановлено
if ! command -v pyinstaller &> /dev/null; then
    echo "[INFO] Встановлення PyInstaller..."
    pip install pyinstaller
fi

# 2. Очищення старих збірок
echo "[2/4] Очищення попередніх збірок (build, dist)..."
rm -rf build
# Зберігаємо Windows .exe якщо вони є, видаляємо попередні mac-артефакти
rm -rf dist/ZoomAutomation_GUI.app dist/ZoomAutomation_GUI dist/ZoomAutomation_CLI ZoomAutomation_GUI.app

# 3. Збірка GUI версії (.app бандл для macOS)
echo "[3/4] Збірка GUI додатку (ZoomAutomation_GUI.app)..."
pyinstaller --windowed --name "ZoomAutomation_GUI" --clean \
    --collect-all googleapiclient \
    --collect-all google_auth_oauthlib \
    --collect-all customtkinter \
    --collect-all pydantic \
    --hidden-import darkdetect \
    --add-data "assets:assets" \
    main.py

# 4. Збірка CLI версії (консольний виконуваний файл)
echo "[4/4] Збірка CLI додатку (ZoomAutomation_CLI)..."
pyinstaller --onefile --console --name "ZoomAutomation_CLI" --clean \
    --collect-all googleapiclient \
    --collect-all google_auth_oauthlib \
    --collect-all customtkinter \
    --collect-all pydantic \
    --hidden-import darkdetect \
    --add-data "assets:assets" \
    cli.py

# Підготовка файлів у dist/
echo "[INFO] Підготовка середовища в dist/..."
mkdir -p dist/configs dist/reports dist/thumbnails
cp configs/* dist/configs/ 2>/dev/null || true
cp thumbnails/* dist/thumbnails/ 2>/dev/null || true
cp -r assets dist/ 2>/dev/null || true
cp -r dist/ZoomAutomation_GUI.app ./ 2>/dev/null || true
cp dist/ZoomAutomation_CLI ./ 2>/dev/null || true

echo ""
echo "=========================================="
echo "  Збірка успішно завершена! 🎉            "
echo "=========================================="
echo "Результати у папці 'dist/':"
echo "  - dist/ZoomAutomation_GUI.app  (Графічний додаток для macOS)"
echo "  - dist/ZoomAutomation_CLI      (Консольна версія для Терміналу)"
echo ""
echo "Для запуску GUI додатку:"
echo "  open dist/ZoomAutomation_GUI.app"
echo ""
echo "Для запуску CLI:"
echo "  ./dist/ZoomAutomation_CLI"
echo "=========================================="
