from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from .models import (get_tasks, create_task, update_task, delete_task,
                     get_notes, create_note, update_note, delete_note,
                     get_expenses, create_expense, update_expense, delete_expense,
                     get_user_by_id)
from functools import wraps

main_bp = Blueprint("main_bp", __name__)

# --- Helper Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access this page.", "warning")
            return redirect(url_for("auth_bp.login"))
        return f(*args, **kwargs)
    return decorated_function

# --- Main Pages ---
@main_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    db_path = current_app.config["DB_PATH"]
    # For the dashboard, we get all items without filters
    tasks = get_tasks(db_path, user_id)
    notes = get_notes(db_path, user_id)
    expenses = get_expenses(db_path, user_id)
    return render_template("dashboard.html", tasks=tasks, notes=notes, expenses=expenses)

@main_bp.route("/tasks")
@login_required
def tasks_page():
    user_id = session["user_id"]
    db_path = current_app.config["DB_PATH"]

    # **FIX**: Get filter values from URL query parameters (e.g., /tasks?q=mysearch)
    search_term = request.args.get('q')
    status = request.args.get('status')
    priority = request.args.get('priority')
    due_date = request.args.get('due_date')

    # Pass the retrieved filters to the database function
    all_tasks = get_tasks(db_path, user_id, search_term, status, priority, due_date)
    return render_template("tasks.html", tasks=all_tasks)

@main_bp.route("/notes")
@login_required
def notes_page():
    user_id = session["user_id"]
    db_path = current_app.config["DB_PATH"]

    # **FIX**: Get search term from URL
    search_term = request.args.get('q')

    all_notes = get_notes(db_path, user_id, search_term)
    return render_template("notes.html", notes=all_notes)

@main_bp.route("/expenses")
@login_required
def expenses_page():
    user_id = session["user_id"]
    db_path = current_app.config["DB_PATH"]

    # **FIX**: Get filter values from URL
    search_term = request.args.get('q')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    all_expenses = get_expenses(db_path, user_id, search_term, start_date, end_date)
    return render_template("expenses.html", expenses=all_expenses)

@main_bp.route("/profile")
@login_required
def profile_page():
    user = get_user_by_id(current_app.config["DB_PATH"], session["user_id"])
    return render_template("profile.html", user=user)

# --- Task CRUD Actions ---
@main_bp.route("/task/add", methods=["POST"])
@login_required
def add_task():
    create_task(
        db_path=current_app.config["DB_PATH"],
        user_id=session["user_id"],
        title=request.form.get("title"),
        description=request.form.get("description"),
        due_date=request.form.get("due_date"),
        priority=int(request.form.get("priority", 2)),
        status=request.form.get("status", 'pending')
    )
    flash("Task added successfully.", "success")
    # **IMPROVEMENT**: Redirect back to the tasks page
    return redirect(url_for("main_bp.tasks_page"))

@main_bp.route("/task/edit/<task_id>", methods=["POST"])
@login_required
def edit_task(task_id):
    update_task(
        db_path=current_app.config["DB_PATH"],
        task_id=task_id,
        title=request.form.get("title"),
        description=request.form.get("description"),
        due_date=request.form.get("due_date"),
        priority=int(request.form.get("priority", 2)),
        status=request.form.get("status")
    )
    flash("Task updated successfully.", "success")
    # **IMPROVEMENT**: Redirect back to the previous page (dashboard or tasks page)
    return redirect(request.referrer or url_for('main_bp.tasks_page'))

@main_bp.route("/task/delete/<task_id>", methods=["POST"])
@login_required
def remove_task(task_id):
    delete_task(current_app.config["DB_PATH"], task_id)
    flash("Task deleted.", "info")
    return redirect(request.referrer or url_for('main_bp.tasks_page'))

# --- Note CRUD Actions ---
@main_bp.route("/note/add", methods=["POST"])
@login_required
def add_note():
    content = request.form.get("content")
    if content:
        create_note(current_app.config["DB_PATH"], session["user_id"], content)
        flash("Note added successfully.", "success")
    return redirect(url_for("main_bp.notes_page"))

@main_bp.route("/note/edit/<note_id>", methods=["POST"])
@login_required
def edit_note(note_id):
    content = request.form.get("content")
    if content:
        update_note(current_app.config["DB_PATH"], note_id, content)
        flash("Note updated successfully.", "success")
    return redirect(request.referrer or url_for('main_bp.notes_page'))

@main_bp.route("/note/delete/<note_id>", methods=["POST"])
@login_required
def remove_note(note_id):
    delete_note(current_app.config["DB_PATH"], note_id)
    flash("Note deleted.", "info")
    return redirect(request.referrer or url_for('main_bp.notes_page'))

# --- Expense CRUD Actions ---
@main_bp.route("/expense/add", methods=["POST"])
@login_required
def add_expense():
    create_expense(
        db_path=current_app.config["DB_PATH"],
        user_id=session["user_id"],
        amount=float(request.form.get("amount")),
        category=request.form.get("category"),
        description=request.form.get("description"),
        date=request.form.get("date")
    )
    flash("Expense added successfully.", "success")
    return redirect(url_for("main_bp.expenses_page"))

@main_bp.route("/expense/edit/<expense_id>", methods=["POST"])
@login_required
def edit_expense(expense_id):
    update_expense(
        db_path=current_app.config["DB_PATH"],
        expense_id=expense_id,
        amount=float(request.form.get("amount")),
        category=request.form.get("category"),
        description=request.form.get("description"),
        date=request.form.get("date")
    )
    flash("Expense updated successfully.", "success")
    return redirect(request.referrer or url_for('main_bp.expenses_page'))

@main_bp.route("/expense/delete/<expense_id>", methods=["POST"])
@login_required
def remove_expense(expense_id):
    delete_expense(current_app.config["DB_PATH"], expense_id)
    flash("Expense deleted.", "info")
    return redirect(request.referrer or url_for('main_bp.expenses_page'))