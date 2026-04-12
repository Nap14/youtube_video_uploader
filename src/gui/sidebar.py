import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, switch_cmd, **kwargs):
        super().__init__(master, **kwargs)
        self.switch_cmd = switch_cmd
        self.grid_rowconfigure(5, weight=1)
        self.create_widgets()

    def create_widgets(self):
        self.logo_label = ctk.CTkLabel(self, text="ZOOM UPLOADER", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        btns = [("Dashboard", "dashboard"), ("Weekly Schedule", "schedule"), 
                ("Reports", "reports"), ("Planner", "planner"), ("Settings", "settings")]
        
        self.buttons = {}
        for i, (text, name) in enumerate(btns):
            btn = ctk.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text=text,
                                fg_color="transparent", text_color=("gray10", "gray90"), 
                                hover_color=("gray70", "gray30"), anchor="w",
                                command=lambda n=name: self.switch_cmd(n))
            btn.grid(row=i+1, column=0, sticky="ew")
            self.buttons[name] = btn

    def highlight_button(self, name):
        for n, btn in self.buttons.items():
            btn.configure(fg_color=("gray75", "gray25") if n == name else "transparent")
