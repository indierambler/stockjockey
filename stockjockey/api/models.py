import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import UUID
from . import db
from .service import HasPassword


class utcnow(expression.FunctionElement):
    """Extension column data type for UTC timestamp"""
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    """Get UTC timestamp processed on Postgres server"""
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class User(HasPassword, db.Model):
    """user table definition
    - inherits a password column attribute
    - inherits a password validation method
    """
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # permission = db.Column()
    # flagged = db.Column()
    # created = db.Column(DateTime(timezone=True), server_default=func.now())
    # updated = db.Column(DateTime(timezone=True), onupdate=func.now())
    # deleted = db.Column()
    created = db.Column(DateTime, server_default=utcnow())
    updated = db.Column(DateTime, onupdate=utcnow())
    deleted = db.Column(DateTime)
    user_insight = relationship('UserInsight')

    def __repr__(self):
        return '<User %r>' % self.username


class UserInsight(db.Model):
    """user_insight table definition
    """
    user_id = db.Column(UUID(as_uuid=True), ForeignKey('user.id'), primary_key=True)
    # session_count = db.Column(db.Integer)
    # asset_query_count = db.Column(db.Integer)
    # created = db.Column(DateTime(timezone=True), server_default=func.now())
    # updated = db.Column(DateTime(timezone=True), onupdate=func.now())
    # deleted = db.Column()
    created = db.Column(DateTime, server_default=utcnow())
    updated = db.Column(DateTime, onupdate=utcnow())
    deleted = db.Column(DateTime)

    def __repr__(self):
        return '<User %r>' % self.user_id


class Asset(db.Model):
    """asset table definition
    """
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80))
    ticker = db.Column(db.String(20), unique=True, nullable=False)
    # created = db.Column(DateTime(timezone=True), server_default=func.now())
    # updated = db.Column(DateTime(timezone=True), onupdate=func.now())
    # deleted = db.Column()
    created = db.Column(DateTime, server_default=utcnow())
    updated = db.Column(DateTime, onupdate=utcnow())
    deleted = db.Column(DateTime)

    def __repr__(self):
        return '<Asset %r>' % self.ticker
