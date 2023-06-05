# Import dependencies
import os
from flask import Flask


# App Factory
def create_app(test_config=None):
    # create the app
    app = Flask(__name__, instance_relative_config=True)

    # load the configuration corresponding to the current deployment env
    deployment = os.getenv("DEPLOYMENT")
    if deployment == "prod":
        app.config.from_object("config.ConfigProd")
    elif deployment == "stg":
        app.config.from_object("config.ConfigStg")
    elif deployment == "dev":
        app.config.from_object("config.ConfigDev")

    # load any additional config values
    # app.config.from_mapping(
    #     DATABASE=os.path.join(app.instance_path, 'stockjockey.sqlite'),
    # )

    # Register app functions
    from . import db
    # db.init_app(app)  # check if db exists, if not create it

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass  # add an error or warning here

    # Register blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import main
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='dashboard')  # forward root page to dashboard

    return app
