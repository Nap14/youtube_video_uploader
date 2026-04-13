import requests
import json
from .templates import get_yellow_button_template

class LmsService:
    BASE_URL = "https://login.sendpulse.com/api/edu-service/api/v1"

    def __init__(self, token, logger):
        self.token, self.logger = token, logger
        self.headers = {"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json"}

    def _log_call(self, method, url, res, payload=None):
        """Verbose logging for debugging API issues."""
        status = res.status_code
        body = res.text[:1000]
        log_msg = f"LMS API {method} {url} | Status: {status}"
        if status >= 400:
            log_msg += f"\nResponse: {body}"
        
        if status in [401, 403]:
            err_msg = "LMS_AUTH_ERROR: you need to update the LMS token in settings"
            self.logger.error(f"CRITICAL: {err_msg}")
            raise RuntimeError(err_msg)
        
        if status < 400:
            self.logger.info(f"LMS API {method} {url} | Status: {status} - Success")
        else:
            self.logger.error(log_msg)

    def sync_video(self, school_id, course_id, date, video_url):
        date_str = date.strftime("%d.%m.%y")
        self.logger.info(f"Searching for lesson '{date_str}' in LMS...")
        target = self.get_lesson_by_name(school_id, course_id, date_str)
        if not target: 
            return False, None, "lesson not found"

        actual_name = target.get('name', 'N/A')
        self.logger.info(f"Found LMS lesson: '{actual_name}'. Matching content...")
        lesson_id = target.get('id')
        lesson_obj = self.get_lesson_content(school_id, course_id, lesson_id)
        if not lesson_obj: 
            return False, actual_name, "failed to load lesson content"

        modified = self._update_content(lesson_obj, video_url)
        url = f"{self.BASE_URL}/courses/{school_id}/{course_id}/lesson/{lesson_id}"
        body = {**target, "content": modified['content'], "courseId": int(course_id)}
        
        res = requests.put(url, headers=self.headers, json=body)
        self._log_call("PUT", url, res, payload=body)
        
        success = res.status_code in [200, 204]
        return success, actual_name, "successfully updated" if success else f"API Error {res.status_code}"

    def _update_content(self, lesson_obj, video_url):
        content = lesson_obj.get('content', [])
        found = False
        for wrapper in content:
            if not isinstance(wrapper, dict): continue
            
            elem = wrapper.get('element', {})
            if not isinstance(elem, dict): continue
            
            data = elem.get('data', {})
            if not isinstance(data, dict): continue
                
            btn = data.get('button', {})
            if not isinstance(btn, dict): continue
            
            if btn.get('label') == "Відео":
                if 'link' not in btn: btn['link'] = {}
                btn['link']['url'] = video_url
                found = True; break
        if not found: content.append(get_yellow_button_template(video_url))
        lesson_obj['content'] = content
        return lesson_obj

    def get_lessons(self, school_id, course_id, content=False):
        url = f"{self.BASE_URL}/courses/{school_id}/{course_id}/lessons"
        if content: url += "/content"
        try:
            res = requests.get(url, headers=self.headers)
            self._log_call("GET", url, res)
            if res.status_code != 200: return []
            data = res.json()
            return data if isinstance(data, list) else data.get('data', [])
        except Exception as e:
            if "LMS_AUTH_ERROR" in str(e): raise e
            self.logger.error(f"LMS connection error: {e}")
            return []

    def get_lesson_by_name(self, sid, cid, name):
        lessons_data = self.get_lessons(sid, cid)
        for sec in reversed(lessons_data):
            if not isinstance(sec, dict): continue
            for les in reversed(sec.get('lessons', [])):
                if not isinstance(les, dict): continue
                if name in (les.get('name') or ''): return les
        return None

    def get_lesson_content(self, sid, cid, lid):
        contents = self.get_lessons(sid, cid, content=True)
        for les in reversed(contents):
            if not isinstance(les, dict): continue
            if les.get('id') == lid: return les
        return None
