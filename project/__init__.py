from flask import Flask
from flask_migrate import Migrate, upgrade
from dotenv import load_dotenv

from .extensions import db
from .views import main
from .utils import make_celery
import os


def create_app():
    app = Flask(__name__)

    # Load configuration from .env file
    load_dotenv()

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["CELERY_CONFIG"] = {
        "broker_url": os.getenv("CELERY_BROKER_URL"),
        "result_backend": os.getenv("CELERY_RESULT_BACKEND"),
    }

    with app.app_context():
        db.init_app(app)
        migrate = Migrate(app, db)
        migrate.init_app(app, db)

    celery = make_celery(app)
    celery.set_default()

    app.register_blueprint(main)

    return app, celery
