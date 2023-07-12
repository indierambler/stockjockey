"""Service package of the API contains modules that define application logic
or interact with other services or the db layer.
- routes should delegate all logic to the services.
"""

from .hash import Password, PasswordHash, HasPassword
from .util import get_db, update_db_command, reset_db_command, register_commands