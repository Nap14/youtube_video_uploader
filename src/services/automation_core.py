import os
import csv
import threading
from typing import List, Optional, Callable

from ..services.youtube.auth import Oauth2Service
from ..services.youtube.video import VideoService
from ..services.youtube.playlist import PlaylistController
from ..services.youtube.engine import YoutubeProcessor
from ..services.report_utils import create_report
from ..services.lms.engine import LmsProcessor
from ..services.lms.service import LmsService

_EXECUTION_LOCK = threading.Lock()

class AutomationCore:
    def __init__(self, config, schedule: dict, paths: dict, logger, progress_cb: Callable, error_cb: Optional[Callable[[str, str], None]] = None):
        self.config = config
        self.schedule = schedule
        self.paths = paths
        self.logger = logger
        self.progress_cb = progress_cb
        self.error_cb = error_cb

    def _upload_video(self, task_prefix: str = '') -> List[List[str]]:
        oauth = Oauth2Service(self.logger)
        youtube = oauth.get_service(self.paths['TOKEN_FILE'], self.paths['SECRETS_FILE'])
        
        vs = VideoService(youtube, self.logger)
        pc = PlaylistController(youtube, self.logger)
        
        processor = YoutubeProcessor(
            vs, pc, self.config, self.schedule, self.logger, 
            root_dir=self.paths['BASE_DIR'],
            error_cb=self.error_cb
        )
        result = processor.process(self.progress_cb)

        if not result:
            return []

        create_report(result, self.config.get_reports_dir(), f"{task_prefix}youtube")
        return result

    def _get_lms_service(self) -> Optional[LmsService]:
        try:
            token = self.config.get_lms_token()
            return LmsService(token, self.logger)
        except ValueError as e:
            msg = "LMS Sync failed: Token is missing in settings."
            self.logger.error(e)
            if self.error_cb:
                self.error_cb("Config Error", msg)
            return None

    def _sync_lms(self, yt_res: List[List[str]], task_prefix: str = ""):
        if not yt_res:
            return self.logger.warning("No data for LMS sync.")

        lms_service = self._get_lms_service()
        if not lms_service:
            return

        processor = LmsProcessor(
            lms_service,
            self.config,
            self.schedule,
            self.logger,
            error_cb=self.error_cb
        )

        lms_res = processor.process(yt_res, self.progress_cb)
        if not lms_res:
            return

        headers = ["Date", "Course", "Lesson Name", "Status", "Details"]
        create_report(lms_res, self.config.get_reports_dir(), f"{task_prefix}lms", headers=headers)

    def _load_ytb_csv(self, lms_csv_path):
        if not os.path.exists(lms_csv_path):
            raise Exception(f"File not found: {lms_csv_path}")
            
        with open(lms_csv_path, mode='r', encoding='utf-8') as f_obj:
            return list(csv.reader(f_obj))[1:]

    def execute_automation(self, mode, lms_csv_path=None, task_prefix=""):
        """
        Core sequence: YouTube upload -> LMS sync with execution locking.
        """
        if not _EXECUTION_LOCK.acquire(blocking=False):
            self.logger.error("Automation is already in progress. Task skipped.")
            return False

        try:
            yt_res = []
            
            if mode in ["1", "2"]:
                yt_res = self._upload_video(task_prefix)
            
            if mode == "3" and lms_csv_path:
                yt_res = self._load_ytb_csv(lms_csv_path)
                self.logger.info(f"Loaded {len(yt_res)} records from CSV.")

            if mode in ["1", "3"]:
                self._sync_lms(yt_res, task_prefix)
            
            self.logger.info("Automation Sequence Completed!")
            return True
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False
        finally:
            _EXECUTION_LOCK.release()
