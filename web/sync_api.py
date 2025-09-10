# web/sync_api.py
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from . import models
import jwt
import datetime
from .utils import current_timestamp


sync_bp = Blueprint("sync_bp", __name__, url_prefix="/api")

# --- API Authentication Routes ---
@sync_bp.route("/register", methods=["POST"])
def api_register():
    data = request.json
    db_path = current_app.config["DB_PATH"]
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    if models.get_user_by_username(db_path, username):
        return jsonify({"error": "Username already exists."}), 409

    user_id = models.create_user(db_path, username, password)

    # Generate token immediately using app's secret key
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "message": "User created successfully",
        "user_id": user_id,
        "token": token
    }), 201


@sync_bp.route("/login", methods=["POST"])
def api_login():
    data = request.json
    db_path = current_app.config["DB_PATH"]
    user = models.get_user_by_username(db_path, data.get('username'))

    if not user or not models.check_password_hash(user["password_hash"], data.get('password')):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"token": token, "user_id": user['id']})


# --- Token-based Authentication Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({"error": "Unauthorized: Token is missing"}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            return f(user_id=data['user_id'], *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Unauthorized: Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized: Token is invalid"}), 401

    return decorated


# --- Main Sync Endpoint ---
@sync_bp.route('/sync', methods=['POST'])
@token_required
def sync_data(user_id):
    """Handles the main two-way sync transaction."""
    client_data = request.get_json()
    db_path = current_app.config['DB_PATH']
    client_last_sync = client_data.get('last_sync_time')

    response_payload = {"tasks": [], "notes": [], "expenses": [], "conflicts": []}

    # Phase 1: Process items pushed FROM the client
    for item_type in ["tasks", "notes", "expenses"]:
        for client_item in client_data.get(item_type, []):
            client_item['user_id'] = user_id
            server_item = models.get_item_by_id(db_path, item_type, client_item['id'])
            if server_item is None or client_item['last_modified'] > server_item['last_modified']:
                models.create_or_update_item(db_path, item_type, client_item)
            else:
                response_payload['conflicts'].append(dict(server_item))

    # Phase 2: Pull items FROM the server to the client
    if client_last_sync:
        for item_type in ["tasks", "notes", "expenses"]:
            server_changes = models.get_items_since(db_path, item_type, user_id, client_last_sync)
            response_payload[item_type].extend([dict(item) for item in server_changes])

    response_payload['server_time'] = current_timestamp()
    return jsonify(response_payload)
