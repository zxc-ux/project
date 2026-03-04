import tkinter as tk
from tkinter import ttk, messagebox
import database  # Добавлен импорт

class SettingsDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройки напоминаний")
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        current_days = database.get_reminder_days()
        
        ttk.Label(main_frame, text="Напоминать за сколько дней:").pack(pady=10)
        
        self.days_var = tk.IntVar(value=current_days)
        self.days_spinbox = ttk.Spinbox(main_frame, from_=1, to=30, textvariable=self.days_var, width=10)
        self.days_spinbox.pack(pady=5)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        days = self.days_var.get()
        database.set_reminder_days(days)
        messagebox.showinfo("Успех", "Настройки сохранены")
        self.dialog.destroy()