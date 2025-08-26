import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "local_cache.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def init_local_db():
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    print(f"[LOCAL DB] Initialized at: {DB_PATH}")

if __name__ = "__main__":
    init_local_db()