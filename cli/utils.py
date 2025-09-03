# cli/utils.py
import sqlite3
from pathlib import Path
from datetime import datetime
import uuid
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# ==========================
# Color printing helpers
# ==========================
def print_success(msg):
    print(Fore.GREEN + msg)

def print_info(msg):
    print(Fore.CYAN + msg)

def print_warning(msg):
    print(Fore.YELLOW + msg)

def print_error(msg):
    print(Fore.RED + msg)

# ==========================
# Database helpers
# ==========================
LOCAL_DB_PATH = Path(__file__).resolve().parent.parent / 'db' / 'local_cache.db'

def get_db_connection(db_path=LOCAL_DB_PATH):
    """Return a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ==========================
# Utility helpers
# ==========================
def current_timestamp():
    """Return current UTC timestamp in ISO format."""
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def generate_uuid():
    """Return a new UUID string."""
    return str(uuid.uuid4())
