import sqlite3
import hashlib

class Database:
    def __init__(self, db_name='users.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.insert_test_users()
    
    def create_table(self):
        """Создание таблицы пользователей"""
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
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def insert_test_users(self):
        """Вставка тестовых пользователей"""
        # Проверяем, есть ли уже пользователи
        self.cursor.execute("SELECT COUNT(*) FROM users")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            test_users = [
                # Администраторы
                ('admin1', 'admin123', 'admin1@test.com', 'admin'),
                ('admin2', 'admin456', 'admin2@test.com', 'admin'),
                # Обычные пользователи
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
                except sqlite3.IntegrityError:
                    print(f"Пользователь {username} уже существует")
            
            self.conn.commit()
            print("Тестовые пользователи добавлены")
    
    def register_user(self, username, password, email, role='user'):
        """Регистрация нового пользователя"""
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
        """Вход пользователя"""
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
        """Получение всех пользователей (для администратора)"""
        self.cursor.execute("SELECT id, username, email, role, created_at FROM users")
        return self.cursor.fetchall()
    
    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()