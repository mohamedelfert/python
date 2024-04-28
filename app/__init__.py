from flask import Flask
from config import Config
from app.extensions import db
import os
from flask_jwt_extended import JWTManager
from datetime import timedelta


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(weeks=48)
    JWTManager(app)

    # Register blueprints here
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')

    return app
