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
        root.withdraw()
        messagebox.showerror("Critical Error", ERRORS['NO_SECRETS'])
        root.destroy()
        return False
