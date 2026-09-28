import customtkinter as ctk
import os
import sys
from PIL import Image

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, switch_cmd, **kwargs):
        super().__init__(master, **kwargs)
        self.switch_cmd = switch_cmd
        self.grid_rowconfigure(5, weight=1)
        self.load_icons()
        self.create_widgets()

    def load_icons(self):
        def _get_icon(name):
            search_dirs = [
                getattr(sys, '_MEIPASS', ''),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
                os.getcwd()
            ]
            for b in search_dirs:
                if not b:
                    continue
                p = os.path.join(b, "assets", "icons", f"{name}.png")
                if os.path.exists(p):
                    try:
                        img = Image.open(p)
                        return ctk.CTkImage(light_image=img, dark_image=img, size=(20, 20))
                    except Exception:
                        pass
            return None
        
        self.icons = {
            "dashboard": _get_icon("dashboard"),
            "schedule": _get_icon("schedule"),
            "reports": _get_icon("reports"),
            "planner": _get_icon("planner"),
            "settings": _get_icon("settings")
        }

    def create_widgets(self):
        self.logo_label = ctk.CTkLabel(self, text="ZOOM UPLOADER", font=ctk.CTkFont(size=14, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=10, pady=(20, 20))
        
        main_btns = [("Dashboard", "dashboard"), ("Weekly Schedule", "schedule"), 
                     ("Reports History", "reports"), ("Automation Planner", "planner")]
        
        self.buttons = {}
        for i, (text, name) in enumerate(main_btns):
            btn = self._create_btn(text, name)
            btn.grid(row=i+1, column=0, sticky="ew")
            self.buttons[name] = btn

        settings_btn = self._create_btn("General Settings", "settings")
        settings_btn.grid(row=10, column=0, padx=0, pady=(0, 20), sticky="ew")
        self.buttons["settings"] = settings_btn

    def _create_btn(self, text, name):
        btn = ctk.CTkButton(self, corner_radius=0, height=45, border_spacing=10, text=text,
                            fg_color="transparent", text_color=("gray10", "gray90"), 
                            hover_color=("gray70", "gray30"), anchor="w",
                            command=lambda n=name: self.switch_cmd(n))
        if name in self.icons and self.icons[name] is not None:
            btn.configure(image=self.icons[name])
        return btn

    def highlight_button(self, name):
        for n, btn in self.buttons.items():
            btn.configure(fg_color=("gray75", "gray25") if n == name else "transparent")
