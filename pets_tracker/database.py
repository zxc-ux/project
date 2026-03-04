import sqlite3
import os
from datetime import datetime, timedelta

DB_NAME = "pets.db"

def init_db():
    """Инициализация базы данных при первом запуске"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Создаём администратора по умолчанию
    cursor.execute("SELECT * FROM users WHERE login='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (login, password, is_admin) VALUES (?, ?, ?)",
                      ("admin", "admin123", 1))
    
    # Таблица питомцев
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            breed TEXT,
            birth_date TEXT NOT NULL,
            gender TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Таблица прививок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vaccinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            vaccine_name TEXT NOT NULL,
            date_given TEXT NOT NULL,
            next_due TEXT,
            FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
        )
    ''')
    
    # Таблица визитов к ветеринару
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vet_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            visit_date TEXT NOT NULL,
            reason TEXT,
            diagnosis TEXT,
            recommendations TEXT,
            FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
        )
    ''')
    
    # Таблица настроек
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            reminder_days INTEGER DEFAULT 7
        )
    ''')
    
    # Настройки по умолчанию
    cursor.execute("SELECT * FROM settings WHERE id=1")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO settings (id, reminder_days) VALUES (1, 7)")
    
    conn.commit()
    conn.close()

# Функции для работы с пользователями
def check_user(login, password):
    """Проверка логина и пароля"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE login=? AND password=?", (login, password))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(login, password):
    """Добавление нового пользователя"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (login, password, is_admin) VALUES (?, ?, ?)",
                      (login, password, 0))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_users():
    """Получение всех пользователей (для админа)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, login, is_admin FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def delete_user(user_id):
    """Удаление пользователя (для админа)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=? AND login!='admin'", (user_id,))
    conn.commit()
    conn.close()

def reset_password(user_id, new_password):
    """Сброс пароля пользователя (для админа)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
    conn.commit()
    conn.close()

# Функции для работы с питомцами
def add_pet(user_id, name, species, breed, birth_date, gender, notes=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pets (user_id, name, species, breed, birth_date, gender, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, name, species, breed, birth_date, gender, notes))
    conn.commit()
    conn.close()

def get_user_pets(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
    pets = cursor.fetchall()
    conn.close()
    return pets

def delete_pet(pet_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pets WHERE id=?", (pet_id,))
    conn.commit()
    conn.close()

# Функции для работы с прививками
def add_vaccination(pet_id, vaccine_name, date_given, next_due=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vaccinations (pet_id, vaccine_name, date_given, next_due)
        VALUES (?, ?, ?, ?)
    ''', (pet_id, vaccine_name, date_given, next_due))
    conn.commit()
    conn.close()

def get_pet_vaccinations(pet_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vaccinations WHERE pet_id=? ORDER BY date_given DESC", (pet_id,))
    vaccinations = cursor.fetchall()
    conn.close()
    return vaccinations

def delete_vaccination(vacc_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vaccinations WHERE id=?", (vacc_id,))
    conn.commit()
    conn.close()

# Функции для работы с визитами
def add_vet_visit(pet_id, visit_date, reason, diagnosis, recommendations):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vet_visits (pet_id, visit_date, reason, diagnosis, recommendations)
        VALUES (?, ?, ?, ?, ?)
    ''', (pet_id, visit_date, reason, diagnosis, recommendations))
    conn.commit()
    conn.close()

def get_pet_visits(pet_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vet_visits WHERE pet_id=? ORDER BY visit_date DESC", (pet_id,))
    visits = cursor.fetchall()
    conn.close()
    return visits

def delete_visit(visit_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vet_visits WHERE id=?", (visit_id,))
    conn.commit()
    conn.close()

# Функции для настроек
def get_reminder_days():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT reminder_days FROM settings WHERE id=1")
    days = cursor.fetchone()[0]
    conn.close()
    return days

def set_reminder_days(days):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET reminder_days=? WHERE id=1", (days,))
    conn.commit()
    conn.close()

# Функция для получения предстоящих событий
def get_upcoming_events(user_id, days_ahead):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    target_date = today + timedelta(days=days_ahead)
    
    # Получаем все прививки пользователя
    cursor.execute('''
        SELECT v.*, p.name as pet_name 
        FROM vaccinations v
        JOIN pets p ON v.pet_id = p.id
        WHERE p.user_id = ? AND v.next_due != '' AND v.next_due BETWEEN ? AND ?
        ORDER BY v.next_due
    ''', (user_id, today.isoformat(), target_date.isoformat()))
    
    events = cursor.fetchall()
    conn.close()
    return events