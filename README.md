# Zoom Video Automation 🚀 (Версія для macOS)

Автоматизація повного циклу обробки записів Zoom на **macOS**: пошук записів, пакетне завантаження на YouTube, організація плейлистів та автоматична прив'язка до уроків SendPulse LMS.

---

## 💻 Системні вимоги для macOS

1. **macOS**: 11.0 (Big Sur) або новіша.
2. **Python**: 3.10 - 3.13.
   > **Важливо для macOS (Homebrew Python):** Якщо ви використовуєте Python, встановлений через Homebrew, переконайтеся, що встановлено Tkinter:
   > ```bash
   > brew install python-tk@3.12   # або ваша версія python
   > ```
3. **Права доступу macOS (Security & Privacy)**:
   - Додатку потрібен доступ до папки з записами Zoom (зазвичай `~/Documents/Zoom`). При першому запуску macOS може запитати дозвіл на доступ до файлів папки «Документи» — натисніть **«Дозволити»**.

---

## 🚀 Швидкий запуск

### 1. Підготовка конфігурацій (папка `configs/`)
* **`configs/client_secret.json`**: Завантажте з [Google Cloud Console](https://console.cloud.google.com/) (OAuth 2.0 Client ID, Desktop App).
* **`configs/config.json`**: Вкажіть шлях до папки Zoom (наприклад, `/Users/ім'я/Documents/Zoom`), `LMS_TOKEN` та `SCHOOL_ID`.
* **`configs/schedule.json`**: Налаштуйте розклад уроків (день тижня англійською та час).

### 2. Запуск через скрипт `run.sh`
У Терміналі перейдіть до папки проєкту та виконайте:
```bash
chmod +x run.sh
./run.sh
```
*Скрипт автоматично створить віртуальне оточення `venv` під macOS, встановить усі залежності з `requirements.txt` і запустить графічний інтерфейс.*

### Запуск CLI версії (Термінал):
```bash
source venv/bin/activate
python3 cli.py
```

---

## 🛠 Збірка в окремий macOS додаток (.app)

Для створення автономного бандлу додатка:
```bash
chmod +x build_mac.sh
./build_mac.sh
```
Після завершення у папці `dist/` будуть створені:
* **`dist/ZoomAutomation_GUI.app`** — повноцінний додаток для macOS.
* **`dist/ZoomAutomation_CLI`** — бінарник для термінала.

> **Порада щодо Gatekeeper macOS:**
> Якщо при відкритті `.app` з'являється повідомлення «Програму заблоковано, оскільки розробник невідомий», зніміть карантинний прапорець:
> ```bash
> xattr -cr dist/ZoomAutomation_GUI.app
> ```

---

## 📂 Структура проєкту (macOS)

```text
zoom_uploader/
├── assets/             # Графіка та іконки інтерфейсу
├── configs/            # client_secret.json, config.json, schedule.json
├── reports/            # Звіти та логи синхронізації (CSV, TXT)
├── src/                # Вихідний код додатку
├── thumbnails/         # Обкладинки для курсів
├── main.py             # Точка входу GUI
├── cli.py              # Точка входу CLI
├── run.sh              # Скрипт запуску для macOS
└── build_mac.sh        # Скрипт збірки .app бандлу
```
