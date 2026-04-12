import os
from datetime import datetime
from send2trash import send2trash
from ..services.file_utils import find_video
from ..services.youtube.video import VideoService
from ..services.youtube.playlist import PlaylistController
from ..services.lms.service import LmsService
from ..services.schedule_utils import get_course_name_by_date, get_date_from_file_name

def process_youtube(config, schedule, youtube, logger, status_cb=None):
    zoom_dir, base_dir = config.get_zoom_dir(), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not zoom_dir or not os.path.exists(zoom_dir): return []
    report_rows, folders = [], [f for f in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, f))]
    total = len(folders)
    
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
        if thumb and not os.path.isabs(thumb): thumb = os.path.join(base_dir, "thumbnails", thumb)
        
        if status_cb: status_cb(f"Processing {name}...", (i, total))
        marker = os.path.join(folder_path, ".uploaded_to_youtube")
        
        if os.path.exists(marker):
            with open(marker, 'r') as f: vid = f.read().strip()
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M'), name, f"https://youtu.be/{vid}", "Already Uploaded"])
            continue

        try:
            vs = VideoService(youtube, logger)
            vid, url = vs.upload(os.path.join(folder_path, mp4[0]), f"{name}/{f_date.strftime('%d.%m.%Y')}", f"Lesson: {name}")
            if thumb: vs.set_thumbnail(vid, thumb)
            with open(marker, 'w') as f: f.write(vid)
            PlaylistController(youtube, logger).add_video(vid, name)
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M'), name, url, "Success"])
            send2trash(os.path.normpath(folder_path))
        except Exception as e:
            logger.error(f"Upload error {folder}: {e}")
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M'), name, "", f"Error: {e}"])
    return report_rows

def process_lms(report_rows, config, schedule, logger, status_cb=None):
    token = config.get_lms_token()
    if not token: return []
    lms, lms_report, total = LmsService(token, logger), [], len(report_rows)
    for i, row in enumerate(report_rows):
        date_str, name, url, status = row
        if not url or ("Success" not in status and "Already" not in status): continue
        if status_cb: status_cb(f"LMS Sync {name}...", (i, total))
        meta = None
        for day, times in schedule.items():
            for t, data in times.items():
                if data.get("name") == name: meta = data; break
            if meta: break
        if not meta or not meta.get("lms_course_id"):
            lms_report.append([date_str, name, "Skipped", "Missing LMS ID"])
            continue
        try:
            rec_date = datetime.strptime(date_str, '%d.%m.%Y %H:%M')
            ok = lms.sync_video(config.get_school_id(), meta.get("lms_course_id"), rec_date, url)
            lms_report.append([date_str, name, "Success" if ok else "Failed", "Updated" if ok else "Error"])
        except Exception as e: lms_report.append([date_str, name, "Error", str(e)])
    return lms_report
