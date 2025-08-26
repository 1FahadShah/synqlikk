import sqlite3
import uuid
from web.utils import get_db_connection, current_timestamp

# ========================
# Users
# ========================
def create_user(db_path, username: str, password_hash: str, email: str = None):
    user_id = str(uuid.uuid4())
    with get_db_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO users (id, username, email, password_hash, last_modified) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, email, password_hash, current_timestamp())
        )
        conn.commit()
    return user_id

def get_user_by_username(db_path, username: str):
    with get_db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username=? AND is_deleted=0",
            (username,)
        ).fetchone()

def get_user_by_email(db_path, email: str):
    if not email:
        return None
    with get_db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email=? AND is_deleted=0",
            (email,)
        ).fetchone()

# ========================
# Tasks
# ========================
def create_task(db_path, user_id, title, description=None, due_date=None, priority=2):
    task_id = str(uuid.uuid4())
    with get_db_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO tasks (id, user_id, title, description, due_date, priority, last_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (task_id, user_id, title, description, due_date, priority, current_timestamp())
        )
        conn.commit()
    return task_id

def get_tasks(db_path, user_id):
    with get_db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM tasks WHERE user_id=? AND is_deleted=0",
            (user_id,)
        ).fetchall()

def update_task_status(db_path, task_id, status):
    with get_db_connection(db_path) as conn:
        conn.execute(
            "UPDATE tasks SET status=?, last_modified=? WHERE id=?",
            (status, current_timestamp(), task_id)
        )
        conn.commit()

def delete_task(db_path, task_id):
    with get_db_connection(db_path) as conn:
        conn.execute(
            "UPDATE tasks SET is_deleted=1, deleted_at=?, last_modified=? WHERE id=?",
            (current_timestamp(), current_timestamp(), task_id)
        )
        conn.commit()

# ========================
# Notes
# ========================
def create_note(db_path, user_id, content):
    note_id = str(uuid.uuid4())
    with get_db_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO notes (id, user_id, content, last_modified) VALUES (?, ?, ?, ?)",
            (note_id, user_id, content, current_timestamp())
        )
        conn.commit()
    return note_id

def get_notes(db_path, user_id):
    with get_db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM notes WHERE user_id=? AND is_deleted=0",
            (user_id,)
        ).fetchall()

def delete_note(db_path, note_id):
    with get_db_connection(db_path) as conn:
        conn.execute(
            "UPDATE notes SET is_deleted=1, deleted_at=?, last_modified=? WHERE id=?",
            (current_timestamp(), current_timestamp(), note_id)
        )
        conn.commit()

# ========================
# Expenses
# ========================
def create_expense(db_path, user_id, amount, category, description=None, date=None):
    expense_id = str(uuid.uuid4())
    with get_db_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO expenses (id, user_id, amount, category, description, date, last_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (expense_id, user_id, amount, category, description, date, current_timestamp())
        )
        conn.commit()
    return expense_id

def get_expenses(db_path, user_id):
    with get_db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM expenses WHERE user_id=? AND is_deleted=0",
            (user_id,)
        ).fetchall()

def delete_expense(db_path, expense_id):
    with get_db_connection(db_path) as conn:
        conn.execute(
            "UPDATE expenses SET is_deleted=1, deleted_at=?, last_modified=? WHERE id=?",
            (current_timestamp(), current_timestamp(), expense_id)
        )
        conn.commit()
