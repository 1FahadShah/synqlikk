import sqlite3
import uuid
from cli.utils import get_db_connection, current_timestamp, print_warning
from cli.auth import load_session

TABLE = "notes"

def _get_user_id():
    _, user_id = load_session()
    if not user_id:
        print_warning("⚠️ You must log in before performing this action.")
        return None
    return user_id

def view_notes():
    user_id = _get_user_id()
    if not user_id:
        return

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id, content FROM {TABLE} WHERE is_deleted=0 AND user_id=?", (user_id,))
    rows = cur.fetchall()
    if not rows:
        print("No notes found.")
    else:
        for r in rows:
            print(f"- {r[1]}")
    conn.close()

def add_note():
    user_id = _get_user_id()
    if not user_id:
        return

    content = input("Note content: ").strip()
    note_id = str(uuid.uuid4())
    ts = current_timestamp()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {TABLE} (id, user_id, content, last_modified, synced)
        VALUES (?, ?, ?, ?, 0)
    """, (note_id, user_id, content, ts))
    conn.commit()
    conn.close()
    print("✅ Note added.")

def edit_note():
    user_id = _get_user_id()
    if not user_id:
        return

    note_id = input("Enter Note ID to edit: ").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT content FROM {TABLE} WHERE id=? AND is_deleted=0 AND user_id=?", (note_id, user_id))
    row = cur.fetchone()
    if not row:
        print("Note not found.")
        return

    content = input(f"Content [{row[0]}]: ").strip() or row[0]
    ts = current_timestamp()
    cur.execute(f"""
        UPDATE {TABLE} SET content=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (content, ts, note_id, user_id))
    conn.commit()
    conn.close()
    print("✅ Note updated.")

def delete_note():
    user_id = _get_user_id()
    if not user_id:
        return

    note_id = input("Enter Note ID to delete: ").strip()
    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE {TABLE}
        SET is_deleted=1, deleted_at=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (ts, ts, note_id, user_id))
    conn.commit()
    conn.close()
    print("✅ Note deleted.")
