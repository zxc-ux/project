import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3  # Добавлен недостающий импорт
import database
from gui.add_pet_dialog import AddPetDialog
from gui.add_vaccination_dialog import AddVaccinationDialog
from gui.add_visit_dialog import AddVisitDialog
from gui.settings_dialog import SettingsDialog
from utils import calculate_age, check_reminders

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Мои питомцы")
        self.root.geometry("900x600")
        
        # Для примера используем user_id=1 (первый пользователь)
        # В реальном проекте нужно передавать ID текущего пользователя
        self.current_user_id = 1
        self.current_pet_id = None
        
        self.setup_menu()
        self.setup_ui()
        self.load_pets()
        
        # Проверяем напоминания при запуске
        self.check_reminders_on_startup()
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новое животное", command=self.add_pet, accelerator="Ctrl+N")
        file_menu.add_command(label="Удалить животное", command=self.delete_pet)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню Записи
        records_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Записи", menu=records_menu)
        records_menu.add_command(label="Новая прививка", command=self.add_vaccination, accelerator="Ctrl+V")
        records_menu.add_command(label="Новый визит к ветеринару", command=self.add_visit, accelerator="Ctrl+W")
        
        # Меню Напоминания
        reminders_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Напоминания", menu=reminders_menu)
        reminders_menu.add_command(label="Настроить", command=self.open_settings)
        reminders_menu.add_command(label="Проверить сейчас", command=self.check_reminders)
        
        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        
        # Горячие клавиши
        self.root.bind('<Control-n>', lambda e: self.add_pet())
        self.root.bind('<Control-v>', lambda e: self.add_vaccination())
        self.root.bind('<Control-w>', lambda e: self.add_visit())
    
    def setup_ui(self):
        # Верхняя панель с выбором питомца
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Выберите питомца:").pack(side=tk.LEFT)
        self.pet_combo = ttk.Combobox(top_frame, state="readonly", width=30)
        self.pet_combo.pack(side=tk.LEFT, padx=10)
        self.pet_combo.bind('<<ComboboxSelected>>', self.on_pet_selected)
        
        # Создаём вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка "Профиль"
        self.profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_frame, text="Профиль")
        self.setup_profile_tab()
        
        # Вкладка "История"
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="История")
        self.setup_history_tab()
        
        # Вкладка "Напоминания"
        self.reminders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reminders_frame, text="Напоминания")
        self.setup_reminders_tab()
    
    def setup_profile_tab(self):
        # Создаём форму для редактирования профиля
        main_frame = ttk.Frame(self.profile_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка - данные
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        fields = [
            ("Имя:", "name"),
            ("Вид:", "species"),
            ("Порода:", "breed"),
            ("Дата рождения:", "birth_date"),
            ("Пол:", "gender")
        ]
        
        self.profile_vars = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(left_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar()
            entry = ttk.Entry(left_frame, textvariable=var, width=30, state="readonly")
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.profile_vars[field] = var
        
        # Возраст (автоматически рассчитывается)
        ttk.Label(left_frame, text="Возраст:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.age_var = tk.StringVar(value="Неизвестно")
        ttk.Label(left_frame, textvariable=self.age_var, font=("Arial", 10, "bold")).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Особые отметки
        ttk.Label(left_frame, text="Особые отметки:").grid(row=6, column=0, sticky=tk.NW, pady=5)
        self.notes_text = tk.Text(left_frame, width=30, height=5, state="disabled")
        self.notes_text.grid(row=6, column=1, padx=10, pady=5)
        
        # Кнопка редактирования
        ttk.Button(left_frame, text="Редактировать профиль", 
                  command=self.edit_profile).grid(row=7, column=0, columnspan=2, pady=20)
    
    def setup_history_tab(self):
        # Создаём две подвкладки
        history_notebook = ttk.Notebook(self.history_frame)
        history_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка "Прививки"
        self.vacc_frame = ttk.Frame(history_notebook)
        history_notebook.add(self.vacc_frame, text="Прививки")
        
        # Таблица прививок
        columns = ("id", "Дата", "Название", "Следующая дата")
        self.vacc_tree = ttk.Treeview(self.vacc_frame, columns=columns, show="headings", selectmode="browse")
        
        self.vacc_tree.heading("id", text="ID")
        self.vacc_tree.heading("Дата", text="Дата")
        self.vacc_tree.heading("Название", text="Название")
        self.vacc_tree.heading("Следующая дата", text="Следующая дата")
        
        self.vacc_tree.column("id", width=50)
        self.vacc_tree.column("Дата", width=100)
        self.vacc_tree.column("Название", width=200)
        self.vacc_tree.column("Следующая дата", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(self.vacc_frame, orient=tk.VERTICAL, command=self.vacc_tree.yview)
        self.vacc_tree.configure(yscrollcommand=scrollbar.set)
        
        self.vacc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки для прививок
        btn_frame = ttk.Frame(self.vacc_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Добавить прививку", command=self.add_vaccination).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить прививку", command=self.delete_vaccination).pack(side=tk.LEFT, padx=5)
        
        # Вкладка "Визиты к ветеринару"
        self.visits_frame = ttk.Frame(history_notebook)
        history_notebook.add(self.visits_frame, text="Визиты к ветеринару")
        
        # Таблица визитов
        columns = ("id", "Дата", "Причина", "Диагноз", "Рекомендации")
        self.visits_tree = ttk.Treeview(self.visits_frame, columns=columns, show="headings")
        
        for col in columns:
            self.visits_tree.heading(col, text=col)
            self.visits_tree.column(col, width=100)
        
        self.visits_tree.column("Рекомендации", width=200)
        
        scrollbar2 = ttk.Scrollbar(self.visits_frame, orient=tk.VERTICAL, command=self.visits_tree.yview)
        self.visits_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.visits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки для визитов
        btn_frame2 = ttk.Frame(self.visits_frame)
        btn_frame2.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame2, text="Добавить визит", command=self.add_visit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Удалить визит", command=self.delete_visit).pack(side=tk.LEFT, padx=5)
    
    def setup_reminders_tab(self):
        # Таблица напоминаний
        columns = ("Тип", "Питомец", "Описание", "Дата", "Осталось дней")
        self.reminders_tree = ttk.Treeview(self.reminders_frame, columns=columns, show="headings")
        
        for col in columns:
            self.reminders_tree.heading(col, text=col)
            self.reminders_tree.column(col, width=120)
        
        self.reminders_tree.column("Описание", width=200)
        
        scrollbar = ttk.Scrollbar(self.reminders_frame, orient=tk.VERTICAL, command=self.reminders_tree.yview)
        self.reminders_tree.configure(yscrollcommand=scrollbar.set)
        
        self.reminders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка обновления
        ttk.Button(self.reminders_frame, text="Обновить", 
                  command=self.update_reminders).pack(pady=5)
    
    def load_pets(self):
        """Загрузка списка питомцев в комбобокс"""
        pets = database.get_user_pets(self.current_user_id)
        pet_list = [f"{p[0]}: {p[2]} ({p[3]})" for p in pets]
        self.pet_combo['values'] = pet_list
        if pet_list:
            self.pet_combo.current(0)
            self.current_pet_id = pets[0][0]
            self.load_pet_data()
    
    def load_pet_data(self):
        """Загрузка данных выбранного питомца"""
        if not self.current_pet_id:
            return
        
        conn = sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pets WHERE id=?", (self.current_pet_id,))
        pet = cursor.fetchone()
        conn.close()
        
        if pet:
            # Заполняем профиль
            self.profile_vars['name'].set(pet[2])
            self.profile_vars['species'].set(pet[3])
            self.profile_vars['breed'].set(pet[4] if pet[4] else "")
            self.profile_vars['birth_date'].set(pet[5])
            self.profile_vars['gender'].set(pet[6])
            
            # Возраст
            age = calculate_age(pet[5])
            self.age_var.set(age)
            
            # Особые отметки
            self.notes_text.config(state="normal")
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(1.0, pet[7] if pet[7] else "")
            self.notes_text.config(state="disabled")
            
            # Загружаем прививки
            self.load_vaccinations()
            
            # Загружаем визиты
            self.load_visits()
    
    def load_vaccinations(self):
        """Загрузка прививок в таблицу"""
        # Очищаем таблицу
        for item in self.vacc_tree.get_children():
            self.vacc_tree.delete(item)
        
        if not self.current_pet_id:
            return
        
        vaccinations = database.get_pet_vaccinations(self.current_pet_id)
        for vacc in vaccinations:
            self.vacc_tree.insert("", tk.END, values=vacc[:5])
    
    def load_visits(self):
        """Загрузка визитов в таблицу"""
        for item in self.visits_tree.get_children():
            self.visits_tree.delete(item)
        
        if not self.current_pet_id:
            return
        
        visits = database.get_pet_visits(self.current_pet_id)
        for visit in visits:
            self.visits_tree.insert("", tk.END, values=visit[:6])
    
    def on_pet_selected(self, event):
        """Обработка выбора питомца"""
        selection = self.pet_combo.get()
        if selection:
            self.current_pet_id = int(selection.split(":")[0])
            self.load_pet_data()
    
    def add_pet(self):
        """Добавление нового питомца"""
        dialog = AddPetDialog(self.root, self.current_user_id)
        self.root.wait_window(dialog.dialog)
        self.load_pets()
    
    def delete_pet(self):
        """Удаление питомца"""
        if not self.current_pet_id:
            messagebox.showwarning("Предупреждение", "Выберите питомца для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить питомца? Все данные будут потеряны!"):
            database.delete_pet(self.current_pet_id)
            self.load_pets()
    
    def edit_profile(self):
        """Редактирование профиля"""
        if not self.current_pet_id:
            messagebox.showwarning("Предупреждение", "Выберите питомца")
            return
        
        # Здесь будет диалог редактирования
        messagebox.showinfo("Информация", "Функция редактирования будет добавлена")
    
    def add_vaccination(self):
        """Добавление прививки"""
        if not self.current_pet_id:
            messagebox.showwarning("Предупреждение", "Выберите питомца")
            return
        
        dialog = AddVaccinationDialog(self.root, self.current_pet_id)
        self.root.wait_window(dialog.dialog)
        self.load_vaccinations()
        self.update_reminders()
    
    def delete_vaccination(self):
        """Удаление прививки"""
        selection = self.vacc_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите прививку для удаления")
            return
        
        item = self.vacc_tree.item(selection[0])
        vacc_id = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Удалить прививку?"):
            database.delete_vaccination(vacc_id)
            self.load_vaccinations()
            self.update_reminders()
    
    def add_visit(self):
        """Добавление визита к ветеринару"""
        if not self.current_pet_id:
            messagebox.showwarning("Предупреждение", "Выберите питомца")
            return
        
        dialog = AddVisitDialog(self.root, self.current_pet_id)
        self.root.wait_window(dialog.dialog)
        self.load_visits()
    
    def delete_visit(self):
        """Удаление визита"""
        selection = self.visits_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите визит для удаления")
            return
        
        item = self.visits_tree.item(selection[0])
        visit_id = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Удалить запись о визите?"):
            database.delete_visit(visit_id)
            self.load_visits()
    
    def open_settings(self):
        """Открытие настроек напоминаний"""
        dialog = SettingsDialog(self.root)
        self.root.wait_window(dialog.dialog)
    
    def check_reminders(self):
        """Проверка напоминаний"""
        events = check_reminders(self.current_user_id)
        self.update_reminders()
        
        if events:
            event_list = "\n".join([f"{e[5]}: {e[2]} (до {e[4]})" for e in events])
            messagebox.showinfo("Напоминания", f"Предстоящие события:\n\n{event_list}")
        else:
            messagebox.showinfo("Напоминания", "Нет предстоящих событий")
    
    def check_reminders_on_startup(self):
        """Проверка напоминаний при запуске"""
        events = check_reminders(self.current_user_id)
        if events:
            event_list = "\n".join([f"{e[5]}: {e[2]} (до {e[4]})" for e in events])
            messagebox.showinfo("Напоминания", f"У вас есть предстоящие события:\n\n{event_list}")
    
    def update_reminders(self):
        """Обновление таблицы напоминаний"""
        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)
        
        events = check_reminders(self.current_user_id)
        for event in events:
            # Форматируем для отображения
            days_left = (datetime.strptime(event[4], "%Y-%m-%d").date() - datetime.now().date()).days
            self.reminders_tree.insert("", tk.END, values=(
                "Прививка",
                event[5],
                event[2],
                event[4],
                f"{days_left} дн."
            ))
    
    def show_about(self):
        """О программе"""
        messagebox.showinfo("О программе", 
                           "Учёт домашних животных\nВерсия 1.0\n\n"
                           "Разработано для учебного проекта\n"
                           "Используемые технологии: Python, Tkinter, SQLite")
    
    def run(self):
        self.root.mainloop()