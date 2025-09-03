from flask import Blueprint, request, jsonify, current_app, session
from functools import wraps
from web.models import (
    get_tasks, create_task, update_task, delete_task,
    get_notes, create_note, update_note, delete_note,
    get_expenses, create_expense, update_expense, delete_expense,
    get_user_by_username # Import the missing model function
)
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

sync_bp = Blueprint("sync_bp", __name__, url_prefix="/api")

# IMPORTANT: This secret key must match the one used in your config.py
# and should be loaded from your .env file in a real application.
JWT_SECRET = 'your-super-secret-key-for-jwt'

# --------------------------
# API Authentication Routes
# --------------------------

@sync_bp.route("/register", methods=["POST"])
def api_register():
    """Handles CLI user registration and returns JSON."""
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required."}), 400

    db_path = current_app.config["DB_PATH"]
    username = data['username']

    if get_user_by_username(db_path, username):
        return jsonify({"error": "Username already exists."}), 409

    password_hash = generate_password_hash(data['password'])
    user_id = create_user(db_path, username, password_hash)

    return jsonify({"message": "User created successfully", "user_id": user_id}), 201

@sync_bp.route("/login", methods=["POST"])
def api_login():
    """Handles CLI user login and returns a JWT token."""
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required."}), 400

    db_path = current_app.config["DB_PATH"]
    user = get_user_by_username(db_path, data['username'])

    if not user or not check_password_hash(user["password_hash"], data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create a token that the CLI can store and use for future requests
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token, "user_id": user['id']})


# --------------------------
# Token-based login_required decorator
# --------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            # Format is "Bearer <token>"
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"error": "Unauthorized: Token is missing"}), 401

        try:
            # Decode the token to ensure it's valid and get the user_id
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            # Store the user_id from the token in the session for this request
            session['user_id'] = data['user_id']
        except:
            return jsonify({"error": "Unauthorized: Token is invalid"}), 401

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
@token_required
def api_get_tasks():
    user_id = session["user_id"]
    since = parse_since_param()
    tasks = get_tasks(current_app.config["DB_PATH"], user_id)
    # Filter by last_modified if 'since' provided
    if since:
        tasks = [t for t in tasks if t["last_modified"] > since]
    return jsonify([dict(task) for task in tasks])

@sync_bp.route("/tasks", methods=["POST"])
@token_required
def api_create_task():
    user_id = session["user_id"]
    data = request.json
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
@token_required
def api_update_task(task_id):
    data = request.json
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
@token_required
def api_delete_task(task_id):
    delete_task(current_app.config["DB_PATH"], task_id)
    return jsonify({"status": "deleted"})

# --------------------------
# Notes API
# --------------------------
@sync_bp.route("/notes", methods=["GET"])
@token_required
def api_get_notes():
    user_id = session["user_id"]
    since = parse_since_param()
    notes = get_notes(current_app.config["DB_PATH"], user_id)
    if since:
        notes = [n for n in notes if n["last_modified"] > since]
    return jsonify([dict(note) for note in notes])

@sync_bp.route("/notes", methods=["POST"])
@token_required
def api_create_note():
    user_id = session["user_id"]
    data = request.json
    note_id = create_note(
        current_app.config["DB_PATH"], user_id, data.get("content")
    )
    return jsonify({"id": note_id}), 201

@sync_bp.route("/notes/<note_id>", methods=["PUT"])
@token_required
def api_update_note(note_id):
    data = request.json
    update_note(current_app.config["DB_PATH"], note_id, data.get("content"))
    return jsonify({"status": "success"})

@sync_bp.route("/notes/<note_id>", methods=["DELETE"])
@token_required
def api_delete_note(note_id):
    delete_note(current_app.config["DB_PATH"], note_id)
    return jsonify({"status": "deleted"})

# --------------------------
# Expenses API
# --------------------------
@sync_bp.route("/expenses", methods=["GET"])
@token_required
def api_get_expenses():
    user_id = session["user_id"]
    since = parse_since_param()
    expenses = get_expenses(current_app.config["DB_PATH"], user_id)
    if since:
        expenses = [e for e in expenses if e["last_modified"] > since]
    return jsonify([dict(expense) for expense in expenses])

@sync_bp.route("/expenses", methods=["POST"])
@token_required
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
@token_required
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
@token_required
def api_delete_expense(expense_id):
    delete_expense(current_app.config["DB_PATH"], expense_id)
    return jsonify({"status": "deleted"})