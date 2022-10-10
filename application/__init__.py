from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from celery import Celery

from application.config import Config

cors = CORS()
db = SQLAlchemy()
bcrypt = Bcrypt()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, result_backend=Config.CELERY_RESULT_BACKEND)


def create_app(config_class=Config):

    # Determine route path
    app = Flask(__name__)
    app.config.from_object(Config)  # Get configs
    celery.conf.update(app.config)  # Update celery configs

    from application import models

    cors.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    

    # Manulay push blueprint to app context
    with app.app_context():
        from application.api import api_bp
        app.register_blueprint(api_bp)

    return app