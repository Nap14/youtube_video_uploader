# Zoom Video Automation 🚀

Інструмент для автоматизації повного циклу обробки записів Zoom: пошук, завантаження на YouTube, організація плейлистів та прив'язка до курсів SendPulse LMS.

## Можливості

- 📂 **Автопошук**: виявлення нових `.mp4` записів у робочій папці Zoom.
- 📅 **Розумний розклад**: зіставлення дати й часу запису з курсом, плейлистом і обкладинкою.
- 📺 **YouTube API**: завантаження відео з доступом «Unlisted» та додавання до плейлиста курсу.
- 🎓 **SendPulse LMS**: синхронізація та автоматичне прикріплення посилань на відео до уроків.
- ⏰ **Фоновий режим**: вбудований планувальник завдань та робота у системному треї (GUI).
- 🗑️ **Безпека й звіти**: автоматичне перенесення оброблених папок у Кошик і створення звітів (TXT/CSV).

## Швидкий старт

### 1. YouTube API (`configs/client_secret.json`)
1. У [Google Cloud Console](https://console.cloud.google.com/) створіть проєкт та увімкніть **YouTube Data API v3**.
2. Створіть **OAuth client ID** (тип «Desktop app»), завантажте JSON-файл і збережіть як `configs/client_secret.json`.
3. При першому запуску відкриється браузер для одноразової авторизації через Google.

### 2. Розклад курсів (`configs/schedule.json`)
Зіставте день тижня (англійською) і час початку уроку з параметрами курсу (обкладинки з `thumbnails/`):
```json
{
  "Monday": {
    "19:00": {
      "name": "Unity Pro",
      "thumbnail": "unity.jpg",
      "lms_course_id": "35014"
    }
  }
}
```

### 3. Токен LMS (`configs/config.json`)
Для оновлення уроків на платформі вкажіть Bearer-токен (кабінет SendPulse → DevTools `F12` → вкладка Network → заголовок `Authorization: Bearer <токен>` будь-якого API-запиту):
```json
{
  "LMS_TOKEN": "ВАШ_BEARER_ТОКЕН",
  "SCHOOL_ID": "18828",
  "REPORTS_DIR": "reports"
}
```

## Запуск

| Платформа | GUI | CLI | З вихідного коду |
|---|---|---|---|
| **Windows** | `Run.bat` або `ZoomAutomation_GUI.exe` | `RunShell.bat` або `ZoomAutomation_CLI.exe` | `python main.py` / `python cli.py` |
| **macOS / Linux** | `./run.sh` або `open ZoomAutomation_GUI.app` | `./dist/ZoomAutomation_CLI` | `python3 main.py` / `python3 cli.py` |

## Збірка

Для компіляції автономних виконуваних файлів:
- **macOS**: виконайте `./build_mac.sh` — формує бандл `ZoomAutomation_GUI.app` та бінарник `ZoomAutomation_CLI` у каталозі `dist/`.
- **Windows**: запустіть `BuildEXE.bat` — компілює автономний `.exe` за допомогою PyInstaller.

## Структура проєкту

```text
zoom_uploader/
├── assets/          # Графіка та іконки інтерфейсу
├── configs/         # client_secret.json, config.json, schedule.json
├── reports/         # Логи та звіти завантажень (TXT, CSV)
├── src/             # Вихідний код (core, gui, services)
├── thumbnails/      # Зображення-обкладинки для курсів
├── main.py / cli.py # Точки входу GUI та CLI
├── Run.bat / run.sh # Скрипти запуску (Windows / macOS)
└── build_mac.sh     # Скрипти збірки (macOS / Windows BuildEXE.bat)
```
