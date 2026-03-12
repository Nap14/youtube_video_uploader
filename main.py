import os
import datetime
import json
import logging
import sys
import shutil
from send2trash import send2trash

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Конфігурація шляхів
ZOOM_DIR = r"D:\зум"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
SCHEDULE_FILE = os.path.join(BASE_DIR, "schedule.json")

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Scopes для YouTube Data API
SCOPES = ['https://www.googleapis.com/auth/youtube']

def get_authenticated_service():
    """Авторизація в YouTube API."""
    credentials = None
    # Якщо файл token.json існує, ми використовуємо його для отримання доступу
    if os.path.exists(TOKEN_FILE):
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Якщо немає (або вони недійсні), авторизуємо користувача
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            logging.info("Оновлюємо токен доступу...")
            credentials.refresh(Request())
        else:
            logging.info("Просимо користувача авторизуватись через браузер...")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            # Запускаємо локальний сервер для отримання відгуку після авторизації
            credentials = flow.run_local_server(port=0)
        
        # Зберігаємо токени для наступних запусків
        with open(TOKEN_FILE, 'w') as token:
            token.write(credentials.to_json())

    return build('youtube', 'v3', credentials=credentials)


def load_schedule():
    """Завантажує розклад з файлу JSON."""
    if not os.path.exists(SCHEDULE_FILE):
         logging.error(f"Файл розкладу {SCHEDULE_FILE} не знайдено.")
         return None
    with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
         return json.load(f)

def get_course_name_by_date(folder_date, schedule):
    """
    Визначає курс на основі дати та часу створення запису.
    Повертає словник з даними курсу (назва, шлях до обкладинки) або None.
    """
    # Назви днів тижня англійською в datetime.strftime('%A')
    day_name = folder_date.strftime('%A') 
    time_str = folder_date.strftime('%H:%M')
    
    # Шукаємо в розкладі за днем тижня і часом
    day_schedule = schedule.get(day_name, {})
    
    # Спочатку пробуємо точний час запису
    course = day_schedule.get(time_str)
    if course:
         return course
    
    # Якщо точний час не збігся, пробуємо знайти найближчий час до початку запису (зум може початись раніше/пізніше)
    for scheduled_time_str, course_name in day_schedule.items():
         scheduled_time = datetime.datetime.strptime(scheduled_time_str, '%H:%M').time()
         scheduled_datetime = datetime.datetime.combine(folder_date.date(), scheduled_time)
         
         # Допускаємо відхилення в 15 хвилин
         time_difference = abs((folder_date - scheduled_datetime).total_seconds())
         if time_difference <= 10 * 60:
             return course_name
    
    return None

def set_video_thumbnail(youtube, video_id, thumbnail_path):
    """
    Встановлює кастомну обкладику для відео.
    """
    if not thumbnail_path or not os.path.exists(thumbnail_path):
        logging.warning(f"Обкладинку не знайдено за шляхом: {thumbnail_path}. Залишаємо стандартну.")
        return
        
    logging.info(f"Встановлюємо обкладинку: {thumbnail_path}")
    try:
        request = youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        )
        request.execute()
        logging.info("Обкладинку успішно встановлено!")
    except Exception as e:
        logging.error(f"Помилка встановлення обкладинки: {e}")

def upload_video(youtube, file_path, title, description, category_id="27"):
    """
    Завантажує відео на YouTube.
    Значення category_id="27" відповідає Education.
    """
    logging.info(f"Спроба завантаження: {title}")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'unlisted', # Важливо: статус "Не для всіх"
            'selfDeclaredMadeForKids': False
        }
    }

    # Вказуємо файл і тип контенту
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/mp4')

    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info(f"Завантажено: {int(status.progress() * 100)}%")

    logging.info("Завантаження завершено!")
    video_id = response.get('id')
    return video_id, f"https://youtu.be/{video_id}"

def get_or_create_playlist(youtube, playlist_title):
    """Шукає плейлист за назвою, якщо немає - створює (Unlisted)."""
    logging.info(f"Шукаємо плейлист: '{playlist_title}'")
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            if item["snippet"]["title"] == playlist_title:
                logging.info(f"Знайдено плейлист: {playlist_title}")
                return item["id"]
        request = youtube.playlists().list_next(request, response)
        
    logging.info(f"Плейлист не знайдено. Створюємо: '{playlist_title}'")
    body = {
        "snippet": {
            "title": playlist_title,
            "description": f"Автоматичні записи занять для {playlist_title}"
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }
    response = youtube.playlists().insert(
        part="snippet,status",
        body=body
    ).execute()
    
    return response["id"]

def add_video_to_playlist(youtube, video_id, playlist_id):
    """Додає відео в плейлист."""
    logging.info(f"Додаємо відео {video_id} у плейлист...")
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            }
        }
    }
    youtube.playlistItems().insert(
        part="snippet",
        body=body
    ).execute()
    logging.info("Відео успішно додано у плейлист.")

