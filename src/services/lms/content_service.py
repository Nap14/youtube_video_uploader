from typing import Optional
from .data.reportRow import ContentObject, Wrapper, Data, Button, Link
from .data.templates import get_video_button_template


class ContentService:

    def update_video(self, obj: dict, video_url: str) -> dict:
        parsed = ContentObject.model_validate(obj)

        video_button_found = False
        for wrapper in parsed.content:
            btn = self._get_button(wrapper)
            if btn and btn.label == "Відео":
                self._set_video_url(btn, video_url)
                video_button_found = True
                break
        
        if not video_button_found:
            parsed.content.append(self._create_video_button(video_url))

        return parsed.model_dump(exclude_none=True)

    def _get_button(self, wrapper: Wrapper) -> Optional[Button]:
        if not wrapper.element:
            return None
        if not isinstance(wrapper.element.data, Data):
            if isinstance(wrapper.element.data, dict) and "button" in wrapper.element.data:
                button_data = wrapper.element.data.get("button")
                if isinstance(button_data, dict):
                    return Button.model_validate(button_data)
            return None
        return wrapper.element.data.button

    def _set_video_url(self, btn: Button, video_url: str):
        if not btn.link:
            btn.link = Link()
        btn.link.url = video_url

    def _create_video_button(self, video_url: str) -> Wrapper:
        template = get_video_button_template(video_url)
        return Wrapper.model_validate(template)