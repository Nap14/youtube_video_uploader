from typing import Optional
from .data.reportRow import ContentObject, Wrapper, Data, Button, Link
from .data.templates import get_video_button_template


class ContentService:

    def update_video(self, obj: dict, video_url: str) -> dict:
        parsed = ContentObject.model_validate(obj)

        existing_video_buttons = []
        empty_placeholder = None

        for wrapper in parsed.content:
            btn = self._get_button(wrapper)
            if not btn:
                continue

            curr_url = (btn.link.url or "").strip() if btn.link else ""
            if curr_url == video_url.strip():
                # Already present in the lesson! Avoid duplicates.
                return parsed.model_dump(exclude_none=True)

            label = (btn.label or "").strip()
            if label.startswith("Відео") or ("youtu.be" in curr_url or "youtube.com" in curr_url):
                if not curr_url and not empty_placeholder:
                    empty_placeholder = btn
                else:
                    existing_video_buttons.append(btn)

        if empty_placeholder:
            self._set_video_url(empty_placeholder, video_url)
            idx = len(existing_video_buttons) + 1
            empty_placeholder.label = f"Відео {idx}"
        elif not existing_video_buttons:
            parsed.content.append(self._create_video_button(video_url, label="Відео 1"))
        else:
            if existing_video_buttons[0].label == "Відео":
                existing_video_buttons[0].label = "Відео 1"

            new_label = f"Відео {len(existing_video_buttons) + 1}"
            parsed.content.append(self._create_video_button(video_url, label=new_label))

        return parsed.model_dump(exclude_none=True)

    def _get_button(self, wrapper: Wrapper) -> Optional[Button]:
        if not wrapper.element:
            return None
        if isinstance(wrapper.element.data, Data):
            return wrapper.element.data.button
        if isinstance(wrapper.element.data, dict) and "button" in wrapper.element.data:
            try:
                wrapper.element.data = Data.model_validate(wrapper.element.data)
                return wrapper.element.data.button
            except Exception:
                return None
        return None

    def _set_video_url(self, btn: Button, video_url: str):
        if not btn.link:
            btn.link = Link()
        btn.link.url = video_url

    def _create_video_button(self, video_url: str, label: str = "Відео") -> Wrapper:
        template = get_video_button_template(video_url, label=label)
        return Wrapper.model_validate(template)