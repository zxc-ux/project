from datetime import datetime
import database

def calculate_age(birth_date_str):
    """Расчёт возраста в годах и месяцах"""
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        years = today.year - birth_date.year
        months = today.month - birth_date.month
        
        if months < 0:
            years -= 1
            months += 12
        
        if years > 0:
            return f"{years} г. {months} мес."
        else:
            return f"{months} мес."
    except:
        return "Неизвестно"

def check_reminders(user_id):
    """Проверка предстоящих событий"""
    days_ahead = database.get_reminder_days()
    return database.get_upcoming_events(user_id, days_ahead)