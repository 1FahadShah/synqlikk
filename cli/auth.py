# cli/auth.py
import requests
import json
from pathlib import Path
from colorama import init, Fore, Style
from cli.constants import LOGIN_ENDPOINT, REGISTER_ENDPOINT, LOCAL_DB_PATH
from cli.exceptions import APIError, AuthenticationError

init(autoreset=True)

SESSION_FILE = Path('.synqlikk_session.json')

def save_session(token: str, user_id: str):
    """Save session token locally."""
    SESSION_FILE.write_text(json.dumps({"token": token, "user_id": user_id}))

def load_session():
    """Load session token if exists."""
    if SESSION_FILE.exists():
        data = json.loads(SESSION_FILE.read_text())
        return data.get('token'), data.get('user_id')
    return None, None

def clear_session():
    """Remove saved session."""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()

def register(username: str, password: str):
    """Register a new user via server API."""
    try:
        resp = requests.post(REGISTER_ENDPOINT, json={"username": username, "password": password}, timeout=10)
        if resp.status_code == 201:
            data = resp.json()
            save_session(data['token'], data['user_id'])
            print(Fore.GREEN + "✅ Registration successful!")
        else:
            raise AuthenticationError(resp.json().get("error", "Registration failed"))
    except requests.RequestException as e:
        raise APIError(f"Network error: {e}")

def login(username: str, password: str):
    """Login existing user via server API."""
    try:
        resp = requests.post(LOGIN_ENDPOINT, json={"username": username, "password": password}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            save_session(data['token'], data['user_id'])
            print(Fore.GREEN + "✅ Login successful!")
        else:
            raise AuthenticationError(resp.json().get("error", "Login failed"))
    except requests.RequestException as e:
        raise APIError(f"Network error: {e}")

def is_authenticated():
    """Check if user is logged in."""
    token, user_id = load_session()
    return token is not None

def get_auth_headers():
    """Return headers for authenticated API requests."""
    token, _ = load_session()
    if not token:
        raise AuthenticationError("No active session. Please login first.")
    return {"Authorization": f"Bearer {token}"}
