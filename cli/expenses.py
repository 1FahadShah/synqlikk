# cli/expenses.py
import uuid
from tabulate import tabulate
from cli.utils import get_db_connection, current_timestamp, print_warning
from cli.auth import load_session

TABLE = "expenses"

def _get_user_id():
    """Returns the logged-in user's ID or None if not logged in."""
    _, user_id = load_session()
    if not user_id:
        print_warning("⚠️ You must log in before performing this action.")
        return None
    return user_id

def view_expenses():
    """
    Views all expenses for the logged-in user, displays them in a numbered table,
    and returns them as a list of dictionaries.
    """
    user_id = _get_user_id()
    if not user_id:
        return []

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, amount, category, description, date, last_modified
        FROM {TABLE}
        WHERE is_deleted=0 AND user_id=?
        ORDER BY date DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("\nNo expenses found.")
        return []

    headers = ["#", "ID", "Amount", "Category", "Date", "Description"]
    table_data = []
    expenses = []

    for i, row in enumerate(rows, 1):
        exp_id, amount, category, description, date, last_modified = row
        table_data.append([
            i,
            exp_id[:8],
            f"{float(amount):.2f}",
            category,
            date,
            description or ""
        ])
        expenses.append({
            "id": exp_id,
            "amount": float(amount),
            "category": category,
            "description": description,
            "date": date,
            "last_modified": last_modified
        })

    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
    return expenses

def add_expense():
    """Adds a new expense to the local database for the logged-in user."""
    user_id = _get_user_id()
    if not user_id:
        return

    try:
        amount = float(input("Amount: ").strip())
    except ValueError:
        print("\nError: Amount must be a valid number.")
        return

    category = input("Category: ").strip()
    date = input("Date (YYYY-MM-DD): ").strip()
    description = input("Description (optional): ").strip()

    if not category or not date:
        print("\nError: Category and Date are required.")
        return

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
    print("\n✅ Expense added locally. Run 'Sync with Server' to upload it online.")

def edit_expense():
    """Edits an existing expense in the local database by selecting from the table."""
    user_id = _get_user_id()
    if not user_id:
        return

    expenses = view_expenses()
    if not expenses:
        return

    try:
        choice = int(input("\nEnter the # of the Expense to edit: ").strip())
        if not (1 <= choice <= len(expenses)):
            raise ValueError
        expense = expenses[choice - 1]
    except (ValueError, IndexError):
        print("\nError: Invalid selection.")
        return

    print("\nEditing expense. Press Enter to keep the current value.")
    amount = input(f"Amount [{expense['amount']:.2f}]: ").strip() or expense['amount']
    category = input(f"Category [{expense['category']}]: ").strip() or expense['category']
    date = input(f"Date [{expense['date']}]: ").strip() or expense['date']
    description = input(f"Description [{expense.get('description', '')}]: ").strip() or expense.get('description', '')

    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE {TABLE}
        SET amount=?, category=?, date=?, description=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (float(amount), category, date, description, ts, expense['id'], user_id))
    conn.commit()
    conn.close()
    print("\n✅ Expense updated locally.")

def delete_expense():
    """Marks an expense as deleted in the local database by selecting from the table."""
    user_id = _get_user_id()
    if not user_id:
        return

    expenses = view_expenses()
    if not expenses:
        return

    try:
        choice = int(input("\nEnter the # of the Expense to delete: ").strip())
        if not (1 <= choice <= len(expenses)):
            raise ValueError
        expense_to_delete = expenses[choice - 1]
    except (ValueError, IndexError):
        print("\nError: Invalid selection.")
        return

    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE {TABLE}
        SET is_deleted=1, deleted_at=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (ts, ts, expense_to_delete['id'], user_id))
    conn.commit()
    conn.close()
    print("\n✅ Expense marked for deletion. It will be removed on the next sync.")
