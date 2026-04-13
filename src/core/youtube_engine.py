import os
from datetime import datetime
from send2trash import send2trash
from ..services.file_utils import find_video
from ..services.youtube.video import VideoService
from ..services.youtube.playlist import PlaylistController
from ..services.schedule_utils import get_course_name_by_date, get_date_from_file_name

def process_youtube(config, schedule, youtube, logger, status_cb=None):
    zoom_dir = config.get_zoom_dir()
    if not zoom_dir or not os.path.exists(zoom_dir): return []
    folders = [f for f in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, f))]
    report_rows, total = [], len(folders)
    
    for i, folder in enumerate(folders):
        folder_path = os.path.join(zoom_dir, folder)
        mp4 = find_video(folder_path)
        if not mp4: continue
        
        f_date = get_date_from_file_name(folder)
        course_data = get_course_name_by_date(f_date, schedule) if f_date else None
        
        if not course_data: 
            logger.info(f"No schedule match for '{folder}'. Marked as PRIVATE skipped.")
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M') if f_date else "N/A", "Private/Unknown", "", "Skipped (Private)"])
            continue

        name = course_data if isinstance(course_data, str) else course_data.get("name")
        thumb = None if isinstance(course_data, str) else course_data.get("thumbnail")
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if thumb and not os.path.isabs(thumb): thumb = os.path.join(root_dir, "thumbnails", thumb)
        
        if status_cb: status_cb(f"Processing {name}...", (i + 1, total))
        marker = os.path.join(folder_path, ".uploaded_to_youtube")
        
        if os.path.exists(marker):
            with open(marker, 'r') as f: vid = f.read().strip()
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M'), name, f"https://youtu.be/{vid}", "Already Uploaded"])
            continue

        try:
            logger.info(f"Uploading '{name}' ({f_date.strftime('%d.%m.%Y')})...")
            vs = VideoService(youtube, logger)
            vid, url = vs.upload(os.path.join(folder_path, mp4[0]), f"{name}/{f_date.strftime('%d.%m.%Y')}", f"Lesson: {name}")
            
            if thumb and os.path.exists(thumb):
                logger.info(f"Setting thumbnail: {os.path.basename(thumb)}")
                vs.set_thumbnail(vid, thumb)
            elif thumb:
                logger.warning(f"Thumbnail not found: {thumb}")

            with open(marker, 'w') as f: f.write(vid)
            PlaylistController(youtube, logger).add_video(vid, name)
            logger.info(f"SUCCESS: '{name}' uploaded to YouTube.")
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M'), name, url, "Success"])
            send2trash(os.path.normpath(folder_path))
        except Exception as e:
            logger.error(f"Upload error {folder}: {e}")
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M'), name, "", f"Error: {e}"])
    return report_rows
