import json
import os
from typing import Any, Dict

from src.core.logger import Logger

_DEFAULT_CONFIG = {
    "ZOOM_DIR": "",
    "LMS_TOKEN": "",
    "SCHOOL_ID": "",
    "REPORTS_DIR": "reports"
}

class Config:
    def __init__(self, config_file: str, logger: Logger = None):
        self.config_file = config_file
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(config_file)))
        self.logger = logger
        self._ensure_defaults()
        self.data = self._load()

    def _ensure_defaults(self):
        """Create config.json with safe defaults if it doesn't exist."""
        if os.path.exists(self.config_file):
            return
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(_DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self._log_error(f"Cannot create default config: {e}")

    def _log_error(self, msg: str):
        if hasattr(self.logger, 'error') and callable(self.logger.error):
            self.logger.error(msg)
        else:
            print(f"[ERROR] {msg}")

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_file):
            return {}
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self._log_error(f"Config error: {e}")
            return {}

    def get_data(self): 
        return self.data

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self._log_error(f"Save error: {e}")

    def get_zoom_dir(self): 
        return self.data.get("ZOOM_DIR")

    def get_lms_token(self) -> str: 
        token = self.data.get("LMS_TOKEN")
        if not token:
            raise ValueError("Missing LMS token")
        return token

    def get_school_id(self): 
        return self.data.get("SCHOOL_ID", "")

    def get_reports_dir(self) -> str:
        d = self.data.get("REPORTS_DIR", "reports")
        if not os.path.isabs(d) and self.base_dir:
            d = os.path.join(self.base_dir, d)
        if not os.path.exists(d): 
            try:
                os.makedirs(d, exist_ok=True)
            except Exception as e:
                self._log_error(f"Cannot create reports dir {d}: {e}")
        return d

    def get_planner_config(self) -> Dict[str, Any]:
        return self.data.get("PLANNER", {
            "enabled": False,
            "frequency": "daily", 
            "interval": 1,
            "time": "20:00",
            "day": "Monday",
            "mode": "1",
            "require_confirmation": True
        })

    def save_planner_config(self, config: Dict[str, Any]):
        self.data["PLANNER"] = config
        self.save()
