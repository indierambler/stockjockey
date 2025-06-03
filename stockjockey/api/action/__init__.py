import re

from stockjockey.api.service.util import get_db

# Import table definitions for use in the actions
from ..models import (
    pg_utcnow, utcnow, User, UserInsight, Asset, AssetMetric, UserAssetRelation
)

# Import actions for internal db interaction
from . import user
from . import user_insight
from . import asset
from . import user_asset_relation


# Function to commit actions to db
def commit():
    get_db().session.commit()


def clean_tag_text(tag):
    """Manually scrub html tags and unwanted text patterns from a BS4 tag object"""
    result = re.sub('<[^>]+>', '\n', str(tag))
    if any([x in result for x in ['Show more\n', 'Show less\n']]):
        result = result.replace('Show more\n', '').replace('Show less\n', '')

    while any([x in result for x in ['\n\n', '  ', '\n \n', ' \n ']]):
        result = (result
            .replace('\n\n', '\n')
            .replace('  ', ' ')
            .replace('\n \n', '\n')
            .replace(' \n ', '\n'))
    return result

class BaseCRUD:
    """Object to handle basic CRUD operations on a Postgres database
    - created, updated, and deleted times are handled in the model
    """
    def __init__(self, model):
        self.model = model
        self.db = get_db()

    def create(self, **kwargs):
        try:
            instance = self.model(**kwargs)
            self.db.session.add(instance)
            self.db.session.commit()
            return instance
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Create error: {e}")
            return None

    def get_by_id(self, record_id):
        return self.model.query.get(record_id)
    
    def get_by_filter(self, *args, **kwargs):
        return self.model.query.filter_by(*args, **kwargs).all()

    def get_all(self):
        return self.model.query.all()

    def update(self, record_id, **kwargs):
        instance = self.model.query.get(record_id)
        if not instance:
            return None
        try:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.session.commit()
            return instance
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Update error: {e}")
            return None

    def delete(self, record_id):
        instance = self.model.query.get(record_id)
        if not instance:
            return False
        try:
            self.db.session.delete(instance)
            self.db.session.commit()
            return True
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Delete error: {e}")
            return False
    