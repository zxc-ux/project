import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import database  # Добавлен импорт

class AddVaccinationDialog:
    def __init__(self, parent, pet_id):
        self.pet_id = pet_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить прививку")
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Название вакцины:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text="Дата введения:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(main_frame, width=30)
        self.date_entry.grid(row=1, column=1, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(main_frame, text="Следующая дата:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.next_entry = ttk.Entry(main_frame, width=30)
        self.next_entry.grid(row=2, column=1, pady=5)
        
        # Подсказка
        next_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        self.next_entry.insert(0, next_date)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        name = self.name_entry.get().strip()
        date_given = self.date_entry.get().strip()
        next_due = self.next_entry.get().strip()
        
        if not name:
            messagebox.showerror("Ошибка", "Введите название вакцины")
            return
        
        try:
            datetime.strptime(date_given, "%Y-%m-%d")
            if next_due:
                datetime.strptime(next_due, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return
        
        database.add_vaccination(self.pet_id, name, date_given, next_due)
        self.dialog.destroy()