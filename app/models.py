from datetime import datetime
import re

class FinancialOperation:
    def __init__(self, amount, category, date, operation_type, comment=""):
        self.amount = amount
        self.category = category
        self.date = self._validate_date(date)
        self.operation_type = operation_type
        self.comment = comment

    def _validate_date(self, date):
        """Проверка корректности формата даты (YYYY-MM-DD)"""
        if re.match(r"\d{4}-\d{2}-\d{2}", date):
            return date
        raise ValueError("Некорректный формат даты. Используйте YYYY-MM-DD.")

    def __repr__(self):
        return f"Финансовая операция: {self.amount}, {self.category}, {self.date}, {self.operation_type}, {self.comment}"