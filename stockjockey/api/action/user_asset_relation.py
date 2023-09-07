from . import get_db
from . import utcnow
from . import UserAssetRelation
from . import Asset  # import model class
from . import user  # import actions for user table
from . import asset  # import actions for asset table


def get(**kwargs):
    # filters = []
    assert isinstance(kwargs, dict), f'kwargs is type {type(kwargs)}'
    return UserAssetRelation.query.filter_by(**kwargs).all()


def add(user_id, ticker):
    # validate user id
    # validate ticker
    asset_id = asset.get(ticker=ticker)[0].id  # get asset id that matches ticker
    if not conflict_test(**{'user_id': user_id, 'asset_id': asset_id}):
        obj = UserAssetRelation(user_id=user_id, asset_id=asset_id)
        get_db().session.add(obj)
        return obj
    return


def remove(user_id, ticker):
    # validate user id
    # validate ticker
    filters = {'user_id': user_id}
    filters['asset_id'] = asset.get(ticker=ticker)[0].id  # get asset id that matches ticker
    obj = get(**filters)[0]
    get_db().session.delete(obj)
    return obj


def update(search={}, value={}):
    db = get_db()
    obj = db.session.execute(db.update(User).filter_by(search)).values(value)


def conflict_test(**kwargs):
    if get(**kwargs):
        return True
    return False


def get_user_assets(user_id):
    relations = [x.asset_id for x in get(**{'user_id': user_id})]
    return Asset.query.filter(Asset.id.in_(relations)).all()


def get_asset_users(ticker):
    pass
