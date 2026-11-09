# Zoom Video Automation 🚀

Інструмент для автоматизації повного циклу обробки записів Zoom: пошук нових відео, пакетне завантаження на YouTube, організація плейлистів, автоматична синхронізація з уроками SendPulse LMS та формування звітів.

---

## 🔀 Оберіть гілку для вашої операційної системи

Проєкт розділено на дві спеціалізовані, повністю оптимізовані гілки:

### 1. 🪟 Версія для Windows — гілка [`windows`](https://github.com/Nap14/youtube_video_uploader/tree/windows)
* **Переваги**: інтеграція з системним треєм Windows, підтримка пакетних файлів запуску (`Run.bat`, `RunShell.bat`), скрипт створення автономного `.exe` (`BuildEXE.bat`), відслідковування декількох відео на один урок (`Ч1`, `Ч2`).
* **Швидкий старт на Windows**:
  ```powershell
  git checkout windows
  ```
  Запустіть файл **`Run.bat`** (він автоматично налаштує віртуальне оточення `venv` та запустить додаток).
* Детальна інструкція: дивіться `README.md` у гілці `windows`.

---

### 2. 🍏 Версія для macOS — гілка [`macos`](https://github.com/Nap14/youtube_video_uploader/tree/macos)
* **Переваги**: повна сумісність з macOS (Big Sur / Monterey / Ventura / Sonoma / Sequoia), потокобезпечна взаємодія з інтерфейсом Tkinter через `queue.Queue`, готові bash-скрипти (`run.sh`), компіляція у повноцінний бандл `ZoomAutomation_GUI.app` (`build_mac.sh`).
* **Швидкий старт на macOS**:
  ```bash
  git checkout macos
  chmod +x run.sh
  ./run.sh
  ```
* Детальна інструкція: дивіться `README.md` у гілці `macos`.

---

## ⚙️ Загальні налаштування перед першим запуском

Для роботи додатку на будь-якій системі необхідна папка `configs/` з такими файлами:

1. **`configs/client_secret.json` (YouTube API)**:
   - Перейдіть у [Google Cloud Console](https://console.cloud.google.com/).
   - Увімкніть **YouTube Data API v3**.
   - Створіть облікові дані: **OAuth 2.0 Client ID** (тип «Desktop app»).
   - Завантажте JSON-файл та збережіть його як `configs/client_secret.json`.
   - При першому запуску відкриється вікно браузера для одноразового підтвердження входу в акаунт Google.

2. **`configs/config.json`**:
   ```json
   {
       "ZOOM_DIR": "Шлях_до_папки_записів_Zoom",
       "LMS_TOKEN": "Bearer_токен_SendPulse",
       "SCHOOL_ID": "ID_школи_SendPulse",
       "THEME": "Dark"
   }
   ```

3. **`configs/schedule.json`**:
   Розклад занять для автоматичного зіставлення часу запису Zoom із назвою курсу (назви днів тижня англійською):
   ```json
   {
     "Monday": {
       "18:00": {
         "name": "Python Basic",
         "thumbnail": "python.jpg",
         "lms_course_id": "12345",
         "duration": 60
       }
     }
   }
   ```

4. **Обкладинки (`thumbnails/`)**:
   Зображення-обкладинки курсів розміщуються у папці `thumbnails/` (наприклад, `thumbnails/python.jpg`).
