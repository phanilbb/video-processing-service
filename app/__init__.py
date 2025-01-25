from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth

db = SQLAlchemy()
auth = HTTPTokenAuth(scheme='Bearer')

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)

    from .routes import api
    app.register_blueprint(api)

    return app
