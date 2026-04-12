import customtkinter as ctk
import csv
import os

class ReportTableModal(ctk.CTkToplevel):
    def __init__(self, master, file_path, **kwargs):
        super().__init__(master, **kwargs)
        self.title(f"Viewing: {os.path.basename(file_path)}")
        self.geometry("900x500")
        self.transient(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.container = ctk.CTkScrollableFrame(self)
        self.container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.load_data(file_path)

    def load_data(self, path):
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                data = list(csv.reader(f))
                
            if not data: return
            
            # Setup columns based on first row
            cols = len(data[0])
            self.container.grid_columnconfigure(list(range(cols)), weight=1)
            
            for r, row in enumerate(data):
                for c, val in enumerate(row):
                    weight = "bold" if r == 0 else "normal"
                    fg = ("gray85", "gray25") if r == 0 else "transparent"
                    
                    # Highlights
                    txt_color = ("black", "white")
                    if "Success" in val: txt_color = "#27ae60"
                    elif "Error" in val or "Failed" in val: txt_color = "#e74c3c"
                    elif "Skipped" in val: txt_color = "#f39c12"

                    lbl = ctk.CTkLabel(self.container, text=val, font=ctk.CTkFont(size=12, weight=weight), 
                                       text_color=txt_color, fg_color=fg, padx=10, pady=5, anchor="w")
                    lbl.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
        except Exception as e:
            ctk.CTkLabel(self.container, text=f"Error loading report: {e}").pack()