def process_zoom_folders():
    """
    Основний цикл для пошуку та завантаження відео з Zoom.
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        logging.error(f"Файл {CLIENT_SECRETS_FILE} не знайдено. Ви не налаштували API.")
        return

    if not os.path.exists(ZOOM_DIR):
        logging.error(f"Папка зуму {ZOOM_DIR} не знайдена. Створіть її для тестування.")
        return

    schedule = load_schedule()
    if not schedule:
         return

    youtube = get_authenticated_service()

    # Отримуємо сьогоднішню дату для звіту
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    report_lines = []

    # Читаємо папки в D:\зум
    folders = [f for f in os.listdir(ZOOM_DIR) if os.path.isdir(os.path.join(ZOOM_DIR, f))]
    
    # Фільтруємо і завантажуємо відео
    for folder in folders:
         # Парсимо назву папки Zoom (зазвичай: YYYY-MM-DD HH.MM.SS)
         folder_path = os.path.join(ZOOM_DIR, folder)
         
         # Шукаємо mp4 файл в папці
         mp4_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
         if not mp4_files:
             logging.info(f"В папці '{folder}' не знайдено .mp4 файлів. Пропускаємо.")
             continue
         
         video_file = os.path.join(folder_path, mp4_files[0]) # Беремо перше відео
         
         # Спробуємо розібрати дату/час з назви папки "2024-03-12 15.00.00 ..."
         date_str = folder[:19] # "2024-03-12 15.00.00"
         try:
             folder_date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H.%M.%S')
         except ValueError:
             logging.warning(f"Не вдалося розпізнати дату з назви папки: '{folder}'")
             continue
         
         # Визначаємо курс
         course_data = get_course_name_by_date(folder_date, schedule)
         if not course_data:
             logging.warning(f"Курс не знайдено у розкладі для папки '{folder}'. Пропускаємо відео.")
             continue
         elif isinstance(course_data, str):
             # Підтримка старого формату schedule.json, коли значення було просто рядком
             course_name = course_data
             thumbnail_path = None
         else:
             # Новий формат, коли значення - це словник (dict)
             course_name = course_data.get("name", f"Невідомий курс ({date_str})")
             thumbnail_path = course_data.get("thumbnail")
         
         # Формуємо заголовок відео для YouTube
         video_title = f"{course_name} - Запис заняття від {folder_date.strftime('%d.%m.%Y')}"
         video_description = f"Автоматичне завантаження запису заняття: {course_name}"
         
         # Перевірка: чи ми вже завантажували це відео? (найпростіший спосіб - шукати .txt файл поруч з відео)
         uploaded_marker = os.path.join(folder_path, ".uploaded_to_youtube")
         if os.path.exists(uploaded_marker):
              logging.info(f"Відео в '{folder}' вже було завантажено раніше. Пропускаємо.")
              continue

         # Завантажуємо
         logging.info(f"Починаємо завантаження відео для: {course_name}")
         try:
             video_id, video_url = upload_video(youtube, video_file, video_title, video_description)
             
             # Встановлюємо обкладинку
             if thumbnail_path:
                 set_video_thumbnail(youtube, video_id, thumbnail_path)
             
             # Додаємо в плейлист
             playlist_id = get_or_create_playlist(youtube, course_name)
             add_video_to_playlist(youtube, video_id, playlist_id)
             
             # Пишемо у звіт
             report_lines.append(f"{folder_date.strftime('%H:%M')} | {course_name} | Посилання: {video_url}")
             
             # Все пройшло успішно. Переміщуємо папку в Кошик.
             logging.info(f"Відео завантажено успішно. Переміщуємо папку '{folder}' у Кошик...")
             try:
                 send2trash(folder_path)
                 logging.info(f"Папка {folder} відправлена у Кошик.")
             except Exception as trash_e:
                 logging.warning(f"Не вдалося відправити у કોшик: {trash_e}. Залишаємо папку.")
                 
         except Exception as e:
             logging.error(f"Помилка завантаження відео з '{folder}': {e}")
             report_lines.append(f"ПОМИЛКА | {course_name}: {e}")

    # Створюємо звіт
    if report_lines:
        report_path = os.path.join(BASE_DIR, f"Звіт_YouTube_{today}.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"--- Звіт завантажених відео за {today} ---\n\n")
            f.write("\n".join(report_lines))
        logging.info(f"Готово! Звіт збережено у файл: {report_path}")
    else:
        logging.info("Нових відео для завантаження не знайдено.")

if __name__ == '__main__':
    process_zoom_folders()
