import json
import os

class Config:
    def __init__(self, config_file, logging):
        self.config_file = config_file
        self.logging = logging
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logging.error(f"Помилка при читанні конфігурації: {e}")
        return {}

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            self.logging.info(f"Конфігурацію збережено у {self.config_file}")
        except Exception as e:
            self.logging.error(f"Помилка при збереженні конфігурації: {e}")

    def get_zoom_dir(self):
        zoom_dir = self.data.get("ZOOM_DIR")
        if not zoom_dir:
            print("\n" + "="*50)
            print("ПЕРШИЙ ЗАПУСК - НАЛАШТУВАННЯ")
            print("="*50)
            zoom_dir = input("Введіть повний шлях до папки з відео Zoom (наприклад, D:\\зум): ").strip().strip('"')
            
            while not zoom_dir or not os.path.exists(zoom_dir):
                print(f"Помилка: Шлях '{zoom_dir}' не існує або порожній.")
                zoom_dir = input("Будь ласка, введіть коректний шлях: ").strip().strip('"')
            
            self.data["ZOOM_DIR"] = zoom_dir
            self.save()
            print("="*50 + "\n")
            
        return zoom_dir
