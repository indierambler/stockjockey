# Import dependencies
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


### App Factory ###
def create_app(test_config=None):
    ## Create the App ##
    app = Flask(__name__, instance_relative_config=True)

    ## Configure the App ##
    # load default and public config corresponding to current deployment env
    if os.getenv('DEPLOYMENT'):
        config_str = f"config.Config{os.getenv('DEPLOYMENT').capitalize()}"
    else:
        config_str = "config.Config"
    app.config.from_object(config_str)
    # load private config values from env
    # app.config.from_envvar('PRIVATE_CONFIG', default='')

    ## Register CLI Functions With App ##
    from . import api
    api.init_app(app)

    ## Ensure Instance Folder Exists ## (possibly remove?)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass  # add an error or warning here

    ## Register Blueprints ##
    register_blueprints(app)

    ## Create or Initialize DB ## (possibly remove to support lazy connection?)
    from stockjockey.api import db
    db.init_app(app)

    return app


### Helper Functions ###
def register_blueprints(app):
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .main import main_bp
    app.register_blueprint(main_bp)
    app.add_url_rule('/', endpoint='dashboard')  # forward root page to dashboard
    

def initialize_extensions(app):
    pass


def register_error_handlers(app):
    pass


def configure_logging(app):
    pass
