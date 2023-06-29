# Import dependencies
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# App Factory
def create_app(test_config=None):
    # create the app
    app = Flask(__name__, instance_relative_config=True)

    # load default and public config corresponding to current deployment env
    if os.getenv('DEPLOYMENT'):
        config_str = f"config.Config{os.getenv('DEPLOYMENT').capitalize()}"
    else:
        config_str = "config.Config"
    app.config.from_object(config_str)

    # load private config values from env
    # app.config.from_envvar('PRIVATE_CONFIG', default='')

    # register CLI functions with app
    from . import db
    db.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass  # add an error or warning here

    # Register blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from .main import main_bp
    app.register_blueprint(main_bp)
    app.add_url_rule('/', endpoint='dashboard')  # forward root page to dashboard

    # create db
    db = SQLAlchemy(app)
    # db.init_app(app)
    with app.app_context():
        db.create_all()

    return app
