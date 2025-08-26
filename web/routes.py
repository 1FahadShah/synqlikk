from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from web.models import get_tasks, create_task, update_task, delete_task
from web.models import get_notes, create_note, update_note, delete_note
from web.models import get_expenses, create_expense, update_expense, delete_expense
from web.utils import current_timestamp

main_bp = Blueprint("main_bp", __name__)

# --------------------------
# Helper decorator
# --------------------------
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first", "danger")
            return redirect(url_for("auth_bp.login"))
        return f(*args, **kwargs)
    return decorated

# --------------------------
# Dashboard
# --------------------------
@main_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]

    tasks = get_tasks(current_app.config["DB_PATH"], user_id)
    notes = get_notes(current_app.config["DB_PATH"], user_id)
    expenses = get_expenses(current_app.config["DB_PATH"], user_id)

    return render_template("dashboard.html", tasks=tasks, notes=notes, expenses=expenses)

# --------------------------
# Task CRUD
# --------------------------
@main_bp.route("/task/add", methods=["POST"])
@login_required
def add_task():
    user_id = session["user_id"]
    title = request.form.get("title")
    description = request.form.get("description")
    due_date = request.form.get("due_date")
    priority = int(request.form.get("priority", 2))
    create_task(current_app.config["DB_PATH"], user_id, title, description, due_date, priority)
    flash("Task added successfully", "success")
    return redirect(url_for("main_bp.dashboard"))

@main_bp.route("/task/update/<task_id>", methods=["POST"])
@login_required
def edit_task(task_id):
    title = request.form.get("title")
    description = request.form.get("description")
    due_date = request.form.get("due_date")
    priority = int(request.form.get("priority", 2))
    status = request.form.get("status")
    update_task(current_app.config["DB_PATH"], task_id, title, description, due_date, priority, status)
    flash("Task updated successfully", "success")
    return redirect(url_for("main_bp.dashboard"))

@main_bp.route("/task/delete/<task_id>", methods=["POST"])
@login_required
def remove_task(task_id):
    delete_task(current_app.config["DB_PATH"], task_id)
    flash("Task deleted successfully", "success")
    return redirect(url_for("main_bp.dashboard"))

# --------------------------
# Notes CRUD
# --------------------------
@main_bp.route("/note/add", methods=["POST"])
@login_required
def add_note():
    content = request.form.get("content")
    create_note(current_app.config["DB_PATH"], session["user_id"], content)
    flash("Note added successfully", "success")
    return redirect(url_for("main_bp.dashboard"))

@main_bp.route("/note/update/<note_id>", methods=["POST"])
@login_required
def edit_note(note_id):
    content = request.form.get("content")
    update_note(current_app.config["DB_PATH"], note_id, content)
    flash("Note updated successfully", "success")
    return redirect(url_for("main_bp.dashboard"))

@main_bp.route("/note/delete/<note_id>", methods=["POST"])
@login_required
def remove_note(note_id):
    delete_note(current_app.config["DB_PATH"], note_id)
    flash("Note deleted successfully", "success")
    return redirect(url_for("main_bp.dashboard"))

# --------------------------
# Expenses CRUD
# --------------------------
@main_bp.route("/expense/add", methods=["POST"])
@login_required
def add_expense():
    amount = float(request.form.get("amount"))
    category = request.form.get("category")
    description = request.form.get("description")
    date = request.form.get("date")
    create_expense(current_app.config["DB_PATH"], session["user_id"], amount, category, description, date)
    flash("Expense added successfully", "success")
    return redirect(url_for("main_bp.dashboard"))

@main_bp.route("/expense/update/<expense_id>", methods=["POST"])
@login_required
def edit_expense(expense_id):
    amount = float(request.form.get("amount"))
    category = request.form.get("category")
    description = request.form.get("description")
    date = request.form.get("date")
    update_expense(current_app.config["DB_PATH"], expense_id, amount, category, description, date)
    flash("Expense updated successfully", "success")
    return redirect(url_for("main_bp.dashboard"))

@main_bp.route("/expense/delete/<expense_id>", methods=["POST"])
@login_required
def remove_expense(expense_id):
    delete_expense(current_app.config["DB_PATH"], expense_id)
    flash("Expense deleted successfully", "success")
    return redirect(url_for("main_bp.dashboard"))
