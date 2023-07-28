from . import get_db
from . import utcnow
from . import Asset


def get(*args, **kwargs):
    return Asset.query.filter_by(*args, **kwargs).all()


def add(ticker):
    # check if ticker refers to a real-life asset?
    # conflict should potentially be handled using try except
    if not conflict_test(ticker=ticker):
        obj = Asset(ticker=ticker)
        get_db().session.add(obj)
        return obj
    return get(ticker=ticker)[0]


def remove(email=None, username=None):
    db = get_db()
    if email:
        obj = db.session.execute(db.select(User).filter_by(email=email)).scalar_one()
    elif username:
        obj = db.session.execute(db.select(User).filter_by(username=username).scalar_one())
        # User.update().where(User.email.data == email).values(deleted=utcnow())
    obj.deleted = utcnow()
    return obj


def update(search={}, value={}):
    db = get_db()
    obj = db.session.execute(db.update(User).filter_by(search)).values(value)


def conflict_test(*args, **kwargs):
    if get(*args, **kwargs):
        return True
    return False
