# Import dependencies
import sqlite3
import click
from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


def get_db():
    # for sqlite3 db
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    # for postgres db

    return g.db


def close_db(e=None):
    # for sqlite3 db
    db = g.pop('db', None)

    if db is not None:
        db.close()

# for postgres db


def init_db():
    # for sqlite3 db
    # db = get_db()

    # with current_app.open_resource('schema.sql') as f:
    #     db.executescript(f.read().decode('utf8'))

    # for postgres db
    SQLAlchemy.init_app
    db = SQLAlchemy(current_app)
    return db


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register db functions with the application instance"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
