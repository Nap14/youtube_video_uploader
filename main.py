import os
import logging
import csv
from datetime import datetime
from send2trash import send2trash

from src.authenticated_service import Oauth2Service
from src.file_service import find_video
from src.playlist_service import PlaylistController
from src.report import create_report
from src.schedule import get_course_name_by_date, load_schedule, get_date_from_file_name
from src.video_service import VideoService
from src.config import Config
from src.lms_service import LmsService

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIGS_DIR = os.path.join(BASE_DIR, "configs")
CONFIG_FILE = os.path.join(CONFIGS_DIR, "config.json")
CLIENT_SECRETS_FILE = os.path.join(CONFIGS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CONFIGS_DIR, "token.json")
SCHEDULE_FILE = os.path.join(CONFIGS_DIR, "schedule.json")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_youtube_uploads(config, schedule, youtube, reports_dir):
    """
    Handles the YouTube upload phase and returns report rows.
    """
    zoom_dir = config.get_zoom_dir()
    if not zoom_dir or not os.path.exists(zoom_dir):
        logging.error(f"Zoom folder {zoom_dir} not found.")
        return []

    report_rows = []
    folders = [f for f in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, f))]
    
    for folder in folders:
        folder_path = os.path.join(zoom_dir, folder)
        mp4_files = find_video(folder_path)
        if not mp4_files:
            continue
        
        video_file = os.path.join(folder_path, mp4_files[0])
        folder_date = get_date_from_file_name(folder)
        if not folder_date:
            logging.warning(f"Could not recognize date from folder name: '{folder}'")
            continue

        course_data = get_course_name_by_date(folder_date, schedule)
        if not course_data:
            logging.warning(f"Course not found in schedule for folder '{folder}'. Skipping.")
            continue

        course_name = course_data if isinstance(course_data, str) else course_data.get("name")
        thumbnail_path = None if isinstance(course_data, str) else course_data.get("thumbnail")
        if thumbnail_path and not os.path.isabs(thumbnail_path):
            thumbnail_path = os.path.join(BASE_DIR, "thumbnails", thumbnail_path)
        
        uploaded_marker = os.path.join(folder_path, ".uploaded_to_youtube")
        if os.path.exists(uploaded_marker):
             logging.info(f"Video in '{folder}' was already uploaded. Skipping YT.")
             with open(uploaded_marker, 'r') as f:
                 video_id = f.read().strip()
             report_rows.append([folder_date.strftime('%d.%m.%Y %H:%M'), course_name, f"https://youtu.be/{video_id}", "Already Uploaded"])
             continue

        logging.info(f"Uploading to YouTube: {course_name} ({folder_date})")
        try:
            video_service = VideoService(youtube, logging)
            video_title = f"{course_name}/{folder_date.strftime('%d.%m.%Y')}"
            video_description = f"Automatic upload of lesson recording: {course_name}"
            
            video_id, video_url = video_service.upload_video(video_file, video_title, video_description)
            
            if thumbnail_path:
                video_service.set_video_thumbnail(video_id, thumbnail_path)
            
            with open(uploaded_marker, 'w') as f:
                f.write(video_id)
                
            playlist_service = PlaylistController(youtube, logging)
            playlist_service.add_video_to_playlist(video_id, course_name)
            
            report_rows.append([folder_date.strftime('%d.%m.%Y %H:%M'), course_name, video_url, "Success"])
            
            logging.info(f"YT Success. Trashing {folder}...")
            send2trash(os.path.normpath(folder_path))
            
        except Exception as e:
            logging.error(f"YT Error for '{folder}': {e}")
            report_rows.append([folder_date.strftime('%d.%m.%Y %H:%M'), course_name, "", f"Error: {e}"])

    return report_rows

