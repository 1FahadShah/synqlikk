# cli/sync.py
import requests
from cli.constants import SYNC_ENDPOINT, DEFAULT_TIMEOUT
from cli.auth import get_auth_headers
from cli.utils import get_db_connection, current_timestamp
from cli.exceptions import SyncConflictError

TABLES = ["tasks", "notes", "expenses"]

def push_local_changes():
    """Push unsynced local changes to the server, including deletions."""
    conn = get_db_connection()
    cur = conn.cursor()
    payload = {}

    for table in TABLES:
        cur.execute(f"SELECT * FROM {table} WHERE synced=0")
        rows = cur.fetchall()
        if rows:
            payload[table] = [dict(row) for row in rows]

    if not payload:
        print("✅ No local changes to sync.")
        return

    try:
        resp = requests.post(SYNC_ENDPOINT, json=payload, headers=get_auth_headers(), timeout=DEFAULT_TIMEOUT)
        if resp.status_code == 200:
            ts = current_timestamp()
            # Mark all pushed rows as synced
            for table in TABLES:
                cur.execute(f"UPDATE {table} SET synced=1 WHERE synced=0")
            conn.commit()
            print("✅ Local changes synced to server.")
        else:
            print(f"❌ Server rejected changes: {resp.status_code} {resp.text}")
    except requests.RequestException as e:
        print(f"❌ Network error during sync: {e}")
    finally:
        conn.close()


def pull_server_changes():
    """Pull latest changes from server and merge locally, including deletions."""
    try:
        resp = requests.get(SYNC_ENDPOINT, headers=get_auth_headers(), timeout=DEFAULT_TIMEOUT)
        if resp.status_code != 200:
            print(f"❌ Failed to fetch server changes: {resp.status_code}")
            return

        data = resp.json()
        conn = get_db_connection()
        cur = conn.cursor()

        for table in TABLES:
            items = data.get(table, [])
            for item in items:
                cur.execute(f"SELECT last_modified FROM {table} WHERE id=?", (item['id'],))
                row = cur.fetchone()

                if row:
                    # Conflict: last-write-wins
                    if row['last_modified'] < item['last_modified']:
                        columns = ", ".join(f"{k}=?" for k in item if k != "id")
                        values = [item[k] for k in item if k != "id"] + [item['id']]
                        cur.execute(f"UPDATE {table} SET {columns} WHERE id=?", values)
                else:
                    # New item from server → insert locally
                    columns = ", ".join(item.keys())
                    placeholders = ", ".join("?" for _ in item)
                    cur.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(item.values()))

        conn.commit()
        print("✅ Pulled latest changes from server.")
    except requests.RequestException as e:
        print(f"❌ Network error during pull: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def sync_all():
    """Full sync: push local changes (including deletions), then pull server updates."""
    print("🔄 Starting sync...")
    push_local_changes()
    pull_server_changes()
    print("✅ Sync complete.")
