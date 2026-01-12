import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from io import BytesIO
import base64

class FinancialAnalysis:
    def __init__(self, db_name="data/tables.db"):
        self.db_name = db_name

    def get_balance(self):
        """Расчёт текущего баланса (доходы - расходы)"""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql("""
                SELECT o.amount, o.operation_type
                FROM operations o
            """, conn)
        incomes = df[df["operation_type"] == "доход"]["amount"].sum()
        expenses = df[df["operation_type"] == "расход"]["amount"].sum()
        return incomes - expenses

    def get_category_summary(self):
        """Суммарные расходы по категориям"""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql("""
                SELECT c.name, SUM(o.amount) AS total
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.operation_type = 'расход'
                GROUP BY c.name
            """, conn)
        return df

    def get_top_expenses(self, n=5):
        """Топ-N расходов"""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql("""
                SELECT o.amount, c.name, o.date
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.operation_type = 'расход'
                ORDER BY o.amount DESC
                LIMIT ?
            """, conn, params=(n,))
        return df

    def _fig_to_html(self, fig):
        """Конвертирует объект Figure в HTML-тег <img> с изображением в формате base64."""
        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'/>"

    def plot_expenses_by_category(self):
        """График расходов по категориям в виде HTML-тега <img>"""
        df = self.get_category_summary()
        if df.empty:
            return "Нет данных"
        fig = Figure(figsize=(8, 6))
        ax = fig.subplots()
        ax.bar(df["name"], df["total"])
        ax.set_title("Расходы по категориям")
        ax.set_xlabel("Категория")
        ax.set_ylabel("Сумма")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        return self._fig_to_html(fig)

    def plot_top_expenses(self):
        """График топовых расходов в виде HTML-тега <img>"""
        df = self.get_top_expenses()
        if df.empty:
            return "Нет данных"
        fig = Figure(figsize=(8, 6))
        ax = fig.subplots()
        ax.bar(df["name"], df["amount"])
        ax.set_title("Топ расходов")
        ax.set_xlabel("Категория")
        ax.set_ylabel("Сумма")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        return self._fig_to_html(fig)

    def plot_income_vs_expenses(self):
        """График доходов и расходов в виде HTML-тега <img>"""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql("""
                SELECT o.date, o.amount, o.operation_type
                FROM operations o
            """, conn)
        if df.empty:
            return "Нет данных"
        income_df = df[df["operation_type"] == "доход"].groupby("date").sum()
        expense_df = df[df["operation_type"] == "расход"].groupby("date").sum()
        fig = Figure(figsize=(10, 6))
        ax = fig.subplots()
        ax.plot(income_df.index, income_df["amount"], label="Доходы")
        ax.plot(expense_df.index, expense_df["amount"], label="Расходы")
        ax.set_title("Доходы и расходы по времени")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Сумма")
        ax.legend()
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        return self._fig_to_html(fig)