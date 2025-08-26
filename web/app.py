from flask import Flask
from web.auth import auth_bp
from web.routes import main_bp
from web.sync_api import sync_bp
from web.utils import init_server_db
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)

    # Load configuration (secret key, DB path)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['DB_PATH'] = os.getenv('DB_PATH')

    # Initialize server database if not exists
    init_server_db(app.config['DB_PATH'])

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(sync_bp)

    return app



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)