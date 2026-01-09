import sqlite3
import csv
import os
from datetime import datetime

class Storage:
    def __init__(self, db_name="data/tables.db"):
        self.db_name = db_name
        self._ensure_db_exists()
        self._create_tables()

    def _ensure_db_exists(self):
        """Проверка наличия файла базы данных. Если файла нет, создаём его."""
        if not os.path.exists(self.db_name):
            open(self.db_name, "w").close()

    def _create_tables(self):
        """Создание таблиц в базе данных"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Таблица категорий
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL CHECK(type IN ('доход', 'расход'))
                )
            """)
            # Таблица операций
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    category_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    comment TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            """)
            conn.commit()

    def add_category(self, name, category_type):
        """Добавление категории"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO categories (name, type) 
                VALUES (?, ?)
            """, (name, category_type))
            conn.commit()

    def get_categories(self, category_type=None):
        """Получение категорий"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if category_type:
                cursor.execute("""
                    SELECT * FROM categories 
                    WHERE type = ?
                """, (category_type,))
            else:
                cursor.execute("SELECT * FROM categories")
            return cursor.fetchall()

    def update_category(self, category_id, new_name, new_type):
        """Обновление категории"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE categories 
                SET name = ?, type = ? 
                WHERE id = ?
            """, (new_name, new_type, category_id))
            conn.commit()

    def add_operation(self, operation):
        """Добавление финансовой операции"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO operations (amount, category_id, date, operation_type, comment)
                VALUES (?, ?, ?, ?, ?)
            """, (
                operation["amount"],
                operation["category_id"],
                operation["date"],
                operation["operation_type"],
                operation["comment"]
            ))
            conn.commit()

    def get_operations(self, limit=20):
        """Получение последних операций"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, o.amount, c.name, o.date, o.operation_type, o.comment
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                ORDER BY o.date DESC
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()

    def delete_operation(self, operation_id):
        """Удаление операции по ID"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM operations WHERE id = ?", (operation_id,))
            conn.commit()

     # Загрузка категорий из CSV
    def load_categories_from_csv(self, file_path):
        """Загрузка категорий из CSV-файла"""
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Пропускаем заголовок
            for row in reader:
                self.add_category(row[0], row[1])

    # Выгрузка категорий в CSV
    def export_categories_to_csv(self, file_path):
        """Выгрузка категорий в CSV-файл"""
        categories = self.get_categories()
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["name", "type"])  # Заголовок
            for category in categories:
                writer.writerow([category[1], category[2]])

    # Загрузка операций из CSV
    def load_operations_from_csv(self, file_path):
        """Загрузка операций из CSV-файла"""
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Пропускаем заголовок
            for row in reader:
                self.add_operation({
                    "amount": float(row[0]),
                    "category_id": int(row[1]),
                    "date": row[2],
                    "operation_type": row[3],
                    "comment": row[4]
                })

    # Выгрузка операций в CSV
    def export_operations_to_csv(self, file_path):
        """Выгрузка операций в CSV-файл"""
        operations = self.get_operations()
        with open(file_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["amount", "category_id", "date", "operation_type", "comment"])  # Заголовок
            for operation in operations:
                writer.writerow([operation[1], operation[2], operation[3], operation[4], operation[5]])