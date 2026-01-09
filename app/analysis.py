import sqlite3
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os

# Указываем использование неинтерактивного бэкенда
matplotlib.use("Agg")

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

    def plot_expenses_by_category(self, output_path):
        """График расходов по категориям"""
        df = self.get_category_summary()
        if df.empty:
            return None
        plt.figure(figsize=(8, 6))
        plt.bar(df["name"], df["total"])
        plt.title("Расходы по категориям")
        plt.xlabel("Категория")
        plt.ylabel("Сумма")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

    def plot_top_expenses(self, output_path):
        """График топовых расходов"""
        df = self.get_top_expenses()
        if df.empty:
            return None
        plt.figure(figsize=(8, 6))
        plt.bar(df["name"], df["amount"])
        plt.title("Топ расходов")
        plt.xlabel("Категория")
        plt.ylabel("Сумма")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

    def plot_income_vs_expenses(self, output_path):
        """График доходов и расходов"""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql("""
                SELECT o.date, o.amount, o.operation_type
                FROM operations o
            """, conn)
        if df.empty:
            return None
        income_df = df[df["operation_type"] == "доход"].groupby("date").sum()
        expense_df = df[df["operation_type"] == "расход"].groupby("date").sum()
        plt.figure(figsize=(10, 6))
        plt.plot(income_df.index, income_df["amount"], label="Доходы")
        plt.plot(expense_df.index, expense_df["amount"], label="Расходы")
        plt.title("Доходы и расходы по времени")
        plt.xlabel("Дата")
        plt.ylabel("Сумма")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()