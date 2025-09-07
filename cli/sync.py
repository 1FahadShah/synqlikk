# cli/sync.py
import requests
from .constants import SYNC_ENDPOINT, DEFAULT_TIMEOUT
from .auth import get_auth_headers, load_session, save_session
from .utils import get_db_connection, current_timestamp
from .exceptions import APIError

TABLES = ["tasks", "notes", "expenses"]

def sync_all():
    """
    Performs a full two-way sync in a single transaction:
    1. Gathers all local changes (new, updated, deleted).
    2. Pushes them to the server in a single batch.
    3. Receives a batch of server changes in the response.
    4. Applies server changes and conflicts locally.
    """
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
    payload = {
        "tasks": [],
        "notes": [],
        "expenses": [],
    }

    for table in TABLES:
        # Get all rows that have been created or modified locally (synced = 0)
        local_changes = conn.execute(
            f"SELECT * FROM {table} WHERE user_id = ? AND synced = 0",
            (user_id,)
        ).fetchall()

        if local_changes:
            payload[table] = [dict(row) for row in local_changes]

    # Add the last sync time to the payload
    session_data = json.loads(Path('.synqlikk_session.json').read_text())
    payload['last_sync_time'] = session_data.get('last_sync_time')

    print(f"   Pushing {len(payload['tasks'])} tasks, {len(payload['notes'])} notes, {len(payload['expenses'])} expenses...")

    # --- 2. PUSH TO SERVER & PULL RESPONSE ---
    try:
        response = requests.post(SYNC_ENDPOINT, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status() # Raise an exception for HTTP errors
        server_data = response.json()
        print("   Successfully connected to the server.")
    except Exception as e:
        print(f"❌ Sync failed. Could not connect to the server: {e}")
        conn.close()
        return

    # --- 3. APPLY SERVER CHANGES LOCALLY ---
    items_pulled = 0
    for table in TABLES:
        for item in server_data.get(table, []):
            items_pulled += 1
            item['synced'] = 1 # Mark items from server as already synced
            columns = ', '.join(item.keys())
            placeholders = ', '.join(['?'] * len(item))
            conn.execute(f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})", tuple(item.values()))

    print(f"   Pulled {items_pulled} new/updated items from the server.")

    # --- 4. FINALIZE AND CLEAN UP ---
    for table in TABLES:
        # Mark all successfully pushed items as synced
        conn.execute(f"UPDATE {table} SET synced = 1 WHERE user_id = ? AND synced = 0 AND is_deleted = 0", (user_id,))
        # Hard delete items that were successfully synced as deleted
        conn.execute(f"DELETE FROM {table} WHERE user_id = ? AND synced = 0 AND is_deleted = 1", (user_id,))

    conn.commit()
    conn.close()

    # Save the new server time as our last sync time in the session file
    session_data['last_sync_time'] = server_data.get('server_time')
    Path('.synqlikk_session.json').write_text(json.dumps(session_data))

    if server_data.get('conflicts'):
        print(f"   ⚠️  Resolved {len(server_data['conflicts'])} conflicts (server's version was kept).")

    print("✅ Sync complete!")