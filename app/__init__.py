from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        # Load the instance config when not testing
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'ddmonsters.sqlite'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Add custom Jinja2 filters
    @app.template_filter('nl2br')
    def nl2br(s):
        return s.replace('\n', '<br>') if s else ''
    
    with app.app_context():
        # Import models
        from app.models import user, campaign, player, npc, event, encounter, monster, loot
        
        # Create database tables
        db.create_all()
        
        # Register blueprints
        from app.routes import auth, campaigns, players, npcs, events, encounters, monsters, loot
        app.register_blueprint(auth.bp)
        app.register_blueprint(campaigns.bp)
        app.register_blueprint(players.bp)
        app.register_blueprint(npcs.bp)
        app.register_blueprint(events.bp)
        app.register_blueprint(encounters.bp)
        app.register_blueprint(monsters.bp)
        app.register_blueprint(loot.bp)
        
        # Set the root route
        from app.routes.campaigns import index
        app.add_url_rule('/', endpoint='index')
        
        return app 