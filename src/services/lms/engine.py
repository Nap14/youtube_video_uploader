from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

from src.core.context import AppContext
from src.services.base_processor import BaseProcessor
from .data.reportRow import ReportRow, SyncResult
from .data.status import SyncStatus
from .service import LmsService
from ..schedule_utils import get_course_name_by_date

class LmsProcessor(BaseProcessor):
    def __init__(self, lms: LmsService, ctx: AppContext, error_cb: Optional[Callable[[str, str], None]] = None):
        super().__init__(ctx, error_cb)
        self.lms = lms

    def process(self, raw_rows: List[List[str]], progress_cb: Optional[Callable[[str, tuple], None]] = None) -> List[List[str]]:
        self.ctx.logger.info(f"Starting LMS Sync for {len(raw_rows)} items...")
        if progress_cb:
            progress_cb(f"LMS Syncing...", (0, len(raw_rows)))

        results: List[SyncResult] = []
        for i, raw in enumerate(raw_rows):
            res = self._process_single_raw(raw, i, len(raw_rows), progress_cb)
            
            if res == "AUTH_ERROR":
                results.extend(self._skip_remaining(raw_rows, i))
                self._report_error("LMS Auth Error", "LMS authentication failed. Check token.")
                break
                
            results.append(res)
            
        if progress_cb:
            progress_cb("LMS Sync Completed!", (1, 1))

        return [r.to_list() for r in results]

    def _process_single_raw(self, raw, i, total, progress_cb):
        row = self._parse_raw(raw, i)
        if isinstance(row, SyncResult):
            return row
            
        return self._process_row(row, progress_cb)

    def _skip_remaining(self, raw_rows, current_idx) -> List[SyncResult]:
        skipped = []
        for r in raw_rows[current_idx + 1:]:
            skipped.append(SyncResult(r[0], r[1], "", SyncStatus.SKIPPED, "auth failed"))
        return skipped

    def _parse_raw(self, r: List[str], i: int) -> Union[ReportRow, SyncResult]:
        if not r or len(r) < 3:
            return SyncResult("", f"Row {i}", "", SyncStatus.SKIPPED, "invalid row")
        return ReportRow(r[0], r[1], r[2], r[3] if len(r) > 3 else "")

    def _process_row(self, row: ReportRow, progress_cb: Optional[Callable] = None) -> Union[SyncResult, str]:
        try:
            dt = datetime.strptime(row.date_str, "%d.%m.%Y %H:%M")
        except:
            return SyncResult(row.date_str, row.name, "", SyncStatus.SKIPPED, "bad date")
            
        meta = get_course_name_by_date(dt, self.ctx.schedule)
        if not meta or isinstance(meta, str) or not meta.get("lms_course_id"):
            self.ctx.logger.warning(f"No LMS metadata for course: {row.name}")
            return SyncResult(row.date_str, row.name, "", SyncStatus.SKIPPED, "no lms meta")
            
        self.ctx.logger.info(f"Syncing to LMS Course: {row.name} (ID: {meta['lms_course_id']})")

        return self._sync(row, dt, meta, progress_cb)

    def _sync(self, row: ReportRow, dt: datetime, meta: Dict[str, Any], progress_cb: Optional[Callable] = None) -> Union[SyncResult, str]:
        try:
            ok, name, msg = self.lms.sync_video(
                self.ctx.config.get_school_id(), meta["lms_course_id"], dt, row.url
            )
            status = SyncStatus.PASS if ok else SyncStatus.FAIL
            details = "updated" if ok else msg
            
            res_str = "SUCCESS" if ok else f"FAILED: {msg}"
            self.ctx.logger.info(f"LMS Sync {res_str} for {row.name}")

            return SyncResult(row.date_str, row.name, name or "", status, details)
        except RuntimeError as e:
            if "LMS_AUTH_ERROR" in str(e):
                return "AUTH_ERROR"
            return SyncResult(row.date_str, row.name, "", SyncStatus.FAIL, str(e))
        except Exception as e:
            self.ctx.logger.error(f"LMS Error: {e}")
            return SyncResult(row.date_str, row.name, "", SyncStatus.FAIL, str(e))
