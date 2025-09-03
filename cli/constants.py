# cli/constants.py
from pathlib import Path

# ==========================
# Paths
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / 'db'
LOCAL_DB_PATH = DB_DIR / 'local_cache.db'

# ==========================
# Server API
# ==========================
SERVER_API_URL = 'http://127.0.0.1:5000/api'
LOGIN_ENDPOINT = f'{SERVER_API_URL}/login'
REGISTER_ENDPOINT = f'{SERVER_API_URL}/register'
SYNC_ENDPOINT = f'{SERVER_API_URL}/sync'

# ==========================
# Defaults
# ==========================
DEFAULT_TIMEOUT = 10  # seconds for API calls
RETRY_ATTEMPTS = 3
