# cli/expenses.py
import sqlite3
import uuid
from cli.utils import get_db_connection, current_timestamp

TABLE = "expenses"

def view_expenses():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id, amount, category, description, date FROM {TABLE} WHERE is_deleted=0")
    rows = cur.fetchall()
    if not rows:
        print("No expenses found.")
    else:
        for r in rows:
            print(f"- {r[2]}: {r[1]} ({r[3]} on {r[4]})")
    conn.close()

def add_expense():
    amount = input("Amount: ").strip()
    category = input("Category: ").strip()
    description = input("Description: ").strip()
    date = input("Date (YYYY-MM-DD): ").strip()

    exp_id = str(uuid.uuid4())
    ts = current_timestamp()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {TABLE} (id, amount, category, description, date, last_modified, synced)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (exp_id, amount, category, description, date, ts))
    conn.commit()
    conn.close()
    print("✅ Expense added.")

def edit_expense():
    exp_id = input("Enter Expense ID to edit: ").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT amount, category, description, date FROM {TABLE} WHERE id=? AND is_deleted=0", (exp_id,))
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
        UPDATE {TABLE} SET amount=?, category=?, description=?, date=?, last_modified=?, synced=0 WHERE id=?
    """, (amount, category, description, date, ts, exp_id))
    conn.commit()
    conn.close()
    print("✅ Expense updated.")

def delete_expense():
    exp_id = input("Enter Expense ID to delete: ").strip()
    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE {TABLE} SET is_deleted=1, deleted_at=?, last_modified=?, synced=0 WHERE id=?", (ts, ts, exp_id))
    conn.commit()
    conn.close()
    print("✅ Expense deleted.")
