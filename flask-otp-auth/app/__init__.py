from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import config
import os

from flask import Flask
from flask_cors import CORS
from app.config import config
from app.extensions import db, migrate, limiter
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    limiter.init_app(app)
    
    # Register Blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'flask-otp-auth'}, 200
        
    return app
