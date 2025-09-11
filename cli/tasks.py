# cli/tasks.py
import uuid
from tabulate import tabulate
from cli.utils import get_db_connection, current_timestamp, print_warning
from cli.auth import load_session

TABLE = "tasks"

# Standardized status options
STATUS_OPTIONS = ["pending", "in_progress", "completed"]

def _get_user_id():
    _, user_id = load_session()
    if not user_id:
        print_warning("⚠️ You must log in before performing this action.")
        return None
    return user_id

def view_tasks():
    """
    Displays tasks in a table with sequence numbers and returns the full list for CRUD actions.
    """
    user_id = _get_user_id()
    if not user_id:
        return []

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, title, description, due_date, priority, status
        FROM {TABLE}
        WHERE is_deleted=0 AND user_id=?
        ORDER BY last_modified DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("\n⚠️ No tasks found.")
        return []

    headers = ["#", "ID", "Title", "Status", "Priority", "Due Date"]
    table_data = [
        [i, r[0][:8], r[1], r[5], r[4], r[3]] for i, r in enumerate(rows, 1)
    ]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

    return [
        {"id": r[0], "title": r[1], "description": r[2], "due_date": r[3], "priority": r[4], "status": r[5]}
        for r in rows
    ]

def add_task():
    user_id = _get_user_id()
    if not user_id:
        return

    title = input("Title: ").strip()
    if not title:
        print("❌ Title is required.")
        return

    description = input("Description (optional): ").strip()
    due_date = input("Due date (YYYY-MM-DD, optional): ").strip()
    priority = input("Priority (1=High, 2=Medium, 3=Low) [2]: ").strip() or "2"
    status = "pending"  # new tasks always start as pending

    task_id = str(uuid.uuid4())
    ts = current_timestamp()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {TABLE} (id, user_id, title, description, due_date, priority, status, last_modified, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (task_id, user_id, title, description, due_date, int(priority), status, ts))
    conn.commit()
    conn.close()
    print("\n✅ Task added locally. Run 'Sync' to push online.")

def edit_task():
    user_id = _get_user_id()
    if not user_id:
        return

    tasks = view_tasks()
    if not tasks:
        return

    try:
        choice = int(input("\nEnter the # of the task to edit: ").strip())
        if not (1 <= choice <= len(tasks)):
            raise ValueError
        task = tasks[choice - 1]
    except (ValueError, IndexError):
        print("\n❌ Invalid selection.")
        return

    print("\n✏️ Editing task. Press Enter to keep current values.")
    title = input(f"Title [{task['title']}]: ").strip() or task['title']
    description = input(f"Description [{task['description']}]: ").strip() or task['description']
    due_date = input(f"Due date [{task['due_date']}]: ").strip() or task['due_date']
    priority = input(f"Priority [{task['priority']}]: ").strip() or task['priority']

    # status selection menu (final fix)
    print("\nSelect a new status:")
    for i, option in enumerate(STATUS_OPTIONS, 1):
        print(f"  {i}. {option.replace('_', ' ').title()}")
    status_choice = input(f"Status [{task['status']}]: ").strip()
    if status_choice:
        try:
            status = STATUS_OPTIONS[int(status_choice) - 1]
        except (ValueError, IndexError):
            print("\n⚠️ Invalid status selection. Keeping original value.")
            status = task['status']
    else:
        status = task['status']

    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE {TABLE}
        SET title=?, description=?, due_date=?, priority=?, status=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (title, description, due_date, int(priority), status, ts, task['id'], user_id))
    conn.commit()
    conn.close()
    print("\n✅ Task updated locally.")

def delete_task():
    user_id = _get_user_id()
    if not user_id:
        return

    tasks = view_tasks()
    if not tasks:
        return

    try:
        choice = int(input("\nEnter the # of the task to delete: ").strip())
        if not (1 <= choice <= len(tasks)):
            raise ValueError
        task = tasks[choice - 1]
    except (ValueError, IndexError):
        print("\n❌ Invalid selection.")
        return

    confirm = input(f"⚠️ Are you sure you want to delete '{task['title']}'? (y/N): ").strip().lower()
    if confirm != "y":
        print("❌ Deletion cancelled.")
        return

    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE {TABLE}
        SET is_deleted=1, deleted_at=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (ts, ts, task['id'], user_id))
    conn.commit()
    conn.close()
    print("\n✅ Task marked for deletion. Will be removed on next sync.")
