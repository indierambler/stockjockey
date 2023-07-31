# Import dependencies
from . import stocksnap_bp
import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort
from stockjockey.auth.views import login_required
from stockjockey.api import action


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
            action.asset.add(ticker=ticker)
            action.user_asset_relation.add(user_id=session.get('user_id'), ticker=ticker)
            action.commit()
            flash(f'{ticker} has been added to watchlist.')
            return redirect(url_for('main.stocksnap.snapshot', ticker=ticker))
        elif request.form['submit'] == 'Remove':
            # "remove" button - remove the ticker from watchlist
            action.user_asset_relation.remove(user_id=session.get('user_id'), ticker=ticker)
            action.commit()
            flash(f'{ticker} has been removed from watchlist.')
            return redirect(url_for('main.stocksnap.snapshot', ticker=ticker))

    # Update watchlist form

    # process ticker input
    if ticker:
        # get ticker row from asset table (if exists)
        # if not - get ticker data from the aether and put in asset table
        # get corresponding row from asset_meta table (if exists)
        # if not - get metadata from the aether and put in asset_meta table
        # get all rows from asset_metric table to complete nasdaq12 analysis
        # get any missing data for nasdaq12 from the aether and add to asset_metric table
        pass
    else:
        # flash ticker not valid message
        pass

    return render_template('stocksnap/snapshot.html', ticker=ticker)
