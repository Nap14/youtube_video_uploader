import os
import logging

from send2trash import send2trash

from src.authenticated_service import Oauth2Service
from src.file_service import find_video
from src.playlist_service import PlaylistController
from src.report import create_report
from src.schedule import get_course_name_by_date, load_schedule, get_date_from_file_name
from src.video_service import VideoService
from src.config import Config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
SCHEDULE_FILE = os.path.join(BASE_DIR, "schedule.json")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_zoom_folders():
    """
    Основний цикл для пошуку та завантаження відео з Zoom.
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        logging.error(f"Файл {CLIENT_SECRETS_FILE} не знайдено. Ви не налаштували API.")
        return

    # Ініціалізація конфігурації
    config = Config(CONFIG_FILE, logging)
    zoom_dir = config.get_zoom_dir()

    if not zoom_dir or not os.path.exists(zoom_dir):
        logging.error(f"Папка зуму {zoom_dir} не знайдена.")
        return

    schedule = load_schedule(SCHEDULE_FILE, logging)
    if not schedule:
        return

    oauth2 = Oauth2Service(logging)
    youtube = oauth2.get_youtube_service(TOKEN_FILE, CLIENT_SECRETS_FILE)

    report_lines = []

    # Читаємо папки в ZOOM_DIR
    folders = [f for f in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, f))]
    
    for folder in folders:
         folder_path = os.path.join(zoom_dir, folder)
         
         mp4_files = find_video(folder_path)
         if not mp4_files:
             logging.info(f"В папці '{folder}' не знайдено .mp4 файлів. Пропускаємо.")
             continue
         
         video_file = os.path.join(folder_path, mp4_files[0])
         
         folder_date = get_date_from_file_name(folder)
         if not folder_date:
            logging.warning(f"Не вдалося розпізнати дату з назви папки: '{folder}'")
            continue

         course_data = get_course_name_by_date(folder_date, schedule)
         if not course_data:
             logging.warning(f"Курс не знайдено у розкладі для папки '{folder}'. Пропускаємо відео.")
             continue
         elif isinstance(course_data, str):
             course_name = course_data
             thumbnail_path = None
         else:
             course_name = course_data.get("name", f"Невідомий курс")
             thumbnail_path = course_data.get("thumbnail")
             if thumbnail_path and not os.path.isabs(thumbnail_path):
                 thumbnail_path = os.path.join(BASE_DIR, "thumbnails", thumbnail_path)
         
         video_title = f"{course_name} - Запис заняття від {folder_date.strftime('%d.%m.%Y')}"
         video_description = f"Автоматичне завантаження запису заняття: {course_name}"
         
         uploaded_marker = os.path.join(folder_path, ".uploaded_to_youtube")
         if os.path.exists(uploaded_marker):
              logging.info(f"Відео в '{folder}' вже було завантажено раніше. Пропускаємо.")
              continue

         logging.info(f"Починаємо завантаження відео для: {course_name}")
         try:
             video_service = VideoService(youtube, logging)
             video_id, video_url = video_service.upload_video(video_file, video_title, video_description)
             
             if thumbnail_path:
                 video_service.set_video_thumbnail(video_id, thumbnail_path)
             
             playlist_service = PlaylistController(youtube, logging)
             playlist_service.add_video_to_playlist(video_id, course_name)
             
             report_lines.append(f"{folder_date.strftime('%H:%M')} | {course_name} | Посилання: {video_url}")
             
             logging.info(f"Відео завантажено успішно. Переміщуємо папку '{folder}' у Кошик...")
             try:
                 send2trash(folder_path)
                 logging.info(f"Папка {folder} відправлена у Кошик.")
             except Exception as trash_e:
                 logging.warning(f"Не вдалося відправити у Кошик: {trash_e}. Залишаємо папку.")
                 
         except Exception as e:
             logging.error(f"Помилка завантаження відео з '{folder}': {e}")
             report_lines.append(f"ПОМИЛКА | {course_name}: {e}")

    if report_lines:
        report_path = create_report(BASE_DIR, report_lines)
        logging.info(f"Готово! Звіт збережено у файл: {report_path}")
    else:
        logging.info("Нових відео для завантаження не знайдено.")

if __name__ == '__main__':
    process_zoom_folders()
