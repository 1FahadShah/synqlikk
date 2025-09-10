import sqlite3
import uuid
from cli.utils import get_db_connection, current_timestamp, print_warning
from cli.auth import load_session

TABLE = "tasks"

def _get_user_id():
    _, user_id = load_session()
    if not user_id:
        print_warning("⚠️ You must log in before performing this action.")
        return None
    return user_id

def view_tasks():
    user_id = _get_user_id()
    if not user_id:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, title, description, due_date, priority, status
        FROM {TABLE}
        WHERE is_deleted=0 AND user_id=?
    """, (user_id,))
    rows = cur.fetchall()
    if not rows:
        print("No tasks found.")
    else:
        for r in rows:
            print(f"- [{r[5]}] {r[1]} (Due: {r[3]})")
    conn.close()

def add_task():
    user_id = _get_user_id()
    if not user_id:
        return

    title = input("Title: ").strip()
    description = input("Description: ").strip()
    due_date = input("Due date (YYYY-MM-DD): ").strip()
    priority = input("Priority (1-3): ").strip() or "2"
    status = "pending"

    task_id = str(uuid.uuid4())
    ts = current_timestamp()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {TABLE} (id, user_id, title, description, due_date, priority, status, last_modified, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (task_id, user_id, title, description, due_date, priority, status, ts))
    conn.commit()
    conn.close()
    print("✅ Task added.")

def edit_task():
    user_id = _get_user_id()
    if not user_id:
        return

    task_id = input("Enter Task ID to edit: ").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT title, description, due_date, priority, status
        FROM {TABLE}
        WHERE id=? AND is_deleted=0 AND user_id=?
    """, (task_id, user_id))
    row = cur.fetchone()
    if not row:
        print("Task not found.")
        return

    title = input(f"Title [{row[0]}]: ").strip() or row[0]
    description = input(f"Description [{row[1]}]: ").strip() or row[1]
    due_date = input(f"Due date [{row[2]}]: ").strip() or row[2]
    priority = input(f"Priority [{row[3]}]: ").strip() or row[3]
    status = input(f"Status [{row[4]}]: ").strip() or row[4]
    ts = current_timestamp()

    cur.execute(f"""
        UPDATE {TABLE}
        SET title=?, description=?, due_date=?, priority=?, status=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (title, description, due_date, priority, status, ts, task_id, user_id))
    conn.commit()
    conn.close()
    print("✅ Task updated.")

def delete_task():
    user_id = _get_user_id()
    if not user_id:
        return

    task_id = input("Enter Task ID to delete: ").strip()
    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE {TABLE}
        SET is_deleted=1, deleted_at=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (ts, ts, task_id, user_id))
    conn.commit()
    conn.close()
    print("✅ Task deleted.")
