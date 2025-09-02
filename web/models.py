import sqlite3
import uuid
from web.utils import get_db_connection, current_timestamp

# ========================
# Users
# ========================
def create_user(db_path, username: str, password_hash: str, email: str = None):
    """Create a new user and return its UUID."""
    user_id = str(uuid.uuid4())
    with get_db_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO users (id, username, email, password_hash, last_modified) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, email, password_hash, current_timestamp())
        )
        conn.commit()
    return user_id

def get_user_by_username(db_path, username: str):
    """Fetch a user by username."""
    with get_db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username=? AND is_deleted=0",
            (username,)
        ).fetchone()

def get_user_by_email(db_path, email: str):
    """Fetch a user by email."""
    if not email:
        return None
    with get_db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email=? AND is_deleted=0",
            (email,)
        ).fetchone()

def get_user_by_id(db_path, user_id: str):
    """Fetch a user by ID."""
    with get_db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id=? AND is_deleted=0",
            (user_id,)
        ).fetchone()

# ========================
# Tasks
# ========================
def create_task(db_path, user_id, title, description=None, due_date=None, priority=2):
    """Create a new task for a user."""
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

# --- Update get_tasks FUNCTION (with new filter logic) ---
def get_tasks(db_path, user_id, search_term=None, status=None, priority=None, due_date=None):
    query = "SELECT * FROM tasks WHERE user_id=? AND is_deleted=0"
    params = [user_id]
    if search_term:
        query += " AND (title LIKE ?)"
        params.append(f'%{search_term}%')
    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if due_date:
        query += " AND due_date = ?"
        params.append(due_date)
    query += " ORDER BY last_modified DESC"
    with get_db_connection(db_path) as conn:
        return conn.execute(query, tuple(params)).fetchall()


def update_task(db_path, task_id, title=None, description=None, due_date=None, priority=None, status=None):
    """Update task details (any field can be updated)."""
    fields = []
    values = []

    if title is not None:
        fields.append("title=?")
        values.append(title)
    if description is not None:
        fields.append("description=?")
        values.append(description)
    if due_date is not None:
        fields.append("due_date=?")
        values.append(due_date)
    if priority is not None:
        fields.append("priority=?")
        values.append(priority)
    if status is not None:
        fields.append("status=?")
        values.append(status)

    # Always update last_modified
    fields.append("last_modified=?")
    values.append(current_timestamp())

    values.append(task_id)

    with get_db_connection(db_path) as conn:
        conn.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()

def update_task_status(db_path, task_id, status):
    """Update only the status of a task."""
    update_task(db_path, task_id, status=status)

def delete_task(db_path, task_id):
    """Soft delete a task."""
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
    """Create a new note for a user."""
    note_id = str(uuid.uuid4())
    with get_db_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO notes (id, user_id, content, last_modified) VALUES (?, ?, ?, ?)",
            (note_id, user_id, content, current_timestamp())
        )
        conn.commit()
    return note_id

# --- Update get_notes FUNCTION (with new filter logic) ---
def get_notes(db_path, user_id, search_term=None):
    query = "SELECT * FROM notes WHERE user_id=? AND is_deleted=0"
    params = [user_id]
    if search_term:
        query += " AND content LIKE ?"
        params.append(f'%{search_term}%')
    query += " ORDER BY last_modified DESC"
    with get_db_connection(db_path) as conn:
        return conn.execute(query, tuple(params)).fetchall()

def update_note(db_path, note_id, content):
    """Update the content of a note."""
    with get_db_connection(db_path) as conn:
        conn.execute(
            "UPDATE notes SET content=?, last_modified=? WHERE id=?",
            (content, current_timestamp(), note_id)
        )
        conn.commit()

def delete_note(db_path, note_id):
    """Soft delete a note."""
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
    """Create a new expense for a user."""
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
    """Get all expenses for a user (not deleted)."""
    with get_db_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM expenses WHERE user_id=? AND is_deleted=0",
            (user_id,)
        ).fetchall()

def update_expense(db_path, expense_id, amount=None, category=None, description=None, date=None):
    """Update any field of an expense."""
    fields = []
    values = []

    if amount is not None:
        fields.append("amount=?")
        values.append(amount)
    if category is not None:
        fields.append("category=?")
        values.append(category)
    if description is not None:
        fields.append("description=?")
        values.append(description)
    if date is not None:
        fields.append("date=?")
        values.append(date)

    # Always update last_modified
    fields.append("last_modified=?")
    values.append(current_timestamp())
    values.append(expense_id)

    with get_db_connection(db_path) as conn:
        conn.execute(f"UPDATE expenses SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()

def delete_expense(db_path, expense_id):
    """Soft delete an expense."""
    with get_db_connection(db_path) as conn:
        conn.execute(
            "UPDATE expenses SET is_deleted=1, deleted_at=?, last_modified=? WHERE id=?",
            (current_timestamp(), current_timestamp(), expense_id)
        )
        conn.commit()
