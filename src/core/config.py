import json
import os

class Config:
    def __init__(self, config_file, logger):
        self.config_file = config_file
        self.logger = logger
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Config error: {e}")
        return {}

    def get_data(self): 
        return self.data

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger.error(f"Save error: {e}")

    def get_zoom_dir(self): 
        return self.data.get("ZOOM_DIR")

    def get_lms_token(self): 
        return self.data.get("LMS_TOKEN")

    def get_school_id(self): 
        return self.data.get("SCHOOL_ID", "")

    def get_reports_dir(self):
        d = self.data.get("REPORTS_DIR", "reports")
        if not os.path.exists(d): os.makedirs(d, exist_ok=True)
        return d

    def get_planner_config(self):
        return self.data.get("PLANNER", {
            "enabled": False,
            "frequency": "daily", 
            "interval": 1,
            "time": "20:00",
            "day": "Monday",
            "mode": "1",
            "require_confirmation": True
        })

    def save_planner_config(self, config):
        self.data["PLANNER"] = config
        self.save()

