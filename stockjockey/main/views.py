# Import dependencies
from . import main_bp
import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort
from stockjockey.auth import login_required
from stockjockey.api import get_db, init_db, query_db


@main_bp.route('/', methods=('GET', 'POST'))
@login_required
def dashboard():
    if request.method == 'POST':
        # process ticker input
        ticker = request.form['ticker']
        error = None
        if not ticker:
            error = 'Ticker is required.'
            flash(error)
        else:
            if request.form['submit'] == 'Search':
                # "search" button - open the ticker snapshot page
                return redirect(url_for('main.stocksnap.snapshot', ticker=ticker))
            elif request.form['submit'] == 'Add':
                # "add" button - add the ticker to watchlist
                query_db(
                    f"INSERT INTO asset (ticker)"
                    f" VALUES ('{ticker}')"
                )
            elif request.form['submit'] == 'Remove':
                # "remove" button - remove the ticker from watchlist
                query_db(
                    f"DELETE FROM asset"
                    f" WHERE ticker = '{ticker}'"
                )

    # get all watchlist items
    posts = query_db(
        'SELECT * FROM asset'
    )
    return render_template('main/dashboard.html', posts=posts)


@main_bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        ticker = request.form['ticker']
        error = None

        if not ticker:
            error = 'Ticker is required.'

        if error is not None:
            flash(error)
        else:
            query_db(
                f"INSERT INTO asset (ticker)"
                f" VALUES ('{ticker}')"
            )
            return redirect(url_for('main.dashboard'))

    return render_template('main/create.html')


def get_post(id, check_author=True):
    post = query_db(
        'SELECT p.id, name, ticker'
        ' FROM post p'
        ' WHERE p.id = ?',
        (id,)
    )[0]

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@main_bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = query_db('DELETE FROM post WHERE id = ?', (id,))
    return redirect(url_for('main.dashboard'))
