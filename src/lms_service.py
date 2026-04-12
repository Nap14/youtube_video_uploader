import requests

class LmsService:
    BASE_URL = "https://login.sendpulse.com/api/edu-service/api/v1"

    def __init__(self, token, logging_obj):
        self.token = token
        self.logging = logging_obj
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json"
        }

    def sync_video_to_lesson(self, school_id, course_id, recording_date, video_url):
        """
        Main method to sync a YouTube link to a specific lesson in SendPulse.
        Finds the lesson by date (dd.MM.yy) and updates/adds the "Відео" button.
        """
        if not self.token:
            self.logging.error("LMS Token missing. Skipping sync.")
            return False

        date_str = recording_date.strftime("%d.%m.%y")
        self.logging.info(f"Syncing to LMS: Course {course_id}, Date {date_str}")

        target_lesson = self.get_lesson_by_name(school_id, course_id, date_str)

        if not target_lesson:
            self.logging.warning(f"No lesson found in SendPulse containing date '{date_str}' for course {course_id}")
            return False

        lesson_id = target_lesson.get('id')
        self.logging.info(f"Found target lesson: '{target_lesson.get('name')}' (ID: {lesson_id})")

        lesson_content = self.get_lesson_content(school_id, course_id, lesson_id)
        if not lesson_content:
            self.logging.error(f"Could not retrieve content for lesson {lesson_id}")
            return False

        modified_lesson = self._update_lesson_content(lesson_content, video_url)
        
        update_url = f"{self.BASE_URL}/courses/{school_id}/{course_id}/lesson/{lesson_id}"
        try:
            put_body = {
                "id": lesson_id,
                "name": target_lesson.get('name'),
                "courseId": int(course_id),
                "sectionId": target_lesson.get('sectionId'),
                "content": modified_lesson['content'],
                "order": target_lesson.get('order'),
                "status": target_lesson.get('status', 'opened'),
                "startDate": target_lesson.get('startDate'),
                "intervalDate": target_lesson.get('intervalDate'),
                "timezone": target_lesson.get('timezone'),
                "isStopLesson": target_lesson.get('isStopLesson', False),
                "minCompletionTime": target_lesson.get('minCompletionTime')
            }

            res = requests.put(update_url, headers=self.headers, json=put_body)
            if res.status_code in [200, 204]:
                self.logging.info(f"Successfully updated lesson {lesson_id} with video link.")
                return True
            else:
                self.logging.error(f"Failed to update lesson {lesson_id}: {res.status_code}")
                self.logging.debug(res.text)
                return False
        except Exception as e:
            self.logging.error(f"Error updating LMS lesson: {e}")
            return False

    def _update_lesson_content(self, lesson_obj, video_url):
        """
        Searches for the 'Відео' button in lesson content.
        Updates it if found, or appends a new one if missing.
        """
        if not lesson_obj:
            return {"content": []}
            
        content = lesson_obj.get('content', [])
        if not isinstance(content, list):
            content = []

        button_found = False

        for element_wrapper in content:
            if not isinstance(element_wrapper, dict):
                continue
            element = element_wrapper.get('element', {})
            if not isinstance(element, dict):
                continue
                
            data = element.get('data', {})
            if not isinstance(data, dict):
                continue
                
            button = data.get('button', {})
            if not isinstance(button, dict):
                continue
                
            if button.get('label') == "Відео":
                if 'link' not in button:
                    button['link'] = {}
                button['link']['url'] = video_url
                button_found = True
                self.logging.info("Updating existing 'Відео' button link.")
                break

        if not button_found:
            self.logging.info("Adding new yellow 'Відео' button.")
            new_button = self._get_yellow_button_template(video_url)
            content.append(new_button)

        lesson_obj['content'] = content
        return lesson_obj

    def _get_yellow_button_template(self, video_url):
        """Returns the JSON structure for the yellow 'Відео' button as requested."""
        return {
            "id": "450e8b82-5e56-4ad7-9958-107d16d09360",
            "data": [],
            "styles": {
                "background": "#ffffff",
                "paddingTop": "10px",
                "paddingLeft": "10px",
                "borderRadius": "0px",
                "paddingRight": "10px",
                "paddingBottom": "15px"
            },
            "element": {
                "id": "76d6d818-fb97-4482-9908-89160584adba",
                "data": {
                    "button": {
                        "link": {
                            "url": video_url,
                            "type": "link",
                            "selectedTariffs": []
                        },
                        "size": "M",
                        "label": "Відео",
                        "styleType": "custom",
                        "widthType": "full",
                        "buttonBase": {
                            "color": ["#373737"],
                            "background": ["#ffed4f"],
                            "borderColor": ["rgba(255, 255, 255, 0)"],
                            "borderStyle": "solid",
                            "borderWidth": 2,
                            "borderRadius": 8
                        },
                        "widthValue": 260,
                        "description": None,
                        "isTargetBlank": True
                    },
                    "horizontalAlign": "L",
                    "horizontalIndent": "M"
                },
                "name": "button",
                "label": "widget_button_label"
            }
        }

    def get_lessons(self, school_id, course_id, *, content=False):
        """ Fetches lessons from SendPulse. Returns a list of objects. """
        lessons_url = f"{self.BASE_URL}/courses/{school_id}/{course_id}/lessons"
        if content:
            lessons_url += "/content"

        try:
            response = requests.get(lessons_url, headers=self.headers)
            if response.status_code == 401:
                self.logging.error("LMS Token expired or invalid! Please update it in config.json.")
                return []
            
            if response.status_code != 200:
                self.logging.error(f"Failed to fetch course {course_id} lessons: {response.status_code}")
                return []

            data = response.json()
            if isinstance(data, dict):
                return data.get('data', [])
            elif isinstance(data, list):
                return data
            return []

        except Exception as e:
            self.logging.error(f"Error fetching LMS lessons: {e}")
            return []

    def get_lesson_by_name(self, school_id, course_id, lesson_name):
        """ Searches for a lesson by checking if lesson_name is in its title. """
        sections = self.get_lessons(school_id, course_id, content=False)

        for section in reversed(sections):
            if not isinstance(section, dict): continue
            lessons = section.get('lessons', [])
            for lesson in reversed(lessons):
                if lesson_name in lesson.get('name', ''):
                    return lesson
        return None

    def get_lesson_content(self, school_id, course_id, lesson_id):
        """ Fetches content for a specific lesson by its ID. """
        lessons_with_content = self.get_lessons(school_id, course_id, content=True)

        for lesson in reversed(lessons_with_content):
            if lesson.get('id') == lesson_id:
                return lesson
        return None
