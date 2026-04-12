import requests
from .templates import get_yellow_button_template

class LmsService:
    BASE_URL = "https://login.sendpulse.com/api/edu-service/api/v1"

    def __init__(self, token, logger):
        self.token, self.logger = token, logger
        self.headers = {"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json"}

    def sync_video(self, school_id, course_id, date, video_url):
        date_str = date.strftime("%d.%m.%y")
        target = self.get_lesson_by_name(school_id, course_id, date_str)
        if not target: return False

        lesson_id = target.get('id')
        lesson_obj = self.get_lesson_content(school_id, course_id, lesson_id)
        if not lesson_obj: return False

        modified = self._update_content(lesson_obj, video_url)
        url = f"{self.BASE_URL}/courses/{school_id}/{course_id}/lesson/{lesson_id}"
        body = {**target, "content": modified['content'], "courseId": int(course_id)}
        
        res = requests.put(url, headers=self.headers, json=body)
        return res.status_code in [200, 204]

    def _update_content(self, lesson_obj, video_url):
        content = lesson_obj.get('content', [])
        found = False
        for wrapper in content:
            btn = wrapper.get('element', {}).get('data', {}).get('button', {})
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
            return res.json().get('data', []) if res.status_code == 200 else []
        except: return []

    def get_lesson_by_name(self, sid, cid, name):
        for sec in reversed(self.get_lessons(sid, cid)):
            for les in reversed(sec.get('lessons', [])):
                if name in les.get('name', ''): return les
        return None

    def get_lesson_content(self, sid, cid, lid):
        for les in reversed(self.get_lessons(sid, cid, content=True)):
            if les.get('id') == lid: return les
        return None
