# cli/tasks.py
import sqlite3
import uuid
from cli.utils import get_db_connection, current_timestamp

TABLE = "tasks"

def view_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id, title, description, due_date, priority, status FROM {TABLE} WHERE is_deleted=0")
    rows = cur.fetchall()
    if not rows:
        print("No tasks found.")
    else:
        for r in rows:
            print(f"- [{r[5]}] {r[1]} (Due: {r[3]})")
    conn.close()

def add_task():
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
        INSERT INTO {TABLE} (id, title, description, due_date, priority, status, last_modified, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
    """, (task_id, title, description, due_date, priority, status, ts))
    conn.commit()
    conn.close()
    print("✅ Task added.")

def edit_task():
    task_id = input("Enter Task ID to edit: ").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT title, description, due_date, priority, status FROM {TABLE} WHERE id=? AND is_deleted=0", (task_id,))
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
        WHERE id=?
    """, (title, description, due_date, priority, status, ts, task_id))
    conn.commit()
    conn.close()
    print("✅ Task updated.")

def delete_task():
    task_id = input("Enter Task ID to delete: ").strip()
    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE {TABLE} SET is_deleted=1, deleted_at=?, last_modified=?, synced=0 WHERE id=?", (ts, ts, task_id))
    conn.commit()
    conn.close()
    print("✅ Task deleted.")
