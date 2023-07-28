from . import get_db
from . import utcnow
from . import User


def get(*args, **kwargs):
    return User.query.filter_by(*args, **kwargs).first()


def add(email, username, password):
    obj = User(email=email, username=username, password=password)
    db = get_db()
    db.session.add(obj)
    return obj


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
