import sqlite3
from pathlib import Path
from datetime import datetime

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "db" / "schema.sql"


# Initialize the server database
def init_server_db(db_path: str):
    db_file = Path(db_path)
    if not db_file.exists():
        with sqlite3.connect(db_file) as connect:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                connect.executescript(f.read())
        print(f"[SERVER DB] Initialized at: {db_file}")
    else:
        print(f"[SERVER DB] Already exists at: {db_file}")

def get_db_connection(db_path: str):
    connect = sqlite3.connect(db_path)
    connect.row_factory = sqlite3.Row
    return connect


def current_timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
