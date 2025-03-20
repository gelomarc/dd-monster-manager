from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from app.web import web as web_blueprint
    app.register_blueprint(web_blueprint)

    # Setup login manager
    from app.models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    login_manager.login_view = 'web.login'
    login_manager.login_message_category = 'info'

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

    return app 