def sync_to_lms(report_rows, config, schedule):
    """
    Syncs YouTube links from report rows to SendPulse LMS.
    """
    token = config.get_lms_token()
    if not token:
        logging.warning("LMS_TOKEN missing in config.json. Skipping LMS sync.")
        logging.info("To enable LMS, add 'LMS_TOKEN': 'yourBearerTokenHere' to config.json.")
        return []

    lms = LmsService(token, logging)
    lms_report = []

    for row in report_rows:
        date_str, course_name, yt_url, status = row
        if not yt_url or "Success" not in status and "Already" not in status:
            continue

        course_meta = None
        for day, times in schedule.items():
            for t, data in times.items():
                if data.get("name") == course_name:
                    course_meta = data
                    break
            if course_meta: break

        if not course_meta or not course_meta.get("lms_course_id"):
            logging.warning(f"LMS metadata (lms_course_id) missing for '{course_name}'. Skipping sync.")
            lms_report.append([date_str, course_name, "Skipped", "Missing LMS ID in schedule.json"])
            continue

        school_id = config.get_school_id()
        course_id = course_meta.get("lms_course_id")
        
        try:
            recording_date = datetime.strptime(date_str, '%d.%m.%Y %H:%M')
            
            success = lms.sync_video_to_lesson(school_id, course_id, recording_date, yt_url)
            lms_report.append([date_str, course_name, "Success" if success else "Failed", "Check logs" if not success else "Updated"])
        except Exception as e:
            logging.error(f"LMS Sync error for {course_name}: {e}")
            lms_report.append([date_str, course_name, "Error", str(e)])

    return lms_report

import sys
from src.gui_app import ZoomUploaderGUI
from src.automation import process_youtube_uploads, sync_to_lms

def run_cli(config, schedule, reports_dir):
    print("\n--- Zoom Video Automation (CLI Mode) ---")
    print("1. Full Cycle (YouTube Upload + LMS Sync)")
    print("2. YouTube Only")
    print("3. LMS Sync Only (from existing YT report CSV)")
    
    choice = input("\nSelect mode (1-3): ").strip()
    
    if choice == '1' or choice == '2':
        if not os.path.exists(CLIENT_SECRETS_FILE):
            logging.error(f"YouTube secrets missing: {CLIENT_SECRETS_FILE}")
            return
        
        oauth2 = Oauth2Service(logging)
        youtube = oauth2.get_youtube_service(TOKEN_FILE, CLIENT_SECRETS_FILE)
        
        yt_report_rows = process_youtube_uploads(config, schedule, youtube)
        
        if yt_report_rows:
            report_path = create_report(reports_dir, yt_report_rows, "youtube")
            logging.info(f"YouTube report saved: {report_path}")
            
            if choice == '1':
                logging.info("Starting LMS Synchronization phase...")
                lms_rows = sync_to_lms(yt_report_rows, config, schedule)
                if lms_rows:
                    lms_path = create_report(reports_dir, lms_rows, "lms")
                    logging.info(f"LMS report saved: {lms_path}")
        else:
            logging.info("No videos processed for YouTube.")

    elif choice == '3':
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        report_file = filedialog.askopenfilename(
            initialdir=reports_dir,
            title="Select YouTube Report CSV",
            filetypes=(("CSV files", "*.csv"), ("all files", "*.*"))
        )
        root.destroy()

        if not report_file:
            logging.info("Selection cancelled.")
            return
        
        rows = []
        with open(report_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # skip header
            for r in reader: rows.append(r)
        
        lms_rows = sync_to_lms(rows, config, schedule)
        if lms_rows:
            lms_path = create_report(reports_dir, lms_rows, "lms")
            logging.info(f"LMS synchronization complete. Report: {lms_path}")
    else:
        print("Invalid choice.")

def main():
    config = Config(CONFIG_FILE, logging)
    schedule = load_schedule(SCHEDULE_FILE, logging)
    reports_dir = config.get_reports_dir()
    
    # Check for CLI flag
    if "--cli" in sys.argv:
        run_cli(config, schedule, reports_dir)
    else:
        # Launch GUI
        paths = {
            'CONFIG_FILE': CONFIG_FILE,
            'CLIENT_SECRETS_FILE': CLIENT_SECRETS_FILE,
            'TOKEN_FILE': TOKEN_FILE,
            'SCHEDULE_FILE': SCHEDULE_FILE
        }
        app = ZoomUploaderGUI(config, schedule, paths)
        app.mainloop()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")
    except Exception as e:
        if "main thread is not in main loop" not in str(e):
            logging.critical(f"Fatal error: {e}", exc_info=True)
