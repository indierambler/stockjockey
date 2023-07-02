"""Package container for interactions with the internal database
- uses sqlite3 database (future migration to postgres for stronger definition)
"""
# Import dependencies
from .core import *
from .sqlite import *


db = SQLAlchemy()