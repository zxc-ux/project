import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import hashlib
from datetime import datetime

class Database:
    # ... (весь класс Database остается без изменений, как в вашем файле)
    def __init__(self, db_name='users.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.insert_test_users()
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def insert_test_users(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            test_users = [
                ('admin1', 'admin123', 'admin1@test.com', 'admin'),
                ('admin2', 'admin456', 'admin2@test.com', 'admin'),
                ('user1', 'user123', 'user1@test.com', 'user'),
                ('user2', 'user123', 'user2@test.com', 'user'),
                ('user3', 'user123', 'user3@test.com', 'user'),
                ('user4', 'user123', 'user4@test.com', 'user'),
                ('user5', 'user123', 'user5@test.com', 'user'),
                ('user6', 'user123', 'user6@test.com', 'user'),
                ('user7', 'user123', 'user7@test.com', 'user'),
                ('user8', 'user123', 'user8@test.com', 'user'),
            ]
            
            for username, password, email, role in test_users:
                hashed_password = self.hash_password(password)
                try:
                    self.cursor.execute('''
                        INSERT INTO users (username, password, email, role)
                        VALUES (?, ?, ?, ?)
                    ''', (username, hashed_password, email, role))
                except:
                    pass
            
            self.conn.commit()
            print("Тестовые пользователи добавлены")
    
    def register_user(self, username, password, email, role='user'):
        hashed_password = self.hash_password(password)
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, email, role)
                VALUES (?, ?, ?, ?)
            ''', (username, hashed_password, email, role))
            self.conn.commit()
            return True, "Регистрация успешна!"
        except sqlite3.IntegrityError:
            return False, "Пользователь с таким именем или email уже существует"
    
    def login_user(self, username, password):
        hashed_password = self.hash_password(password)
        self.cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        user = self.cursor.fetchone()
        
        if user:
            return True, f"Добро пожаловать, {username}!", user
        else:
            return False, "Неверное имя пользователя или пароль", None
    
    def get_all_users(self):
        self.cursor.execute("SELECT id, username, email, role, created_at FROM users")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

class MainMenu:
    """Класс главного меню после входа в систему"""
    
    def __init__(self, parent, user_data, db):
        self.parent = parent
        self.user_data = user_data
        self.db = db
        self.window = tk.Toplevel(parent)
        self.window.title(f"Главное меню - {user_data[1]}")
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self.logout)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса главного меню"""
        
        # Верхняя панель с информацией о пользователе
        top_frame = tk.Frame(self.window, bg="#2c3e50", height=60)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)
        
        # Приветствие и роль
        tk.Label(
            top_frame, 
            text=f"Добро пожаловать, {self.user_data[1]}!",
            fg="white",
            bg="#2c3e50",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=20, pady=15)
        
        tk.Label(
            top_frame,
            text=f"Роль: {self.user_data[4].upper()}",
            fg="#ecf0f1",
            bg="#2c3e50",
            font=("Arial", 10)
        ).pack(side="left", padx=10)
        
        # Кнопка выхода
        tk.Button(
            top_frame,
            text="Выйти",
            command=self.logout,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10),
            relief="flat",
            padx=20
        ).pack(side="right", padx=20, pady=15)
        
        # Основная область с меню
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        tk.Label(
            main_frame,
            text="Главное меню",
            font=("Arial", 20, "bold"),
            fg="#34495e"
        ).pack(pady=20)
        
        # Создаем вкладки для разных функций
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)
        
        # Вкладка "Профиль"
        profile_frame = ttk.Frame(notebook)
        notebook.add(profile_frame, text="Профиль")
        self.setup_profile_tab(profile_frame)
        
        # Вкладка "Пользователи" (только для админов)
        if self.user_data[4] == 'admin':
            users_frame = ttk.Frame(notebook)
            notebook.add(users_frame, text="Управление пользователями")
            self.setup_users_tab(users_frame)
        
        # Вкладка "Настройки"
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Настройки")
        self.setup_settings_tab(settings_frame)
        
        # Вкладка "О программе"
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="О программе")
        self.setup_about_tab(about_frame)
    
    def setup_profile_tab(self, parent):
        """Настройка вкладки профиля"""
        
        # Карточка профиля
        profile_card = tk.Frame(parent, relief="groove", bd=2, bg="#f8f9fa")
        profile_card.pack(pady=30, padx=50, fill="both", expand=True)
        
        tk.Label(
            profile_card,
            text="Информация о профиле",
            font=("Arial", 16, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        ).pack(pady=20)
        
        # Информация о пользователе
        info_frame = tk.Frame(profile_card, bg="#f8f9fa")
        info_frame.pack(pady=20)
        
        info_fields = [
            ("ID пользователя:", self.user_data[0]),
            ("Имя пользователя:", self.user_data[1]),
            ("Email:", self.user_data[3]),
            ("Роль:", self.user_data[4].capitalize()),
            ("Дата регистрации:", self.user_data[5] if len(self.user_data) > 5 else "Не указана")
        ]
        
        for i, (label, value) in enumerate(info_fields):
            row_frame = tk.Frame(info_frame, bg="#f8f9fa")
            row_frame.pack(fill="x", pady=5)
            
            tk.Label(
                row_frame,
                text=label,
                font=("Arial", 11, "bold"),
                bg="#f8f9fa",
                width=15,
                anchor="w"
            ).pack(side="left", padx=10)
            
            tk.Label(
                row_frame,
                text=str(value),
                font=("Arial", 11),
                bg="#f8f9fa",
                anchor="w"
            ).pack(side="left", padx=10)
        
        # Кнопка редактирования профиля
        tk.Button(
            profile_card,
            text="Редактировать профиль",
            command=self.edit_profile,
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            relief="flat",
            padx=30,
            pady=10
        ).pack(pady=30)
    
    def setup_users_tab(self, parent):
        """Настройка вкладки управления пользователями (для админов)"""
        
        # Заголовок
        tk.Label(
            parent,
            text="Список всех пользователей",
            font=("Arial", 14, "bold"),
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Создаем Treeview для отображения пользователей
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Скроллбары
        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Таблица пользователей
        columns = ("ID", "Имя", "Email", "Роль", "Дата регистрации")
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        # Настройка колонок
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, minwidth=100)
        
        tree.pack(fill="both", expand=True)
        
        scrollbar_y.config(command=tree.yview)
        scrollbar_x.config(command=tree.xview)
        
        # Загружаем данные
        users = self.db.get_all_users()
        for user in users:
            tree.insert("", "end", values=user)
        
        # Кнопки управления
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(
            btn_frame,
            text="Обновить список",
            command=lambda: self.refresh_users(tree),
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10),
            padx=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="Экспорт в CSV",
            command=self.export_users,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10),
            padx=20
        ).pack(side="left", padx=5)
    
    def setup_settings_tab(self, parent):
        """Настройка вкладки настроек"""
        
        settings_frame = tk.Frame(parent, relief="groove", bd=2)
        settings_frame.pack(pady=30, padx=50, fill="both", expand=True)
        
        tk.Label(
            settings_frame,
            text="Настройки приложения",
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        # Настройки уведомлений
        notify_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            settings_frame,
            text="Включить уведомления",
            variable=notify_var,
            font=("Arial", 11)
        ).pack(pady=10)
        
        # Выбор темы
        theme_frame = tk.Frame(settings_frame)
        theme_frame.pack(pady=10)
        
        tk.Label(theme_frame, text="Тема оформления:", font=("Arial", 11)).pack(side="left", padx=10)
        
        theme_var = tk.StringVar(value="Светлая")
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=theme_var,
            values=["Светлая", "Темная", "Системная"],
            state="readonly",
            width=15
        )
        theme_combo.pack(side="left")
        
        # Кнопка сохранения настроек
        tk.Button(
            settings_frame,
            text="Сохранить настройки",
            command=lambda: messagebox.showinfo("Успех", "Настройки сохранены!"),
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            padx=30,
            pady=10
        ).pack(pady=30)
    
    def setup_about_tab(self, parent):
        """Настройка вкладки 'О программе'"""
        
        about_frame = tk.Frame(parent)
        about_frame.pack(expand=True)
        
        tk.Label(
            about_frame,
            text="Система авторизации пользователей",
            font=("Arial", 18, "bold"),
            fg="#2c3e50"
        ).pack(pady=20)
        
        tk.Label(
            about_frame,
            text="Версия 1.0",
            font=("Arial", 12),
            fg="#7f8c8d"
        ).pack()
        
        tk.Label(
            about_frame,
            text="\nРазработано с использованием:\n"
                 "• Python 3\n"
                 "• Tkinter\n"
                 "• SQLite3\n",
            font=("Arial", 11),
            justify="center",
            fg="#34495e"
        ).pack(pady=30)
        
        tk.Label(
            about_frame,
            text="© 2026 Все права защищены",
            font=("Arial", 9),
            fg="#95a5a6"
        ).pack(side="bottom", pady=20)
    
    def edit_profile(self):
        """Редактирование профиля"""
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Редактирование профиля")
        edit_window.geometry("400x300")
        
        tk.Label(edit_window, text="Редактирование профиля", font=("Arial", 14, "bold")).pack(pady=20)
        
        # Поля для редактирования
        fields = [
            ("Имя пользователя:", self.user_data[1]),
            ("Email:", self.user_data[3])
        ]
        
        entries = []
        for label, value in fields:
            frame = tk.Frame(edit_window)
            frame.pack(pady=10)
            
            tk.Label(frame, text=label, width=15, anchor="w").pack(side="left")
            entry = tk.Entry(frame, width=25)
            entry.insert(0, value)
            entry.pack(side="left")
            entries.append(entry)
        
        # Кнопка сохранения
        tk.Button(
            edit_window,
            text="Сохранить изменения",
            command=lambda: self.save_profile(entries, edit_window),
            bg="#2ecc71",
            fg="white",
            padx=20,
            pady=5
        ).pack(pady=30)
    
    def save_profile(self, entries, window):
        """Сохранение изменений профиля"""
        # Здесь должна быть логика сохранения в БД
        messagebox.showinfo("Успех", "Профиль успешно обновлен!")
        window.destroy()
    
    def refresh_users(self, tree):
        """Обновление списка пользователей"""
        # Очищаем таблицу
        for item in tree.get_children():
            tree.delete(item)
        
        # Загружаем новые данные
        users = self.db.get_all_users()
        for user in users:
            tree.insert("", "end", values=user)
        
        messagebox.showinfo("Обновлено", "Список пользователей обновлен!")
    
    def export_users(self):
        """Экспорт пользователей в CSV"""
        users = self.db.get_all_users()
        
        # Создаем CSV строку
        csv_content = "ID,Имя,Email,Роль,Дата регистрации\n"
        for user in users:
            csv_content += f"{user[0]},{user[1]},{user[2]},{user[3]},{user[4]}\n"
        
        # Сохраняем файл
        try:
            with open(f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "w", encoding="utf-8") as f:
                f.write(csv_content)
            messagebox.showinfo("Экспорт завершен", "Данные успешно экспортированы в CSV файл!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def logout(self):
        """Выход из системы"""
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти?"):
            self.window.destroy()
            # Возвращаемся к окну входа
            self.parent.deiconify()

class LoginApp:
    def __init__(self):
        self.db = Database()
        
        self.window = tk.Tk()
        self.window.title("Вход / Регистрация")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.email = tk.StringVar()
        self.confirm_password = tk.StringVar()
        
        self.show_login_frame()
    
    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()
    
    def show_login_frame(self):
        self.clear_window()
        
        # Заголовок
        tk.Label(self.window, text="Вход в систему", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Поля ввода
        tk.Label(self.window, text="Имя пользователя:").pack(pady=5)
        tk.Entry(self.window, textvariable=self.username, width=30).pack(pady=5)
        
        tk.Label(self.window, text="Пароль:").pack(pady=5)
        tk.Entry(self.window, textvariable=self.password, width=30, show="*").pack(pady=5)
        
        # Кнопки
        tk.Button(self.window, text="Войти", command=self.login, width=20, height=2).pack(pady=20)
        tk.Button(self.window, text="Регистрация", command=self.show_register_frame, width=20).pack(pady=5)
        
        # Информация
        info_text = "Тестовые пользователи:\nadmin1 / admin123\nadmin2 / admin456\nuser1 / user123"
        tk.Label(self.window, text=info_text, fg="gray").pack(pady=20)
    
    def show_register_frame(self):
        self.clear_window()
        
        tk.Label(self.window, text="Регистрация", font=("Arial", 20, "bold")).pack(pady=20)
        
        tk.Label(self.window, text="Имя пользователя:").pack(pady=5)
        tk.Entry(self.window, textvariable=self.username, width=30).pack(pady=5)
        
        tk.Label(self.window, text="Email:").pack(pady=5)
        tk.Entry(self.window, textvariable=self.email, width=30).pack(pady=5)
        
        tk.Label(self.window, text="Пароль:").pack(pady=5)
        tk.Entry(self.window, textvariable=self.password, width=30, show="*").pack(pady=5)
        
        tk.Label(self.window, text="Подтвердите пароль:").pack(pady=5)
        tk.Entry(self.window, textvariable=self.confirm_password, width=30, show="*").pack(pady=5)
        
        tk.Button(self.window, text="Зарегистрироваться", command=self.register, width=20, height=2).pack(pady=20)
        tk.Button(self.window, text="Назад", command=self.show_login_frame, width=20).pack(pady=5)
    
    def login(self):
        username = self.username.get()
        password = self.password.get()
        
        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        success, message, user_data = self.db.login_user(username, password)
        
        if success:
            messagebox.showinfo("Успех", message)
            # Скрываем окно входа и показываем главное меню
            self.window.withdraw()
            MainMenu(self.window, user_data, self.db)
        else:
            messagebox.showerror("Ошибка", message)
    
    def register(self):
        username = self.username.get()
        password = self.password.get()
        email = self.email.get()
        confirm = self.confirm_password.get()
        
        if not all([username, password, email, confirm]):
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        if password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают!")
            return
        
        success, message = self.db.register_user(username, password, email)
        
        if success:
            messagebox.showinfo("Успех", message)
            self.show_login_frame()
        else:
            messagebox.showerror("Ошибка", message)
    
    def run(self):
        self.window.mainloop()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

if __name__ == "__main__":
    app = LoginApp()
    app.run()