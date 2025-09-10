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
SCHEMA_PATH = Path(__file__).resolve().parent.parent / 'db' / 'schema.sql'

# Flag to ensure initialization happens only once
LOCAL_DB_INITIALIZED = False

def initialize_local_db():
    """
    Initialize the local DB only once per session.
    """
    global LOCAL_DB_INITIALIZED
    if LOCAL_DB_INITIALIZED:
        return  # Already initialized, skip

    try:
        if not LOCAL_DB_PATH.exists():
            print_info(f"🆕 Creating new local DB at {LOCAL_DB_PATH}...")
        else:
            print_info(f"🔄 Ensuring local DB schema exists at {LOCAL_DB_PATH}...")

        conn = sqlite3.connect(LOCAL_DB_PATH)
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            conn.executescript(schema_sql)
        conn.commit()
        conn.close()

        print_success("✅ Local DB initialized successfully.")
        LOCAL_DB_INITIALIZED = True
    except Exception as e:
        print_error(f"❌ Failed to initialize local DB: {e}")
        raise

def get_db_connection(db_path=None):
    """
    Return a SQLite connection to local_cache.db.
    Ensures schema exists, but silently if already initialized.
    """
    initialize_local_db()  # prints only once
    if db_path is None:
        conn = db_connect()  # default local_cache.db
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
