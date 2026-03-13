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
    Main loop to search and upload Zoom videos.
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        logging.error(f"File {CLIENT_SECRETS_FILE} not found. API is not configured.")
        return

    config = Config(CONFIG_FILE, logging)
    zoom_dir = config.get_zoom_dir()

    if not zoom_dir or not os.path.exists(zoom_dir):
        logging.error(f"Zoom folder {zoom_dir} not found.")
        return

    schedule = load_schedule(SCHEDULE_FILE, logging)
    if not schedule:
        return

    oauth2 = Oauth2Service(logging)
    youtube = oauth2.get_youtube_service(TOKEN_FILE, CLIENT_SECRETS_FILE)

    report_lines = []

    folders = [f for f in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, f))]
    
    for folder in folders:
         folder_path = os.path.join(zoom_dir, folder)
         
         mp4_files = find_video(folder_path)
         if not mp4_files:
             logging.info(f"No .mp4 files found in folder '{folder}'. Skipping.")
             continue
         
         video_file = os.path.join(folder_path, mp4_files[0])
         
         folder_date = get_date_from_file_name(folder)
         if not folder_date:
            logging.warning(f"Could not recognize date from folder name: '{folder}'")
            continue

         course_data = get_course_name_by_date(folder_date, schedule)
         if not course_data:
             logging.warning(f"Course not found in schedule for folder '{folder}'. Skipping video.")
             continue
         elif isinstance(course_data, str):
             course_name = course_data
             thumbnail_path = None
         else:
             course_name = course_data.get("name", f"Unknown Course")
             thumbnail_path = course_data.get("thumbnail")
             if thumbnail_path and not os.path.isabs(thumbnail_path):
                 thumbnail_path = os.path.join(BASE_DIR, "thumbnails", thumbnail_path)
         
         video_title = f"{course_name}/{folder_date.strftime('%d.%m.%Y')}"
         video_description = f"Automatic upload of lesson recording: {course_name}"
         
         uploaded_marker = os.path.join(folder_path, ".uploaded_to_youtube")
         if os.path.exists(uploaded_marker):
              logging.info(f"Video in '{folder}' was already uploaded. Skipping.")
              continue

         logging.info(f"Starting video upload for: {course_name}")
         try:
             video_service = VideoService(youtube, logging)
             video_id, video_url = video_service.upload_video(video_file, video_title, video_description)
             
             if thumbnail_path:
                 video_service.set_video_thumbnail(video_id, thumbnail_path)
             
             playlist_service = PlaylistController(youtube, logging)
             playlist_service.add_video_to_playlist(video_id, course_name)
             
             report_lines.append(f"{folder_date.strftime('%H:%M')} | {course_name} | Link: {video_url}")
             
             logging.info(f"Video uploaded successfully. Moving folder '{folder}' to Trash...")
             try:
                 send2trash(folder_path)
                 logging.info(f"Folder {folder} sent to Trash.")
             except Exception as trash_e:
                 logging.warning(f"Failed to send to Trash: {trash_e}. Keeping folder.")
                 
         except Exception as e:
             logging.error(f"Error uploading video from '{folder}': {e}")
             report_lines.append(f"ERROR | {course_name}: {e}")

    if report_lines:
        report_path = create_report(BASE_DIR, report_lines)
        logging.info(f"Done! Report saved to: {report_path}")
    else:
        logging.info("No new videos found for upload.")

if __name__ == '__main__':
    process_zoom_folders()
