import csv
import os
import customtkinter as ctk
from tkinter import messagebox

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
            if isinstance(c, ctk.CTkScrollableFrame):
                c.destroy()
            
        self.container = ctk.CTkScrollableFrame(self)
        self.container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.load_data()

    def load_data(self):
        if not self.file_path.lower().endswith(".csv"):
            ctk.CTkLabel(self.container, text="Only .csv is supported.").pack(pady=20)
            return
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as f:
                self.data = list(csv.reader(f))
            if not self.data or len(self.data[0]) < 2:
                ctk.CTkLabel(self.container, text="Error: empty report format.").pack(pady=20)
                return
            
            self._render_table()
        except Exception as e:
            ctk.CTkLabel(self.container, text=f"Error: {e}").pack()

    def _render_table(self):
        cols = len(self.data[0])
        self.container.grid_columnconfigure(list(range(cols + 1)), weight=1)
        
        for r, row in enumerate(self.data):
            for c, val in enumerate(row):
                self._render_cell(r, c, val)
            
            if r > 0:
                self._add_action_button(r, cols)
            else:
                ctk.CTkLabel(self.container, text="Action", font=ctk.CTkFont(weight="bold")).grid(row=0, column=cols)

    def _render_cell(self, r, c, val):
        txt_color = ("black", "white")
        v_low = val.lower()
        if v_low == "pass" or "success" in v_low:
            txt_color = "#27ae60"
        elif v_low == "fail" or "error" in v_low or "failed" in v_low:
            txt_color = "#e74c3c"
        elif v_low == "skipped":
            txt_color = "#f39c12"

        lbl = ctk.CTkLabel(
            self.container, text=val, font=ctk.CTkFont(size=11, weight="bold" if r==0 else "normal"), 
            text_color=txt_color, fg_color=("gray85", "gray25") if r==0 else "transparent", 
            padx=10, pady=5, anchor="w"
        )
        lbl.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)

    def _add_action_button(self, r, cols):
        btn = ctk.CTkButton(
            self.container, text="X", width=30, height=22, fg_color="#e74c3c", 
            command=lambda idx=r: self.delete_row(idx)
        )
        btn.grid(row=r, column=cols, padx=5)

    def delete_row(self, index):
        if messagebox.askyesno("Confirm", "Remove this record?"):
            self.data.pop(index)
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerows(self.data)
            self.refresh()
