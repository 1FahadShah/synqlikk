# cli/notes.py
import sqlite3
import uuid
from cli.utils import get_db_connection, current_timestamp

TABLE = "notes"

def view_notes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id, content FROM {TABLE} WHERE is_deleted=0")
    rows = cur.fetchall()
    if not rows:
        print("No notes found.")
    else:
        for r in rows:
            print(f"- {r[1]}")
    conn.close()

def add_note():
    content = input("Note content: ").strip()
    note_id = str(uuid.uuid4())
    ts = current_timestamp()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {TABLE} (id, content, last_modified, synced) VALUES (?, ?, ?, 0)", (note_id, content, ts))
    conn.commit()
    conn.close()
    print("✅ Note added.")

def edit_note():
    note_id = input("Enter Note ID to edit: ").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT content FROM {TABLE} WHERE id=? AND is_deleted=0", (note_id,))
    row = cur.fetchone()
    if not row:
        print("Note not found.")
        return

    content = input(f"Content [{row[0]}]: ").strip() or row[0]
    ts = current_timestamp()
    cur.execute(f"UPDATE {TABLE} SET content=?, last_modified=?, synced=0 WHERE id=?", (content, ts, note_id))
    conn.commit()
    conn.close()
    print("✅ Note updated.")

def delete_note():
    note_id = input("Enter Note ID to delete: ").strip()
    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE {TABLE} SET is_deleted=1, deleted_at=?, last_modified=?, synced=0 WHERE id=?", (ts, ts, note_id))
    conn.commit()
    conn.close()
    print("✅ Note deleted.")
