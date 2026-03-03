from database import Database

def test_database():
    # Создаем подключение к БД
    db = Database()
    
    # Проверяем всех пользователей
    print("Все пользователи в базе данных:")
    users = db.get_all_users()
    for user in users:
        print(f"ID: {user[0]}, Имя: {user[1]}, Email: {user[2]}, Роль: {user[3]}")
    
    # Тест входа
    print("\nТест входа:")
    test_logins = [
        ("admin1", "admin123"),
        ("user1", "user123"),
        ("admin1", "wrongpass"),
        ("unknown", "user123")
    ]
    
    for username, password in test_logins:
        success, message, user = db.login_user(username, password)
        print(f"Попытка входа {username}/{password}: {message}")
    
    # Закрываем соединение
    db.close()

if __name__ == "__main__":
    test_database()