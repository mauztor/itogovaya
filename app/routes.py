from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from app.storage import Storage
from app.analysis import FinancialAnalysis

def init_routes(app):
    storage = Storage()
    analysis = FinancialAnalysis()

    @app.route("/")
    def index():
        balance = analysis.get_balance()
        return render_template("index.html", balance=balance)

    @app.route("/add_operation", methods=["GET", "POST"])
    def add_operation():
        if request.method == "POST":
            amount = float(request.form["amount"])
            category_id = int(request.form["category_id"])
            date = request.form["date"]
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
        operations = storage.get_operations()
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
            storage.load_categories_from_csv(file)
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
            storage.load_operations_from_csv(file)
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
        # Генерация графиков и сохранение их в статические файлы
        plot_paths = {
            "expenses_by_category": os.path.join(app.static_folder, "expenses_by_category.png"),
            "top_expenses": os.path.join(app.static_folder, "top_expenses.png"),
            "income_vs_expenses": os.path.join(app.static_folder, "income_vs_expenses.png"),
        }
        analysis.plot_expenses_by_category(plot_paths["expenses_by_category"])
        analysis.plot_top_expenses(plot_paths["top_expenses"])
        analysis.plot_income_vs_expenses(plot_paths["income_vs_expenses"])
        return render_template("analysis.html", plot_paths=plot_paths)