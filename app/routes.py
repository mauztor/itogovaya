from flask import Flask, render_template, request, redirect, url_for, send_file
from .utils import validate_amount, format_date
import os
from app.storage import Storage
from app.analysis import FinancialAnalysis

def init_routes(app):
    storage = Storage()
    analysis = FinancialAnalysis()

    @app.route("/")
    def index():
        balance = analysis.get_balance()
        operations = storage.get_operations()
        return render_template("index.html", balance=balance, operations=operations)

    @app.route("/add_operation", methods=["GET", "POST"])
    def add_operation():
        if request.method == "POST":
            try:
                amount = float(request.form["amount"])
                validate_amount(amount)  # Проверяем сумму
            except ValueError as e:
                return str(e), 400  # Возвращаем ошибку, если сумма некорректна
            category_id = int(request.form["category_id"])
            try:
                date = format_date(request.form["date"])  # Преобразуем дату
            except ValueError as e:
                return str(e), 400  # Возвращаем ошибку, если дата некорректна
            operation_type = request.form["operation_type"]
            comment = request.form["comment"]
            storage.add_operation({
                "amount": amount,
                "category_id": category_id,
                "date": date,
                "operation_type": operation_type,
                "comment": comment
            })
            return redirect(url_for("index"))
        income_categories = storage.get_categories(category_type="доход")
        expense_categories = storage.get_categories(category_type="расход")
        return render_template("add_operation.html", income_categories=income_categories, expense_categories=expense_categories)

    @app.route("/view_operations")
    def view_operations():
        operations = storage.get_operations(limit=2000)
        return render_template("view_operations.html", operations=operations)

    @app.route("/categories", methods=["GET", "POST"])
    def categories():
        if request.method == "POST":
            if "add" in request.form:
                name = request.form["name"]
                category_type = request.form["type"]
                storage.add_category(name, category_type)
            elif "update" in request.form:
                category_id = int(request.form["category_id"])
                new_name = request.form["new_name"]
                new_type = request.form["new_type"]
                storage.update_category(category_id, new_name, new_type)
            return redirect(url_for("categories"))
        categories = storage.get_categories()
        return render_template("categories.html", categories=categories)

    # Загрузка категорий из CSV
    @app.route("/load_categories_csv", methods=["POST"])
    def load_categories_csv():
        if "file" not in request.files:
            return "Файл не найден", 400
        file = request.files["file"]
        if file.filename == "":
            return "Файл не выбран", 400
        if file and file.filename.endswith(".csv"):
            # Сохраняем файл на диск
            file_path = os.path.join(app.static_folder, "uploaded_categories.csv")
            file.save(file_path)
            # Передаем путь к файлу в функцию
            storage.load_categories_from_csv(file_path)
            return redirect(url_for("categories"))
        return "Некорректный формат файла", 400

    # Выгрузка категорий в CSV
    @app.route("/export_categories_csv")
    def export_categories_csv():
        file_path = os.path.join(app.static_folder, "categories_export.csv")
        storage.export_categories_to_csv(file_path)
        return send_file(file_path, as_attachment=True)

    # Загрузка операций из CSV
    @app.route("/load_operations_csv", methods=["POST"])
    def load_operations_csv():
        if "file" not in request.files:
            return "Файл не найден", 400
        file = request.files["file"]
        if file.filename == "":
            return "Файл не выбран", 400
        if file and file.filename.endswith(".csv"):
            # Вариант 1: Передача данных из памяти
            #data = file.read().decode("utf-8")
            #storage.load_operations_from_csv(data)
            # Вариант 2: Сохранение файла на диск
            file_path = os.path.join(app.static_folder, "uploaded_operations.csv")
            file.save(file_path)
            storage.load_operations_from_csv(file_path)
            return redirect(url_for("index"))
        return "Некорректный формат файла", 400

    # Выгрузка операций в CSV
    @app.route("/export_operations_csv")
    def export_operations_csv():
        file_path = os.path.join(app.static_folder, "operations_export.csv")
        storage.export_operations_to_csv(file_path)
        return send_file(file_path, as_attachment=True)

    @app.route("/analysis")
    def show_analysis():
        analysis = FinancialAnalysis()
        expenses_chart_html = analysis.plot_expenses_by_category()
        income_vs_expenses_html = analysis.plot_income_vs_expenses()
        return render_template("analysis.html", expenses_chart=expenses_chart_html, income_vs_expenses_chart=income_vs_expenses_html)