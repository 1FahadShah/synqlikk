# cli/notes.py
import uuid
from tabulate import tabulate
from cli.utils import get_db_connection, current_timestamp, print_warning
from cli.auth import load_session

TABLE = "notes"

def _get_user_id():
    """Returns the current logged-in user's ID or None if not logged in."""
    _, user_id = load_session()
    if not user_id:
        print_warning("⚠️ You must log in before performing this action.")
        return None
    return user_id

def view_notes():
    """
    Views all notes for the logged-in user, displays them in a numbered table,
    and returns them as a list of dictionaries.
    """
    user_id = _get_user_id()
    if not user_id:
        return []

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, content, last_modified
        FROM {TABLE}
        WHERE is_deleted=0 AND user_id=?
        ORDER BY last_modified DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("\nNo notes found.")
        return []

    headers = ["#", "ID", "Content", "Last Modified"]
    table_data = []
    notes = []

    for i, row in enumerate(rows, 1):
        note_id, content, last_modified = row
        content_preview = (content[:60] + "...") if len(content) > 60 else content
        table_data.append([i, note_id[:8], content_preview, last_modified])
        notes.append({
            "id": note_id,
            "content": content,
            "last_modified": last_modified
        })

    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
    return notes

def add_note():
    """Adds a new note to the local database for the logged-in user."""
    user_id = _get_user_id()
    if not user_id:
        return

    content = input("Note content: ").strip()
    if not content:
        print("\nError: Content cannot be empty.")
        return

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
    print("\n✅ Note added locally. Run 'Sync with Server' to save it online.")

def edit_note():
    """Edits an existing note in the local database by selecting from the table."""
    user_id = _get_user_id()
    if not user_id:
        return

    notes = view_notes()
    if not notes:
        return

    try:
        choice = int(input("\nEnter the # of the Note to edit: ").strip())
        if not (1 <= choice <= len(notes)):
            raise ValueError
        note = notes[choice - 1]
    except (ValueError, IndexError):
        print("\nError: Invalid selection.")
        return

    print("\nEditing note. Press Enter to keep the current value.")
    content = input(f"Content [{note['content']}]: ").strip() or note['content']

    ts = current_timestamp()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE {TABLE} SET content=?, last_modified=?, synced=0
        WHERE id=? AND user_id=?
    """, (content, ts, note['id'], user_id))
    conn.commit()
    conn.close()
    print("\n✅ Note updated locally.")

def delete_note():
    """Marks a note as deleted in the local database by selecting from the table."""
    user_id = _get_user_id()
    if not user_id:
        return

    notes = view_notes()
    if not notes:
        return

    try:
        choice = int(input("\nEnter the # of the Note to delete: ").strip())
        if not (1 <= choice <= len(notes)):
            raise ValueError
        note_to_delete = notes[choice - 1]
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
    """, (ts, ts, note_to_delete['id'], user_id))
    conn.commit()
    conn.close()
    print("\n✅ Note marked for deletion. It will be removed on the next sync.")
