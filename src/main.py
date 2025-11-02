import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, redirect, url_for
from flask_login import LoginManager

from dependencies.app_config import load_config, get_config
from dependencies.database import init_db
from routers import auth_bp, admin_bp, audio_bp
from services.auth_service import AuthService


def create_app():
    """Application factory function"""
    app = Flask(__name__, template_folder='templates')

    # Load configuration
    load_config()
    config = get_config()

    # Configure Flask app
    app.config['SECRET_KEY'] = config.get('app.secret_key')
    app.config['DEBUG'] = config.get('app.debug', False)

    # Initialize database
    init_db(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return AuthService.get_user_by_id(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(audio_bp)

    # Root route - redirect to login or audio files
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app


if __name__ == '__main__':
    app = create_app()
    config = get_config()

    host = config.get('app.host', '0.0.0.0')
    port = config.get('app.port', 5000)
    debug = config.get('app.debug', False)

    print(f"Starting Flask application on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
