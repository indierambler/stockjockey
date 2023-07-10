"""All basic maintenance functions for interfacing
with the database
"""

from flask import g
from flask_sqlalchemy import SQLAlchemy
from . import db


def get_db():
    """Connect to the backend database and return the db object"""
    if 'db' not in g:
        # TODO: check if database exists
        # TODO: import models for database creation
        # db.create_all()

        # connect with postgres database
        g.db = db

    return g.db


def create_db():
    db.create_all()


def drop_db():
    db.drop_all()
