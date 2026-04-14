from typing import Optional
from .data.reportRow import ContentObject, Wrapper, Element, Data, Button, Link


class ContentService:

    def update_video(self, obj: dict, video_url: str) -> dict:
        parsed = ContentObject.model_validate(obj)

        for wrapper in parsed.content:
            btn = self._get_button(wrapper)

            if btn and btn.label == "Відео":
                self._set_video_url(btn, video_url)
                break
        else:
            parsed.content.append(self._create_video_button(video_url))

        return parsed.model_dump()

    def _get_button(self, wrapper: Wrapper) -> Optional[Button]:
        if not wrapper.element:
            return None
        if not wrapper.element.data:
            return None
        return wrapper.element.data.button

    def _set_video_url(self, btn: Button, video_url: str):
        if not btn.link:
            btn.link = Link()
        btn.link.url = video_url

    def _create_video_button(self, video_url: str) -> Wrapper:
        return Wrapper(
            element=Element(
                data=Data(
                    button=Button(
                        label="Відео",
                        link=Link(url=video_url)
                    )
                )
            )
        )