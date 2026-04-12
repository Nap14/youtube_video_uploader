import os
import csv
import threading
from ..core.engine import process_youtube, process_lms
from ..services.youtube.auth import Oauth2Service
from ..services.report_utils import create_report

_EXECUTION_LOCK = threading.Lock()

def execute_automation(config, schedule, paths, mode, logger, progress_cb, lms_csv_path=None, task_prefix=""):
    """
    Core sequence: YouTube upload -> LMS sync with execution locking.
    """
    if not _EXECUTION_LOCK.acquire(blocking=False):
        logger.error("Automation is already in progress. Task skipped.")
        return False

    try:
        yt_res = []
        
        # 1. YouTube Upload Phase
        if mode in ["1", "2"]:
            oauth = Oauth2Service(logger)
            youtube = oauth.get_service(paths['TOKEN_FILE'], paths['SECRETS_FILE'])
            yt_res = process_youtube(config, schedule, youtube, logger, progress_cb)
            if yt_res:
                create_report(yt_res, config.get_reports_dir(), f"{task_prefix}youtube")
        
        # 2. LMS Sync Phase (from YouTube results or CSV)
        if mode == "3" and lms_csv_path:
            if not os.path.exists(lms_csv_path):
                logger.error(f"File not found: {lms_csv_path}")
                return False
            with open(lms_csv_path, mode='r', encoding='utf-8') as f_obj:
                yt_res = list(csv.reader(f_obj))[1:]
            logger.info(f"Loaded {len(yt_res)} records from CSV.")

        if mode in ["1", "3"]:
            if not yt_res:
                logger.warning("No data for LMS sync.")
            else:
                lms_res = process_lms(yt_res, config, schedule, logger, progress_cb)
                if lms_res:
                    create_report(lms_res, config.get_reports_dir(), f"{task_prefix}lms")
        
        logger.info("Automation Sequence Completed!")
        return True
    finally:
        _EXECUTION_LOCK.release()
