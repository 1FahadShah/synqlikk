import sqlite3
import uuid
from cli.utils import get_db_connection, current_timestamp, print_warning
from cli.auth import load_session

TABLE = "expenses"

def _get_user_id():
    _, user_id = load_session()
    if not user_id:
        print_warning("⚠️ You must log in before performing this action.")
        return None
    return user_id

def view_expenses():
    user_id = _get_user_id()
    if not user_id:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, amount, category, description, date
        FROM {TABLE} WHERE is_deleted=0 AND user_id=?
    """, (user_id,))
    rows = cur.fetchall()
    if not rows:
        print("No expenses found.")
    else:
        for r in rows:
            print(f"- {r[2]}: {r[1]} ({r[3]} on {r[4]})")
    conn.close()

def add_expense():
    user_id = _get_user_id()
    if not user_id:
        return

    amount = input("Amount: ").strip()
    category = input("Category: ").strip()
    description = input("Description: ").strip()
    date = input("Date (YYYY-MM-DD): ").strip()

    exp_id = str(uuid.uuid4())
    ts = current_timestamp()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {TABLE} (id, user_id, amount, category, description, date, last_modified, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
    """, (exp_id, user_id, amount, category, description, date, ts))
    conn.commit()
    conn.close()
    print("✅ Expense added.")

def edit_expense():
    user_id = _get_user_id()
    if not user_id:
        return

    exp_id = input("Enter Expense ID to edit: ").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT amount, category, description, date
        FROM {TABLE}
        WHERE id=? AND is_deleted=0 AND user_id=?
    """, (exp_id, user_id))
    row = cur.fetchone()
    if not row:
        print("Expense not found.")
        return

    amount = input(f"Amount [{row[0]}]: ").strip() or row[0]
    category = input(f"Category [{row[1]}]: ").strip() or row[1]
    description = input(f"Description [{row[2]}]: ").strip() or row[2]
    date = input(f"Date [{row[3]}]: ").strip() or row[3]
    ts = current_timestamp()

    cur.execute(f"""
        UPDATE {TABLE}
        SET amount=?, category=?, description=?, date=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (amount, category, description, date, ts, exp_id, user_id))
    conn.commit()
    conn.close()
    print("✅ Expense updated.")

def delete_expense():
    user_id = _get_user_id()
    if not user_id:
        return

    exp_id = input("Enter Expense ID to delete: ").strip()
    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE {TABLE}
        SET is_deleted=1, deleted_at=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (ts, ts, exp_id, user_id))
    conn.commit()
    conn.close()
    print("✅ Expense deleted.")
