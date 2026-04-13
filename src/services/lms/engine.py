from src.core.config import Config
from src.services.lms.service import LmsService
from src.services.schedule_utils import get_course_name_by_date
from datetime import datetime
from typing import List, Union, Callable, Optional

from .data.reportRow import ReportRow, SyncResult
from .data.status import SyncStatus

class LmsProcessor:
    def __init__(self, lms_service: LmsService, config: Config, schedule: dict, logger, error_cb: Optional[Callable[[str, str], None]] = None):
        self.lms = lms_service
        self.config = config
        self.schedule = schedule
        self.logger = logger
        self.error_cb = error_cb

    def process(self, raw_rows, progress_cb=None):
        rows = [self._parse_raw_row(r, i) for i, r in enumerate(raw_rows)]
        results: List[SyncResult] = []

        for i, row in enumerate(rows):
            if isinstance(row, SyncResult):
                results.append(row)
                continue

            if progress_cb:
                progress_cb(f"LMS Sync: {row.name}", (i + 1, len(rows)))

            result = self._process_row(row)

            if result == "AUTH_ERROR":
                results.extend(self._skip_remaining(rows[i + 1:]))
                if self.error_cb:
                    self.error_cb("LMS Authentication Error", "LMS authentication failed. Please set LMS token on settings")
                break

            results.append(result)

        return [r.to_list() for r in results]

    def _process_row(self, row: ReportRow) -> Union[SyncResult, str]:
        rec_date = self._parse_date(row)
        if isinstance(rec_date, SyncResult):
            return rec_date

        meta = self._get_meta(row, rec_date)
        if isinstance(meta, SyncResult):
            return meta

        return self._sync(row, rec_date, meta)

    def _parse_raw_row(self, row, i) -> Union[ReportRow, SyncResult]:
        if not row or len(row) < 4:
            self.logger.warning(f"Invalid row {i}: {row}")
            return SyncResult("", "", "", SyncStatus.SKIPPED, "invalid row")

        date_str, name, url, status, *_ = row

        if not url:
            return SyncResult(date_str, name, "", SyncStatus.SKIPPED, "missing url")

        return ReportRow(date_str, name, url, status)

    def _parse_date(self, row: ReportRow) -> Union[datetime, SyncResult]:
        try:
            return datetime.strptime(row.date_str, "%d.%m.%Y %H:%M")
        except Exception:
            self.logger.warning(f"Invalid date: {row.date_str}")
            return SyncResult(row.date_str, row.name, "", SyncStatus.SKIPPED, "invalid date format")

    def _get_meta(self, row: ReportRow, rec_date: datetime):
        meta = get_course_name_by_date(rec_date, self.schedule)

        if not meta or isinstance(meta, str):
            return SyncResult(row.date_str, row.name, "", SyncStatus.SKIPPED, "lesson not found in schedule")

        if not meta.get("lms_course_id"):
            return SyncResult(row.date_str, row.name, "", SyncStatus.SKIPPED, "missing lms id")

        return meta

    def _sync(self, row: ReportRow, rec_date: datetime, meta) -> Union[SyncResult, str]:
        try:
            ok, actual_name, details = self.lms.sync_video(self.config.get_school_id(), meta.get("lms_course_id"), rec_date, row.url)
            
            actual_name = actual_name or ""
            details = "successfully updated" if ok else details
            status = SyncStatus.PASS if ok else SyncStatus.FAIL
            return SyncResult(row.date_str, row.name, actual_name, status, details)

        except RuntimeError as e:
            if "LMS_AUTH_ERROR" in str(e):
                self.logger.error(str(e))
                return "AUTH_ERROR"

            return SyncResult(row.date_str, row.name, "", SyncStatus.FAIL, str(e))

        except Exception as e:
            self.logger.error(f"Critical error: {e}")
            return SyncResult(row.date_str, row.name, "", SyncStatus.FAIL, f"unknown error: {e}")

    def _skip_remaining(self, rows):
        results = []
        for r in rows:
            if isinstance(r, ReportRow):
                results.append(SyncResult(r.date_str, r.name, "", SyncStatus.SKIPPED, "authentication failed"))

        return results

