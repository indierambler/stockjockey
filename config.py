# Flask configuration for production environment
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """class for general flask configuration settings
    """
    SECRET_KEY = 'dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/project/static"
    MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/project/media"
    SESSION_COOKIE_NAME = 'session'

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """create the database connection url
        url syntax: postgresql://user:password@container:port/dbname
        """
        with open(os.getenv("POSTGRES_USER_FILE"), 'r') as file:
            user = file.read().replace('\n', '')
        with open(os.getenv("POSTGRES_PASSWORD_FILE"), 'r') as file:
            password = file.read().replace('\n', '')
        container = os.getenv("DB_CONTAINER")
        port = os.getenv("DB_PORT")
        dbname = os.getenv("POSTGRES_DB")
        return f'postgresql://{user}:{password}@{container}:{port}/{dbname}'


class ConfigProd(Config):
    DEBUG = False  # set this in server launch command
    TESTING = False


class ConfigStg(Config):
    DEBUG = False  # set this in server launch command
    TESTING = True


class ConfigDev(Config):
    DEBUG = True  # set this in server launch command
    TESTING = True
