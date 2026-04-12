import customtkinter as ctk

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, start_command, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.start_command = start_command
        self.create_widgets()

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text="Automation Control", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")
        
        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.grid(row=1, column=0, padx=30, pady=10, sticky="w")
        
        self.mode_var = ctk.StringVar(value="1")
        modes = [("Full Auto", "1"), ("YouTube Only", "2"), ("LMS Sync Only", "3")]
        for i, (text, val) in enumerate(modes):
            ctk.CTkRadioButton(self.mode_frame, text=text, variable=self.mode_var, value=val).grid(row=0, column=i, padx=20)

        self.btn_container = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_container.grid(row=2, column=0, padx=30, pady=20, sticky="ew")
        self.btn_container.grid_columnconfigure(0, weight=1)
        
        self.start_btn = ctk.CTkButton(self.btn_container, text="START AUTOMATION", height=50, width=300, 
                                       command=self.start_command, font=ctk.CTkFont(size=14, weight="bold"))
        self.start_btn.grid(row=0, column=0)
        
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=3, column=0, padx=30, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        self.log_text = ctk.CTkTextbox(self, height=250)
        self.log_text.grid(row=4, column=0, padx=30, pady=10, sticky="nsew")
