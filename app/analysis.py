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

    def get_category_summary(self, operation_type="расход"):
        """Суммарные расходы или доходы по категориям"""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql("""
                SELECT c.name, SUM(o.amount) AS total
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.operation_type = ?
                GROUP BY c.name
            """, conn, params=(operation_type,))
        return df

    def get_top_expenses_or_incomes(self, n=10, operation_type="расход"):
        """Топ-N расходов или доходов"""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql("""
                SELECT o.amount, c.name, o.date
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.operation_type = ?
                ORDER BY o.amount DESC
                LIMIT ?
            """, conn, params=(operation_type, n))
        return df

    def _fig_to_html(self, fig):
        """Конвертирует объект Figure в HTML-тег <img> с изображением в формате base64."""
        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'/>"

    def plot_expenses_by_category(self):
        """График расходов по категориям в виде HTML-тега <img>"""
        df = self.get_category_summary(operation_type="расход")
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

    def plot_incomes_by_category(self):
        """График доходов по категориям в виде HTML-тега <img>"""
        df = self.get_category_summary(operation_type="доход")
        if df.empty:
            return "Нет данных"
        fig = Figure(figsize=(8, 6))
        ax = fig.subplots()
        ax.bar(df["name"], df["total"])
        ax.set_title("Доходы по категориям")
        ax.set_xlabel("Категория")
        ax.set_ylabel("Сумма")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        return self._fig_to_html(fig)

    def plot_top_expenses(self):
        """График топовых расходов в виде HTML-тега <img>"""
        df = self.get_top_expenses_or_incomes(operation_type="расход")
        if df.empty:
            return "Нет данных"
        fig = Figure(figsize=(8, 6))
        ax = fig.subplots()
        ax.bar(df["name"], df["amount"])
        ax.set_title("Топ расходов")
        ax.set_xlabel("Категория")
        ax.set_.ylabel("Сумма")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        return self._fig_to_html(fig)

    def plot_top_incomes(self):
        """График топовых доходов в виде HTML-тега <img>"""
        df = self.get_top_expenses_or_incomes(operation_type="доход")
        if df.empty:
            return "Нет данных"
        fig = Figure(figsize=(8, 6))
        ax = fig.subplots()
        ax.bar(df["name"], df["amount"])
        ax.set_title("Топ доходов")
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

    def plot_top_expenses_and_incomes(self):
        """График топ 10 расходов и доходов в виде HTML-тега <img>"""
        top_expenses = self.get_top_expenses_or_incomes(operation_type="расход")
        top_incomes = self.get_top_expenses_or_incomes(operation_type="доход")
        if top_expenses.empty and top_incomes.empty:
            return "Нет данных"
        fig = Figure(figsize=(10, 6))
        ax = fig.subplots()
        if not top_expenses.empty:
            ax.bar(top_expenses["name"], top_expenses["amount"], label="Расходы")
        if not top_incomes.empty:
            ax.bar(top_incomes["name"], top_incomes["amount"], label="Доходы")
        ax.set_title("Топ 10 расходов и доходов")
        ax.set_xlabel("Категория")
        ax.set_ylabel("Сумма")
        ax.legend()
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        return self._fig_to_html(fig)