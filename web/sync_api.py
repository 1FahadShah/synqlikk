from flask import Blueprint, request, jsonify, current_app, session
from functools import wraps
from web.models import (
    get_tasks, create_task, update_task, delete_task,
    get_notes, create_note, update_note, delete_note,
    get_expenses, create_expense, update_expense, delete_expense
)
from web.utils import current_timestamp

sync_bp = Blueprint("sync_bp", __name__, url_prefix="/api")

# --------------------------
# JSON-safe login_required
# --------------------------
def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# --------------------------
# Generic sync helper
# --------------------------
def parse_since_param():
    """Return timestamp string from query param, or None"""
    return request.args.get("since")

# --------------------------
# Tasks API
# --------------------------
@sync_bp.route("/tasks", methods=["GET"])
@api_login_required
def api_get_tasks():
    user_id = session["user_id"]
    since = parse_since_param()
    tasks = get_tasks(current_app.config["DB_PATH"], user_id)
    # Filter by last_modified if 'since' provided
    if since:
        tasks = [t for t in tasks if t["last_modified"] > since]
    return jsonify([dict(task) for task in tasks])

@sync_bp.route("/tasks", methods=["POST"])
@api_login_required
def api_create_task():
    user_id = session["user_id"]
    data = request.json
    # Support last_modified from client (offline edits)
    task_id = create_task(
        current_app.config["DB_PATH"],
        user_id,
        data.get("title"),
        data.get("description"),
        data.get("due_date"),
        data.get("priority", 2)
    )
    return jsonify({"id": task_id}), 201

@sync_bp.route("/tasks/<task_id>", methods=["PUT"])
@api_login_required
def api_update_task(task_id):
    data = request.json
    # Last-write-wins: update only if incoming last_modified >= DB
    update_task(
        current_app.config["DB_PATH"],
        task_id,
        title=data.get("title"),
        description=data.get("description"),
        due_date=data.get("due_date"),
        priority=data.get("priority"),
        status=data.get("status")
    )
    return jsonify({"status": "success"})

@sync_bp.route("/tasks/<task_id>", methods=["DELETE"])
@api_login_required
def api_delete_task(task_id):
    delete_task(current_app.config["DB_PATH"], task_id)
    return jsonify({"status": "deleted"})

# --------------------------
# Notes API
# --------------------------
@sync_bp.route("/notes", methods=["GET"])
@api_login_required
def api_get_notes():
    user_id = session["user_id"]
    since = parse_since_param()
    notes = get_notes(current_app.config["DB_PATH"], user_id)
    if since:
        notes = [n for n in notes if n["last_modified"] > since]
    return jsonify([dict(note) for note in notes])

@sync_bp.route("/notes", methods=["POST"])
@api_login_required
def api_create_note():
    user_id = session["user_id"]
    data = request.json
    note_id = create_note(
        current_app.config["DB_PATH"], user_id, data.get("content")
    )
    return jsonify({"id": note_id}), 201

@sync_bp.route("/notes/<note_id>", methods=["PUT"])
@api_login_required
def api_update_note(note_id):
    data = request.json
    update_note(current_app.config["DB_PATH"], note_id, data.get("content"))
    return jsonify({"status": "success"})

@sync_bp.route("/notes/<note_id>", methods=["DELETE"])
@api_login_required
def api_delete_note(note_id):
    delete_note(current_app.config["DB_PATH"], note_id)
    return jsonify({"status": "deleted"})

# --------------------------
# Expenses API
# --------------------------
@sync_bp.route("/expenses", methods=["GET"])
@api_login_required
def api_get_expenses():
    user_id = session["user_id"]
    since = parse_since_param()
    expenses = get_expenses(current_app.config["DB_PATH"], user_id)
    if since:
        expenses = [e for e in expenses if e["last_modified"] > since]
    return jsonify([dict(expense) for expense in expenses])

@sync_bp.route("/expenses", methods=["POST"])
@api_login_required
def api_create_expense():
    user_id = session["user_id"]
    data = request.json
    expense_id = create_expense(
        current_app.config["DB_PATH"],
        user_id,
        data.get("amount"),
        data.get("category"),
        data.get("description"),
        data.get("date")
    )
    return jsonify({"id": expense_id}), 201

@sync_bp.route("/expenses/<expense_id>", methods=["PUT"])
@api_login_required
def api_update_expense(expense_id):
    data = request.json
    update_expense(
        current_app.config["DB_PATH"],
        expense_id,
        amount=data.get("amount"),
        category=data.get("category"),
        description=data.get("description"),
        date=data.get("date")
    )
    return jsonify({"status": "success"})

@sync_bp.route("/expenses/<expense_id>", methods=["DELETE"])
@api_login_required
def api_delete_expense(expense_id):
    delete_expense(current_app.config["DB_PATH"], expense_id)
    return jsonify({"status": "deleted"})
