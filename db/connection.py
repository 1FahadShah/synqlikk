import sqlite3
from pathlib import Path

def get_connection(db_name="local_cache.db"):
    db_path = Path(__file__).resolve().parent / db_name
    connect = sqlite3.connect(db_path)
    connect.row_factory = sqlite3.Row
    return connect