# Import table definitions for use in the actions
from ..service.util import get_db
from ..models import (
    utcnow, User, UserInsight, Asset
)

# Import actions for internal db interaction
from . import user
from . import user_insight
from . import asset


# Function to commit actions to db
def commit():
    get_db().session.commit()
    