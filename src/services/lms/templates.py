def get_yellow_button_template(video_url):
    return {
        "id": "450e8b82-5e56-4ad7-9958-107d16d09360",
        "data": [],
        "styles": {"background": "#ffffff", "paddingTop": "10px", "paddingLeft": "10px", "borderRadius": "0px", "paddingRight": "10px", "paddingBottom": "15px"},
        "element": {
            "id": "76d6d818-fb97-4482-9908-89160584adba",
            "data": {
                "button": {
                    "link": {"url": video_url, "type": "link", "selectedTariffs": []},
                    "size": "M", "label": "Відео", "styleType": "custom", "widthType": "full",
                    "buttonBase": {"color": ["#373737"], "background": ["#ffed4f"], "borderColor": ["rgba(255, 255, 255, 0)"], "borderStyle": "solid", "borderWidth": 2, "borderRadius": 8},
                    "widthValue": 260, "description": None, "isTargetBlank": True
                },
                "horizontalAlign": "L", "horizontalIndent": "M"
            },
            "name": "button", "label": "widget_button_label"
        }
    }
