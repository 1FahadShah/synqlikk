from flask import Blueprint

# A Blueprint for the JSON API endpoints that the CLI will use
sync_bp = Blueprint('sync_bp', __name__)

# We will add API routes like @sync_bp.route('/tasks') here later.