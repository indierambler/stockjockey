# Import dependencies
from . import stocksnap_bp
import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort
from stockjockey.auth.views import login_required
from stockjockey.api import get_db, init_db, query_db


@stocksnap_bp.route('/stock/<ticker>', methods=('GET', 'POST'))
@login_required
def snapshot(ticker=None):
    # Search form
    if request.method == 'POST':
        if request.form['submit'] == 'Search':
            # "search" button - open the ticker snapshot page
            if request.form['ticker']:
                ticker = request.form['ticker'].upper()  # get ticker input
            else:
                flash('Ticker is required.')
                return redirect(url_for('main.stocksnap.snapshot', ticker=ticker))
        elif request.form['submit'] == 'Add':
            # "add" button - add the ticker to watchlist
            query_db(
                f"INSERT INTO asset (ticker)"
                f" VALUES ('{ticker}')"
            )
            flash(f'{ticker} has been added to watchlist.')
            return redirect(url_for('main.stocksnap.snapshot', ticker=ticker))
        elif request.form['submit'] == 'Remove':
            # "remove" button - remove the ticker from watchlist
            query_db(
                f"DELETE FROM asset"
                f" WHERE ticker = '{ticker}'"
            )
            flash(f'{ticker} has been removed from watchlist.')
            return redirect(url_for('main.stocksnap.snapshot', ticker=ticker))

    # Update watchlist form

    # process ticker input
    if ticker:
        # load stock template
        pass
    else:
        # load not found template
        pass

    return render_template('stocksnap/snapshot.html', ticker=ticker)


@stocksnap_bp.route('/search', methods=('GET', 'POST'))
@login_required
def search():
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
            return redirect(url_for('main.dashboard', user_id=session.get('user_id')))

    return render_template('stocksnap/search.html')


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
