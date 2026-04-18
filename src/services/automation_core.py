import csv
import os
import threading
from typing import Callable, List, Optional

from src.core.context import AppContext
from src.services.lms.engine import LmsProcessor
from src.services.lms.service import LmsService
from src.services.report_utils import create_report
from src.services.youtube.auth import Oauth2Service
from src.services.youtube.engine import YoutubeProcessor
from src.services.youtube.playlist import PlaylistController
from src.services.youtube.video import VideoService

_EXECUTION_LOCK = threading.Lock()

class AutomationCore:
    def __init__(
        self, 
        ctx: AppContext, 
        progress_cb: Callable[[str, tuple], None], 
        error_cb: Optional[Callable[[str, str], None]] = None
    ):
        self.ctx = ctx
        self.progress_cb = progress_cb
        self.error_cb = error_cb

    def _upload_video(self, task_prefix: str = '') -> List[List[str]]:
        oauth = Oauth2Service(self.ctx.logger)
        youtube = oauth.get_service(self.ctx.paths.token_file, self.ctx.paths.secrets_file)
        
        vs = VideoService(youtube, self.ctx.logger)
        pc = PlaylistController(youtube, self.ctx.logger)
        
        processor = YoutubeProcessor(vs, pc, self.ctx, error_cb=self.error_cb)
        result = processor.process(self.progress_cb)
        
        if result:
            create_report(result, self.ctx.config.get_reports_dir(), f"{task_prefix}youtube")
            
        return result

    def _sync_lms(self, yt_res: List[List[str]], task_prefix: str = "") -> None:
        if not yt_res:
            self.ctx.logger.warning("No data for LMS sync.")
            return
            
        try:
            token = self.ctx.config.get_lms_token()
            lms_service = LmsService(token, self.ctx.logger)
            processor = LmsProcessor(lms_service, self.ctx, error_cb=self.error_cb)
            
            lms_res = processor.process(yt_res, self.progress_cb)
            if lms_res:
                headers = ["Date", "Course", "Lesson Name", "Status", "Details"]
                create_report(lms_res, self.ctx.config.get_reports_dir(), f"{task_prefix}lms", headers=headers)
        except ValueError as e:
            self.ctx.logger.error(str(e))
            if self.error_cb:
                self.error_cb("Config Error", str(e))

    def _load_ytb_csv(self, lms_csv_path: str) -> List[List[str]]:
        if not os.path.exists(lms_csv_path):
            raise FileNotFoundError(f"File not found: {lms_csv_path}")
            
        with open(lms_csv_path, mode='r', encoding='utf-8') as f:
            return list(csv.reader(f))[1:]

    def execute_automation(self, mode: str, lms_csv_path: Optional[str] = None, task_prefix: str = "") -> bool:
        if not _EXECUTION_LOCK.acquire(blocking=False):
            self.ctx.logger.error("Automation is already in progress. Task skipped.")
            return False
            
        try:
            return self._run_sequence(mode, lms_csv_path, task_prefix)
        except Exception as e:
            self.ctx.logger.error(f"Fatal error: {e}")
            return False
        finally:
            _EXECUTION_LOCK.release()

    def _run_sequence(self, mode: str, lms_csv_path: Optional[str], task_prefix: str) -> bool:
        yt_res: List[List[str]] = []
        
        if mode in ["1", "2"]:
            self.ctx.logger.info("Starting YouTube Upload Phase...")
            yt_res = self._upload_video(task_prefix)
            self.ctx.logger.info("YouTube Upload Phase Completed.")
            
        if mode == "3" and lms_csv_path:
            yt_res = self._load_ytb_csv(lms_csv_path)
            self.ctx.logger.info(f"Loaded {len(yt_res)} records from CSV.")
            
        if mode in ["1", "3"]:
            self.ctx.logger.info("Starting LMS Synchronization Phase...")
            self._sync_lms(yt_res, task_prefix)
            
        self.ctx.logger.info("Automation Sequence Completed!")
        return True
