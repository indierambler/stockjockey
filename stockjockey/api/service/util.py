"""All basic maintenance functions for interfacing
with the database
"""

import click
from flask import g
from flask_sqlalchemy import SQLAlchemy
from .. import db


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


@click.command('update-db')
def update_db_command():
    """Update or create tables that have been changed"""
    create_db()
    click.echo('Database updated.')


@click.command('reset-db')
def reset_db_command():
    """Drop the existing database and then rebuild it"""
    drop_db()
    create_db()
    click.echo('Database created.')


def register_commands(app):
    """Register db functions with the application instance"""
    # app.teardown_appcontext(close_db)  # set any funcs to be run on app teardown
    app.cli.add_command(update_db_command)
    app.cli.add_command(reset_db_command)
