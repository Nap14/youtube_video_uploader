import customtkinter as ctk
import csv
import os

class ReportTableModal(ctk.CTkToplevel):
    def __init__(self, master, file_path, **kwargs):
        super().__init__(master, **kwargs)
        self.file_path = file_path
        self.title(f"Viewing: {os.path.basename(file_path)}")
        self.geometry("950x500")
        self.transient(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.refresh()

    def refresh(self):
        for c in self.winfo_children():
            if isinstance(c, ctk.CTkScrollableFrame): c.destroy()
            
        self.container = ctk.CTkScrollableFrame(self)
        self.container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.load_data()

    def load_data(self):
        if not self.file_path.lower().endswith(".csv"):
            ctk.CTkLabel(self.container, text="Error: Unsupported file format. Only .csv is supported.").pack(pady=20)
            return
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as f:
                self.data = list(csv.reader(f))
            if not self.data or len(self.data[0]) < 2:
                ctk.CTkLabel(self.container, text="Error: Invalid or empty report format.").pack(pady=20)
                return
            
            cols = len(self.data[0])
            self.container.grid_columnconfigure(list(range(cols + 1)), weight=1)
            
            for r, row in enumerate(self.data):
                for c, val in enumerate(row):
                    txt_color = ("black", "white")
                    val_lower = val.lower()
                    if val_lower == "pass" or "success" in val: txt_color = "#27ae60"
                    elif val_lower == "fail" or "error" in val or "failed" in val: txt_color = "#e74c3c"
                    elif val_lower == "skipped": txt_color = "#f39c12"

                    lbl = ctk.CTkLabel(self.container, text=val, font=ctk.CTkFont(size=11, weight="bold" if r==0 else "normal"), 
                                       text_color=txt_color, fg_color=("gray85", "gray25") if r==0 else "transparent", 
                                       padx=10, pady=5, anchor="w")
                    lbl.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                
                if r > 0:
                    btn = ctk.CTkButton(self.container, text="X", width=30, height=22, fg_color="#e74c3c", 
                                        command=lambda idx=r: self.delete_row(idx))
                    btn.grid(row=r, column=cols, padx=5)
                else:
                    ctk.CTkLabel(self.container, text="Action", font=ctk.CTkFont(weight="bold")).grid(row=0, column=cols)
        except Exception as e:
            ctk.CTkLabel(self.container, text=f"Error: {e}").pack()

    def delete_row(self, index):
        from tkinter import messagebox
        if messagebox.askyesno("Confirm", "Remove this record from report?"):
            self.data.pop(index)
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerows(self.data)
            self.refresh()
