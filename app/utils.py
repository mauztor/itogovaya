import re
from datetime import datetime

def validate_amount(amount):
    """Проверка корректности суммы (должна быть положительным числом)"""
    if isinstance(amount, (int, float)) and amount > 0:
        return True
    raise ValueError("Сумма должна быть положительным числом.")

def format_date(date_str):
    """Форматирование даты в формат ДД.ММ.ГГГГ чч:мм"""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        return date.strftime("%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError("Некорректный формат даты. Используйте YYYY-MM-DD.")