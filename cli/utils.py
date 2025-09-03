# cli/utils.py
import sqlite3
from pathlib import Path
from datetime import datetime
import uuid
from colorama import init, Fore, Style
from db.connection import get_connection as db_connect

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

def get_db_connection(db_path=None):
    """Return DB connection; fallback to default local_cache.db"""
    if db_path is None:
        conn = db_connect()  # uses default local_cache.db
    else:
        conn = db_connect(db_path)
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
