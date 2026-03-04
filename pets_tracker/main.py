import tkinter as tk
from tkinter import ttk, messagebox
from gui.main_window import MainWindow
import database

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Авторизация - Учёт домашних животных")
        self.root.geometry("300x250")
        self.root.resizable(False, False)
        
        # Центрируем окно
        self.center_window()
        
        # Создаём базу данных при первом запуске
        database.init_db()
        
        self.setup_ui()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Учёт домашних животных", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # Форма входа
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.login_entry = ttk.Entry(frame, width=20)
        self.login_entry.grid(row=0, column=1, pady=5)
        self.login_entry.insert(0, "admin")
        
        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(frame, width=20, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        self.password_entry.insert(0, "admin123")
        
        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Войти", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Регистрация", command=self.show_register).pack(side=tk.LEFT, padx=5)
        
        # Статус
        self.status_label = ttk.Label(frame, text="", foreground="red")
        self.status_label.grid(row=3, column=0, columnspan=2)
    
    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        if database.check_user(login, password):
            self.root.destroy()
            app = MainWindow()
            app.run()
        else:
            self.status_label.config(text="Неверный логин или пароль")
    
    def show_register(self):
        RegisterDialog(self.root)
    
    def run(self):
        self.root.mainloop()

class RegisterDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Регистрация")
        self.dialog.geometry("300x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.login_entry = ttk.Entry(frame, width=20)
        self.login_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(frame, width=20, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Подтверждение:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confirm_entry = ttk.Entry(frame, width=20, show="*")
        self.confirm_entry.grid(row=2, column=1, pady=5)
        
        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Зарегистрироваться", 
                  command=self.register).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(frame, text="", foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=2)
    
    def register(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if len(login) < 3:
            self.status_label.config(text="Логин должен быть не менее 3 символов")
            return
        
        if len(password) < 4:
            self.status_label.config(text="Пароль должен быть не менее 4 символов")
            return
        
        if password != confirm:
            self.status_label.config(text="Пароли не совпадают")
            return
        
        if database.add_user(login, password):
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.dialog.destroy()
        else:
            self.status_label.config(text="Пользователь уже существует")

if __name__ == "__main__":
    app = LoginWindow()
    app.run()