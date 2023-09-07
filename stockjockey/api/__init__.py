"""Package container for interactions with the internal database
- uses sqlite3 database (future migration to postgres for stronger definition)
"""
# Import dependencies
from flask_sqlalchemy import SQLAlchemy

from .core import get_db, query_db, init_db, init_app, init_db_command


db = SQLAlchemy()


from . import models
from . import route
from . import schema
from . import service
from . import action
