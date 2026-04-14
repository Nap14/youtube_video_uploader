import requests
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import Logger
from .content_service import ContentService


class LmsService:
    BASE_URL = "https://login.sendpulse.com/api/edu-service/api/v1"

    def __init__(self, token: str, logger: Logger):
        self.token = token
        self.logger = logger
        self.content_service = ContentService()

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def sync_video(
        self,
        school_id: str,
        course_id: str,
        date: datetime,
        video_url: str,
    ) -> Tuple[bool, Optional[str], str]:

        d_str = date.strftime("%d.%m.%y")
        self.logger.info(f"Searching lesson '{d_str}'")

        lesson = self.get_lesson_by_name(school_id, course_id, d_str)
        if not lesson:
            return False, None, "lesson not found"

        name = lesson.get("name", "N/A")
        lesson_id = lesson.get("id")

        lesson_obj = self.get_lesson_content(school_id, course_id, lesson_id)
        if not lesson_obj:
            return False, name, "failed to load content"

        updated = self.content_service.update_video(lesson_obj, video_url)

        url = f"{self.BASE_URL}/courses/{school_id}/{course_id}/lesson/{lesson_id}"
        body = {
            **lesson,
            "content": updated["content"],
            "courseId": int(course_id),
        }

        res = requests.put(url, headers=self.headers, json=body)
        self._log_call("PUT", url, res)

        success = res.status_code in (200, 204)
        return success, name, "updated" if success else f"API Error {res.status_code}"

    def get_lessons(self, sid: str, cid: str, content: bool = False) -> List[Any]:
        url = f"{self.BASE_URL}/courses/{sid}/{cid}/lessons"
        if content:
            url += "/content"

        try:
            res = requests.get(url, headers=self.headers)
            self._log_call("GET", url, res)

            if res.status_code != 200:
                return []

            data = res.json()
            return data if isinstance(data, list) else data.get("data", [])

        except Exception as e:
            if "LMS_AUTH_ERROR" in str(e):
                raise e
            self.logger.error(f"LMS connection error: {e}")
            return []

    def get_lesson_by_name(
        self, sid: str, cid: str, name: str
    ) -> Optional[Dict[str, Any]]:

        for sec in reversed(self.get_lessons(sid, cid)):
            if not isinstance(sec, dict):
                continue

            for les in reversed(sec.get("lessons", [])):
                if not isinstance(les, dict):
                    continue

                if name in (les.get("name") or ""):
                    return les

        return None

    def get_lesson_content(
        self, sid: str, cid: str, lid: Any
    ) -> Optional[Dict[str, Any]]:

        for les in reversed(self.get_lessons(sid, cid, content=True)):
            if isinstance(les, dict) and les.get("id") == lid:
                return les

        return None

    def _log_call(self, method: str, url: str, res: requests.Response):
        status = res.status_code

        if status in (401, 403):
            err = "LMS_AUTH_ERROR: Update LMS token"
            self.logger.error(err)
            raise RuntimeError(err)

        if status < 400:
            self.logger.info(f"{method} {url} | {status}")
        else:
            self.logger.error(f"{method} {url} | {status} | {res.text[:300]}")