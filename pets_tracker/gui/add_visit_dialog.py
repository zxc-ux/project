import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database  # Добавлен импорт

class AddVisitDialog:
    def __init__(self, parent, pet_id):
        self.pet_id = pet_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить визит к ветеринару")
        self.dialog.geometry("400x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Дата визита:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(main_frame, width=30)
        self.date_entry.grid(row=0, column=1, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(main_frame, text="Причина:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.reason_entry = ttk.Entry(main_frame, width=30)
        self.reason_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(main_frame, text="Диагноз:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.diagnosis_entry = ttk.Entry(main_frame, width=30)
        self.diagnosis_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(main_frame, text="Рекомендации:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.recommendations_text = tk.Text(main_frame, width=30, height=5)
        self.recommendations_text.grid(row=3, column=1, pady=5)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        visit_date = self.date_entry.get().strip()
        reason = self.reason_entry.get().strip()
        diagnosis = self.diagnosis_entry.get().strip()
        recommendations = self.recommendations_text.get(1.0, tk.END).strip()
        
        try:
            datetime.strptime(visit_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return
        
        database.add_vet_visit(self.pet_id, visit_date, reason, diagnosis, recommendations)
        self.dialog.destroy()