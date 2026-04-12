import json
import os
import tkinter as tk
from tkinter import filedialog

class Config:
    def __init__(self, config_file, logging):
        self.config_file = config_file
        self.logging = logging
        self.data = self._load()

    def get_data(self):
        return self.data

    def _load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logging.error(f"Error reading configuration: {e}")
        return {}

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            self.logging.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logging.error(f"Error saving configuration: {e}")

    def get_zoom_dir(self):
        zoom_dir = self.data.get("ZOOM_DIR")
        if not zoom_dir:
            
            self.logging.info("First run: Opening folder selection dialog...")
            
            root = tk.Tk()
            root.withdraw() 
            root.attributes('-topmost', True)
            
            zoom_dir = filedialog.askdirectory(title="Select folder with Zoom recordings")
            root.destroy()

            if not zoom_dir:
                self.logging.error("No folder selected. Portability setup aborted.")
                return None
            
            if not os.path.exists(zoom_dir):
                self.logging.error(f"Selected path '{zoom_dir}' does not exist.")
                return None

            self.data["ZOOM_DIR"] = zoom_dir
            self.save()
            
        return zoom_dir

    def get_lms_token(self):
        return self.data.get("LMS_TOKEN")

    def get_reports_dir(self):
        reports_dir = self.data.get("REPORTS_DIR", "reports")
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir, exist_ok=True)
        return reports_dir

    def get_school_id(self):
        return self.data.get("SCHOOL_ID", "18828")
