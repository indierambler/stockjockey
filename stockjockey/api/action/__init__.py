# Import get_db from utilities for global use
from ..service.util import get_db

# Import table definitions for use in the actions
from ..models import (
    utcnow, User, UserInsight, Asset, AssetMeta, AssetMetric, UserAssetRelation
)

# Import actions for internal db interaction
from . import user
from . import user_insight
from . import asset
from . import user_asset_relation


# Function to commit actions to db
def commit():
    get_db().session.commit()
    