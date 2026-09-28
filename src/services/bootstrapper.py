import os
import tkinter as tk
from tkinter import messagebox
from src.core.path_manager import AppPaths
from src.constants import ERRORS

class Bootstrapper:
    @staticmethod
    def validate_gui_env(paths: AppPaths) -> bool:
        if os.path.exists(paths.secrets_file):
            return True
            
        root = tk.Tk()
        root.title("Критична помилка")
        root.geometry("560x240")
        root.lift()
        root.attributes("-topmost", True)

        header = tk.Label(root, text="Файл 'client_secret.json' не знайдено!", font=("Arial", 13, "bold"), fg="#c0392b")
        header.pack(padx=20, pady=(20, 10), anchor="w")

        msg = (
            f"Для роботи додатку потрібен ключ авторизації YouTube API.\n\n"
            f"Очікуване розташування файлу:\n{paths.secrets_file}\n\n"
            f"Будь ласка, помістіть ваш client_secret.json у цю папку та запустіть додаток знову."
        )
        msg_lbl = tk.Label(root, text=msg, font=("Arial", 11), justify="left", wraplength=520)
        msg_lbl.pack(padx=20, pady=(0, 15), anchor="w")

        btn = tk.Button(root, text="Зрозуміло", command=root.destroy, width=14, font=("Arial", 11))
        btn.pack(pady=(0, 15))

        root.mainloop()
        return False
