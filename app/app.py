from flask import Flask
from flask_httpauth import HTTPTokenAuth
from flask_migrate import upgrade
from .logging import Logging

# # Initialize HTTPTokenAuth
auth = HTTPTokenAuth(scheme='Bearer')


def create_app(config_object="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # configure logging
    Logging()

    # Initialize the app with the videos instance
    from .extension import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.video_routes import video_routes
    app.register_blueprint(video_routes)

    with app.app_context():
        db.create_all()  # To ensure all tables are created
        upgrade()

    return app
