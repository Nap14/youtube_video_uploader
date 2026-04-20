import uuid

def get_video_button_template(video_url: str) -> dict:
    """Генерує словник зі структурою кнопки відео для SendPulse LMS."""
    return {
        "id": str(uuid.uuid4()),
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
            "id": str(uuid.uuid4()),
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
