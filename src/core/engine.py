import os
from datetime import datetime
from send2trash import send2trash
from ..services.file_utils import find_video
from ..services.youtube.video import VideoService
from ..services.youtube.playlist import PlaylistController
from ..services.lms.service import LmsService
from ..services.schedule_utils import get_course_name_by_date, get_date_from_file_name

def process_lms(report_rows, config, schedule, logger, status_cb=None):
    token = config.get_lms_token()
    if not token: 
        msg = "LMS Sync failed: Token is missing in settings."
        logger.error(msg)
        try:
            from tkinter import messagebox
            messagebox.showerror("Config Error", msg)
        except: pass
        return []
        
    lms, lms_report, total = LmsService(token, logger), [], len(report_rows)
    logger.info(f"Starting LMS Sync for {total} records...")
    
    for i, row in enumerate(report_rows):
        if not row or len(row) < 4:
            logger.warning(f"Skipping invalid report row {i}: {row}")
            continue
            
        date_str, name, url, status, *rest = row
        reporting_name = ""

        if not url:
            lms_report.append([date_str, name, "", "skipped", "missing url"])
            continue

        if status_cb: status_cb(f"LMS Sync: {name}...", (i + 1, total))
        logger.info(f"--- Processing LMS Sync: {name} ---")
        if url: logger.info(f"Link: {url}")
        
        try:
            rec_date = datetime.strptime(date_str, '%d.%m.%Y %H:%M')
        except:
            lms_report.append([date_str, name, "", "skipped", "invalid date format"])
            logger.warning(f"Invalid date format: {date_str}")
            continue
            
        meta = get_course_name_by_date(rec_date, schedule)
        if not meta or isinstance(meta, str):
            lms_report.append([date_str, name, "", "skipped", "lesson not found in schedule"])
            logger.warning(f"No schedule entry for '{name}' at {date_str}")
            continue

        if not meta.get("lms_course_id"):
            lms_report.append([date_str, name, "", "skipped", "missing lms id"])
            logger.warning(f"Missing lms_course_id for '{name}'")
            continue
            
        try:
            ok, actual_name, details = lms.sync_video(
                config.get_school_id(), meta.get("lms_course_id"), rec_date, url
            )
            reporting_name = actual_name if actual_name else ""
            st = "pass" if ok else "fail"
            msg = "successfully updated" if ok else details
            lms_report.append([date_str, name, reporting_name, st, msg])
            if ok:
                logger.info(f"SUCCESS: Synchronized '{reporting_name or name}' with LMS")
            else:
                logger.error(f"FAILED: {details}")
                
        except RuntimeError as e:
            if "LMS_AUTH_ERROR" in str(e):
                msg = str(e).split(": ")[1]
                logger.error(msg)
                lms_report.append([date_str, name, "", "skipped", "authentication failed"])
                for j in range(i + 1, total):
                    lms_report.append([report_rows[j][0], report_rows[j][1], "", "skipped", "authentication failed"])
                try:
                    from tkinter import messagebox
                    messagebox.showerror("Auth Error", msg)
                except: pass
                break
            else:
                lms_report.append([date_str, name, "", "fail", f"error: {str(e)}"])
        except Exception as e: 
            msg = f"unknown error: {str(e)}"
            lms_report.append([date_str, name, "", "fail", msg])
            logger.error(f"CRITICAL ERROR for '{name}': {msg}")
            
    return lms_report
