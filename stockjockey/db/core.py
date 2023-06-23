# Import dependencies
import os
import sqlite3
import click
from flask import current_app, g
from psycopg2 import connect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


def get_db():
    """ Connect to the backend database and return the db object """
    if 'db' not in g:
        # connect with sqlite database
        # g.db = sqlite3.connect(
        #    current_app.config['DATABASE'],
        #    detect_types=sqlite3.PARSE_DECLTYPES
        # )
        # g.db.row_factory = sqlite3.Row

        # connect with postgres database
        g.db = connect(
            host=os.getenv("SQL_HOST"),
            port=os.getenv("SQL_PORT"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    # TODO: connect to database server/container
    # TODO: create database if not exist
    # attach database object
    db = get_db()

    # build base schema in database (sqlite)
    # with current_app.open_resource('schema.sql') as f:
    #    db.executescript(f.read().decode('utf8'))

    # build base schema in database (postgres)
    with current_app.open_resource('schema.sql') as f:
        with db.cursor() as cursor:
            cursor.execute(f.read().decode('utf8'))
            # cursor.executescript(open("schema.sql", "r").read())

    db.commit()  # write all changes to db
    db.close()  # leaving context does not close the connection (undecided if it should close or not)


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register db functions with the application instance"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
