import re
from datetime import datetime

def validate_amount(amount):
    """Проверка корректности суммы (должна быть числом)"""
    if isinstance(amount, (int, float)) and amount > 0:
        return True
    raise ValueError("Некорректная сумма. Введите положительное число.")

def format_date(date_str):
    """Форматирование даты в формат ДД.ММ.ГГГГ чч:мм"""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        raise ValueError("Некорректный формат даты. Используйте YYYY-MM-DD.")