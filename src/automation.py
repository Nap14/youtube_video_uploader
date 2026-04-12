import os
import logging
from datetime import datetime
from send2trash import send2trash
from src.file_service import find_video
from src.authenticated_service import Oauth2Service
from src.playlist_service import PlaylistController
from src.video_service import VideoService
from src.lms_service import LmsService
from src.schedule import get_course_name_by_date, get_date_from_file_name

def process_youtube_uploads(config, schedule, youtube, logger=None, status_callback=None):
    """
    Handles the YouTube upload phase.
    status_callback(message, progress_tuple)
    """
    log = logger or logging
    zoom_dir = config.get_zoom_dir()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if not zoom_dir or not os.path.exists(zoom_dir):
        msg = f"Zoom folder {zoom_dir} not found."
        log.error(msg)
        if status_callback: status_callback(msg, (0, 1))
        return []

    report_rows = []
    folders = [f for f in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, f))]
    total = len(folders)
    
    for i, folder in enumerate(folders):
        folder_path = os.path.join(zoom_dir, folder)
        mp4_files = find_video(folder_path)
        if not mp4_files:
            continue
        
        video_file = os.path.join(folder_path, mp4_files[0])
        folder_date = get_date_from_file_name(folder)
        if not folder_date:
            log.warning(f"Could not recognize date from folder name: '{folder}'")
            continue

        course_data = get_course_name_by_date(folder_date, schedule)
        if not course_data:
            log.warning(f"Course not found in schedule for folder '{folder}'. Skipping.")
            continue

        course_name = course_data if isinstance(course_data, str) else course_data.get("name")
        thumbnail_path = None if isinstance(course_data, str) else course_data.get("thumbnail")
        if thumbnail_path and not os.path.isabs(thumbnail_path):
            thumbnail_path = os.path.join(base_dir, "thumbnails", thumbnail_path)
        
        if status_callback: 
            status_callback(f"Processing {course_name}...", (i, total))

        uploaded_marker = os.path.join(folder_path, ".uploaded_to_youtube")
        if os.path.exists(uploaded_marker):
             log.info(f"Video in '{folder}' was already uploaded. Skipping YT.")
             with open(uploaded_marker, 'r') as f:
                  video_id = f.read().strip()
             report_rows.append([folder_date.strftime('%d.%m.%Y %H:%M'), course_name, f"https://youtu.be/{video_id}", "Already Uploaded"])
             continue

        log.info(f"Uploading to YouTube: {course_name} ({folder_date})")
        try:
            video_service = VideoService(youtube, log)
            video_title = f"{course_name}/{folder_date.strftime('%d.%m.%Y')}"
            video_description = f"Automatic upload of lesson recording: {course_name}"
            
            video_id, video_url = video_service.upload_video(video_file, video_title, video_description)
            
            if thumbnail_path:
                video_service.set_video_thumbnail(video_id, thumbnail_path)
            
            with open(uploaded_marker, 'w') as f:
                f.write(video_id)
                
            playlist_service = PlaylistController(youtube, log)
            playlist_service.add_video_to_playlist(video_id, course_name)
            
            report_rows.append([folder_date.strftime('%d.%m.%Y %H:%M'), course_name, video_url, "Success"])
            
            log.info(f"YT Success. Trashing {folder}...")
            send2trash(os.path.normpath(folder_path))
            
        except Exception as e:
            log.error(f"YT Error for '{folder}': {e}")
            report_rows.append([folder_date.strftime('%d.%m.%Y %H:%M'), course_name, "", f"Error: {e}"])

    if status_callback: status_callback("YouTube phase complete.", (total, total))
    return report_rows

def sync_to_lms(report_rows, config, schedule, logger=None, status_callback=None):
    """
    Syncs YouTube links from report rows to SendPulse LMS.
    """
    log = logger or logging
    token = config.get_lms_token()
    if not token:
        log.warning("LMS_TOKEN missing in configs/config.json. Skipping LMS sync.")
        return []

    lms = LmsService(token, log)
    lms_report = []
    total = len(report_rows)

    for i, row in enumerate(report_rows):
        date_str, course_name, yt_url, status = row
        if not yt_url or "Success" not in status and "Already" not in status:
            continue

        if status_callback: 
            status_callback(f"Syncing {course_name} ({date_str}) to LMS...", (i, total))

        course_meta = None
        for day, times in schedule.items():
            for t, data in times.items():
                if data.get("name") == course_name:
                    course_meta = data
                    break
            if course_meta: break

        if not course_meta or not course_meta.get("lms_course_id"):
            log.warning(f"LMS metadata (lms_course_id) missing for '{course_name}'. Skipping sync.")
            lms_report.append([date_str, course_name, "Skipped", "Missing LMS ID in schedule.json"])
            continue

        school_id = config.get_school_id()
        course_id = course_meta.get("lms_course_id")
        
        try:
            recording_date = datetime.strptime(date_str, '%d.%m.%Y %H:%M')
            success = lms.sync_video_to_lesson(school_id, course_id, recording_date, yt_url)
            lms_report.append([date_str, course_name, "Success" if success else "Failed", "Check logs" if not success else "Updated"])
        except Exception as e:
            log.error(f"LMS Sync error for {course_name}: {e}")
            lms_report.append([date_str, course_name, "Error", str(e)])

    if status_callback: status_callback("LMS phase complete.", (total, total))
    return lms_report
