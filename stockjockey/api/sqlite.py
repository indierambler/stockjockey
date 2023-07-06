""""""

# Import dependencies
import os
import sqlite3
import logging
import datetime
from flask import current_app, g


class DbInterface:
    """general object for handling communication with the db"""
    def __init__(self, file=None):
        if file:
            self.dbfile = file
        else:
            self.dbfile = current_app.config['DATABASE']

        self.open()

        # initialize error logging (TODO: replace error prints with logging)
        # self.logger = logger or logging.getLogger(__name__)
        # self.logger.debug('Running __init__')

    def open(self):
        # check that the db file exist and works
        try:
            assert os.path.isfile(self.dbfile)
            # init db object
            if 'db' not in g:
                g.db = sqlite3.connect(
                    self.dbfile,
                    detect_types=sqlite3.PARSE_DECLTYPES
                )
                g.db.row_factory = sqlite3.Row
            self.conn = g.db
        except sqlite3.Error as e:
            print(e)  # TODO: change to logged error
            return -1
        except AssertionError:
            print('ERROR: database file not found.')  # TODO: change to logged error
            return -1
        return 0

    def close(self):
        if hasattr(self, 'conn'):
            self.conn.close()
            return 0
        return -1

    def write(self, query, *args):
        try:
            assert any(map(lambda s: query.upper().strip().startswith(s), ('CREATE TABLE', 'ALTER TABLE', 'DROP TABLE', 'INSERT', 'UPDATE', 'DELETE')))
            assert query.count('?') == len(args)
            c = self.conn.cursor()
            c.execute(query, args)
            self.conn.commit()
            return 0
        except AssertionError:
            print('ERROR: inconsistent query arguments.')
        except sqlite3.Error as e:
            self.conn.rollback()
            print('SQL ERROR:', e)
        return -1

    def read(self, query, *args):
        try:
            assert query.count('?') == len(args)
            assert query.upper().strip().startswith('SELECT')
            c = self.conn.cursor()
            c.execute(query, args)
            rows = c.fetchall()
            return 0, rows
        except AssertionError:
            print('ERROR: inconsistent query arguments.')
        except sqlite3.Error as e:
            print('SQL ERROR:', e)
        return -1, ()


class Asset:
    """object for info on a single stock"""
    def __init__(self):
        pass

    def get(self, ticker):
        pass

    def get_all(self, username):
        pass

    def create(self):
        pass


class User:
    """Current user object"""
    def __init__(self, db, username):
        self.db = db
        self.username = username
        self.get()

    def get(self):
        """search and populate current user from db"""
        cols = ['id', 'username', 'password', 'email', 'created', 'updated', 'deleted']
        query = (f"SELECT {','.join(cols)} FROM user WHERE username = ?;")
        vals = (self.username)
        status, result = self.db.read(query, vals)
        if status < 0:
            return 'Failed to retrieve user'  # TODO: use logging and error
        if result:
            result = dict(result[0])
            for key, val in result.items():
                setattr(self, key, val)
        else:
            for col in cols:
                setattr(self, col, None)
            # TODO: user not found error?

    def create(self, username, password):
        """add a new user to the db"""
        pass

    def update(self, username, password):
        """change data for a user in the db"""
        pass

    def remove(self, username, password):
        """remove a user from the db"""
        pass

    def switch(self, username, password):
        """change the current user"""
        pass

    def get_assets(self):
        """get all assets for this user"""

    def relate_asset(self, ticker):
        """create a relation to an asset for this user"""
        pass

    def unrelate_asset(self, ticker):
        """remove a relation to an asset for this user"""


class StockJockey:
    """Class for stockjockey-specific interactions with its db"""
    def __init__(self, file=None):
        self.interface = DbInterface(file)
        self.calls = 0

    def update_resource(self, api, counts=0, limit=None):
        """Update the api call counter table in the database to keep a daily running total"""
        # request the api entry from the resource table (not found returns empty string)
        query = ("SELECT * FROM resource WHERE name = ?;")
        vals = (api)
        status, result = self.interface.read(query, vals)
        if status < 0:
            return 'E1'

        now = datetime.datetime.now()
        cols = ['id', 'name', 'count', 'maximum', 'created', 'updated', 'deleted']
        if result:  # if api entry found, turn result into resource dict
            resource = dict(zip(cols, result[0]))
            if limit is not None and int(limit) != resource['maximum']:  # update limit if needed (0 sets lim to unlimited)
                query = ("UPDATE resource SET maximum = ? WHERE name = ?;")
                vals = (limit, api)
                status = self.interface.write(query, *vals)
                if status < 0:
                    return 'E2'
                resource['maximum'] = limit

            updated = datetime.datetime.strptime(resource['updated'], '%Y-%m-%d %H:%M:%S.%f')
            if updated.date() == now.date():  # if updated is today then update count
                query = ("UPDATE resource SET count = count + ?, updated = ? WHERE name = ?;")
                vals = (counts, now, api)
                status = self.interface.write(query, *vals)
                if status < 0:
                    return 'E3'
                resource['count'] += counts
                resource['updated'] = now
            else:  # if updated is not today then reset count
                query = ("UPDATE resource SET count = ?, updated = ? WHERE name = ?;")
                vals = (counts, now, api)
                status = self.interface.write(query, *vals)
                if status < 0:
                    return 'E4'
                resource['count'] = counts
                resource['updated'] = now

        else:  # if api entry not found, insert a new one
            result = [api, counts, limit, now, now]
            resource = dict(zip(cols[1:-2], result))
            query = ("INSERT INTO resource(name, count, maximum, created, updated) "
                     "VALUES(?, ?, ?, ?, ?);")
            vals = tuple(result[1:-2])
            status = self.interface.write(query, *vals)
            if status < 0:
                return 'E5'

        return resource

    # def get_n12(self, ticker, period=datetime.datetime.now()):


def test(path):
    """Test function for DB checking
    - needs to be updated for the actual DB
    - should be moved to a separate test directory
    """
    db = DbInterface(path)  # where is Interface from?
    res = db.open()
    q = """
        CREATE TABLE IF NOT EXISTS example(
        id integer PRIMARY KEY,
        sometext text NOT NULL
        );
    """
    res = db.write(q)
    q = 'INSERT INTO example(sometext) VALUES(?);'
    res = db.write(q, 'a')
    q = 'INSERT INTO example(sometext) VALUES(?, ?);'
    res = db.write(q, 'b')
    q = 'INSERT INTO example(sometext) VALUES(?);'
    res = db.write(q)
    q = 'INSERT INTO example(sometext) VALUES(?, ?);'
    res = db.write(q, 'c', 'd')
    q = 'SELECT * FROM example;'
    res, data = db.read(q)
    q = 'SELECT somevalue FROM example;'
    res, data = db.read(q)
    q = 'SELECT * FROM example WHERE sometext = ?;'
    res, data = db.read(q, 'a')
    q = 'SELECT * FROM example WHERE sometext = ?;'
    res, data = db.read(q)
    res = db.close()
    return res
