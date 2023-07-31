# Import dependencies
import os
import sqlite3
import click
from flask import current_app, g
from psycopg2 import connect
import psycopg2.extras
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


def get_db():
    """ Connect to the backend database and return the db object """
    if 'db' not in g:
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
        # db.close()
        pass


def query_db(sql=None):
    db = get_db()
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(sql)
        try:
            results = cursor.fetchall()
        except psycopg2.ProgrammingError:
            results = None

    db.commit()
    # db.close()
    return results


def init_db():
    # TODO: connect to database server/container
    # TODO: create database if not exist

    # build base schema in database (postgres)
    with current_app.open_resource('schema.sql') as f:
        query_db(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register db functions with the application instance"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
