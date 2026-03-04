import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database  # Добавлен импорт

class AddPetDialog:
    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить питомца")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поля ввода
        ttk.Label(main_frame, text="Имя:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text="Вид:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.species_combo = ttk.Combobox(main_frame, values=["Собака", "Кошка", "Птица", "Грызун", "Рыбки", "Другое"], width=27)
        self.species_combo.grid(row=1, column=1, pady=5)
        self.species_combo.current(0)
        
        ttk.Label(main_frame, text="Порода:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.breed_entry = ttk.Entry(main_frame, width=30)
        self.breed_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(main_frame, text="Дата рождения (ГГГГ-ММ-ДД):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.birth_entry = ttk.Entry(main_frame, width=30)
        self.birth_entry.grid(row=3, column=1, pady=5)
        self.birth_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(main_frame, text="Пол:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.gender_var = tk.StringVar(value="М")
        ttk.Radiobutton(main_frame, text="М", variable=self.gender_var, value="М").grid(row=4, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Ж", variable=self.gender_var, value="Ж").grid(row=4, column=1, sticky=tk.E, padx=50)
        
        ttk.Label(main_frame, text="Особые отметки:").grid(row=5, column=0, sticky=tk.NW, pady=5)
        self.notes_text = tk.Text(main_frame, width=30, height=5)
        self.notes_text.grid(row=5, column=1, pady=5)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        name = self.name_entry.get().strip()
        species = self.species_combo.get()
        breed = self.breed_entry.get().strip()
        birth_date = self.birth_entry.get().strip()
        gender = self.gender_var.get()
        notes = self.notes_text.get(1.0, tk.END).strip()
        
        if not name:
            messagebox.showerror("Ошибка", "Введите имя питомца")
            return
        
        if not species:
            messagebox.showerror("Ошибка", "Выберите вид")
            return
        
        # Простая проверка формата даты
        try:
            datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        database.add_pet(self.user_id, name, species, breed, birth_date, gender, notes)
        self.dialog.destroy()