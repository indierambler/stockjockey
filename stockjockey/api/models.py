import uuid
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date
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
    - inherits a password column attribute (password)
    - inherits a password validation method (_validate_password(key, password))
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
    user_asset_relation = relationship('UserAssetRelation')
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
    user_asset_relation = relationship('UserAssetRelation')
    asset_metric = relationship('AssetMetric')
    asset_meta = relationship('AssetMeta')

    def __repr__(self):
        return '<Asset %r>' % self.ticker


class AssetMetric(db.Model):
    """asset_metric table definition
    """
    asset_id = db.Column(UUID(as_uuid=True), ForeignKey('asset.id'), primary_key=True)
    metric = db.Column(db.String(20), nullable=False)
    year = db.Column(Integer, nullable=False)
    quarter = db.Column(Integer)
    value = db.Column(Float, nullable=False)
    created = db.Column(DateTime, server_default=utcnow())
    updated = db.Column(DateTime, onupdate=utcnow())
    deleted = db.Column(DateTime)

    def __repr__(self):
        return f'Asset Metric (Asset:{self.asset_id}, Metric:{self.metric}, Year:{self.year}, Value:{self.value})'


class AssetMeta(db.Model):
    """asset_meta table definition
    """
    asset_id = db.Column(UUID(as_uuid=True), ForeignKey('asset.id'), primary_key=True)
    exchange = db.Column(db.String(20), nullable=False)
    sector = db.Column(db.String(80), nullable=False)
    created = db.Column(DateTime, server_default=utcnow())
    updated = db.Column(DateTime, onupdate=utcnow())
    deleted = db.Column(DateTime)

    def __repr__(self):
        return f'Asset Meta (Asset:{self.asset_id})'


class UserAssetRelation(db.Model):
    """user_asset_relation table definition
    - TODO: make combination of user and asset ids unique
    - TODO: add a relation id column?
    """
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey('user.id'))
    asset_id = db.Column(UUID(as_uuid=True), ForeignKey('asset.id'))
    created = db.Column(DateTime, server_default=utcnow())
    updated = db.Column(DateTime, onupdate=utcnow())
    deleted = db.Column(DateTime)

    def __repr__(self):
        return f'User Asset Relation (User:{self.user_id}, Asset:{self.asset_id})'
