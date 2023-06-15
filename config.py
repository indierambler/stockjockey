# Flask configuration for production environment
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """class for general flask configuration settings
    PARAMS
    ------
    object: class self definition
    db_type (str: 'postgres' | 'sqlite'): selection of which db to use on backend
    """
    # DEBUG = False  # set this in server launch command
    SECRET_KEY = 'dev'
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/project/media"
    SESSION_COOKIE_NAME = 'session'


class ConfigProd(Config):
    # DEBUG = False  # set this in server launch command
    TESTING = False


class ConfigStg(Config):
    # DEBUG = False  # set this in server launch command
    TESTING = True


class ConfigDev(Config):
    # DEBUG = True  # set this in server launch command
    TESTING = True
