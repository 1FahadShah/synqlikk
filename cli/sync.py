import requests
import json
from pathlib import Path  # ✅ FIXED
from .constants import SYNC_ENDPOINT, DEFAULT_TIMEOUT
from .auth import get_auth_headers, load_session, save_session
from .utils import get_db_connection, current_timestamp
from .exceptions import APIError

TABLES = ["tasks", "notes", "expenses"]
SESSION_FILE = Path(".synqlikk_session.json")


def sync_all(force_full: bool = False):
    """
    Performs a full two-way sync:
    1. Gathers local changes.
    2. Pushes them to server.
    3. Applies server updates locally.
    4. Resolves conflicts.

    If force_full=True, performs a full pull of all server records to local DB.
    """
    if force_full:
        print("\n🔄 Pulling all server data (full sync)...")
    else:
        print("\n🔄 Starting two-way sync...")

    try:
        headers = get_auth_headers()
        token, user_id = load_session()
        if not user_id:
            raise APIError("Could not find user_id in session.")
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        return

    conn = get_db_connection()

    # --- 1. GATHER LOCAL CHANGES ---
    payload = {table: [] for table in TABLES}

    if not force_full:
        for table in TABLES:
            local_changes = conn.execute(
                f"SELECT * FROM {table} WHERE user_id = ? AND synced = 0",
                (user_id,)
            ).fetchall()
            if local_changes:
                payload[table] = [dict(row) for row in local_changes]

    # Safely read last sync time
    if SESSION_FILE.exists():
        try:
            session_data = json.loads(SESSION_FILE.read_text())
            payload['last_sync_time'] = None if force_full else session_data.get('last_sync_time')
        except json.JSONDecodeError:
            session_data = {}
            payload['last_sync_time'] = None
    else:
        session_data = {}
        payload['last_sync_time'] = None

    if not force_full:
        print(f"   Pushing {len(payload['tasks'])} tasks, "
              f"{len(payload['notes'])} notes, "
              f"{len(payload['expenses'])} expenses...")

    # --- 2. PUSH TO SERVER & PULL RESPONSE ---
    try:
        response = requests.post(SYNC_ENDPOINT, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        server_data = response.json()
        print("   ✅ Connected to the server.")
    except Exception as e:
        print(f"❌ Sync failed. Could not connect to the server: {e}")
        conn.close()
        return

    # --- 3. APPLY SERVER CHANGES LOCALLY ---
    items_pulled = 0
    for table in TABLES:
        for item in server_data.get(table, []):
            items_pulled += 1
            item['synced'] = 1
            columns = ', '.join(item.keys())
            placeholders = ', '.join(['?'] * len(item))
            conn.execute(
                f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})",
                tuple(item.values())
            )

    print(f"   Pulled {items_pulled} new/updated items from the server.")

    # --- 4. FINALIZE AND CLEAN UP ---
    for table in TABLES:
        conn.execute(f"UPDATE {table} SET synced = 1 WHERE user_id = ? AND synced = 0 AND is_deleted = 0", (user_id,))
        conn.execute(f"DELETE FROM {table} WHERE user_id = ? AND synced = 0 AND is_deleted = 1", (user_id,))

    conn.commit()
    conn.close()

    # Update session file safely
    session_data['last_sync_time'] = server_data.get('server_time')
    SESSION_FILE.write_text(json.dumps(session_data, indent=2))

    if server_data.get('conflicts'):
        print(f"⚠️  Resolved {len(server_data['conflicts'])} conflicts (server version kept).")

    print("✅ Sync complete!")
