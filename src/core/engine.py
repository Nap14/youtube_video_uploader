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
    print(f"\n[INFO] Starting discovery in: {zoom_dir}")
    if not zoom_dir or not os.path.exists(zoom_dir): 
        print(f"[ERROR] Directory not found: {zoom_dir}")
        return []

    report_rows, folders = [], [f for f in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, f))]
    total = len(folders)
    print(f"[INFO] Found {total} folders to process.")
    
    for i, folder in enumerate(folders):
        print(f"\n--- Checking folder: {folder} ---")
        folder_path = os.path.join(zoom_dir, folder)
        mp4 = find_video(folder_path)
        if not mp4: 
            print(f"[SKIP] No video found in {folder}")
            continue
        
        f_date = get_date_from_file_name(folder)
        course_data = get_course_name_by_date(f_date, schedule) if f_date else None
        
        if not course_data: 
            msg = f"No schedule match for '{folder}'. Marked as PRIVATE skipped."
            print(f"[PRIVATE] {msg}")
            logger.info(msg)
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M') if f_date else "N/A", "Private/Unknown", "", "Skipped (Private)"])
            continue

        name = course_data if isinstance(course_data, str) else course_data.get("name")
        print(f"[MATCH] Folder linked to course: {name}")
        
        thumb = None if isinstance(course_data, str) else course_data.get("thumbnail")
        if thumb and not os.path.isabs(thumb): thumb = os.path.join(base_dir, "thumbnails", thumb)
        
        if status_cb: status_cb(f"Processing {name}...", (i, total))
        marker = os.path.join(folder_path, ".uploaded_to_youtube")
        
        if os.path.exists(marker):
            with open(marker, 'r') as f: vid = f.read().strip()
            print(f"[YT] Video already exists: https://youtu.be/{vid}")
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M'), name, f"https://youtu.be/{vid}", "Already Uploaded"])
            continue

        try:
            print(f"[YT] Start uploading: {name}...")
            vs, vid_url = VideoService(youtube, logger), ""
            vid, vid_url = vs.upload(os.path.join(folder_path, mp4[0]), f"{name}/{f_date.strftime('%d.%m.%Y')}", f"Lesson: {name}")
            if thumb: 
                print(f"[YT] Setting thumbnail: {thumb}")
                vs.set_thumbnail(vid, thumb)
            with open(marker, 'w') as f: f.write(vid)
            print(f"[YT] Success: {vid_url}")
            PlaylistController(youtube, logger).add_video(vid, name)
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M'), name, vid_url, "Success"])
            print(f"[CLEANUP] Trashing local folder: {folder}")
            send2trash(os.path.normpath(folder_path))
        except Exception as e:
            msg = f"Upload error {folder}: {e}"
            print(f"[ERROR] {msg}")
            logger.error(msg)
            report_rows.append([f_date.strftime('%d.%m.%Y %H:%M'), name, "", f"Error: {e}"])

    print(f"\n[INFO] Discovery finished. {len(report_rows)} rows generated.")
    return report_rows

def process_lms(report_rows, config, schedule, logger, status_cb=None):
    token = config.get_lms_token()
    if not token: return []
    
    lms, lms_report, total = LmsService(token, logger), [], len(report_rows)
    for i, row in enumerate(report_rows):
        date_str, name, url, status = row
        if not url or "Success" not in status and "Already" not in status: continue
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
