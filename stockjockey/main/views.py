# Import dependencies
from . import main_bp
import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort
from sqlalchemy import insert
from stockjockey.auth.views import login_required
from stockjockey.api import action


@main_bp.route('/')
def home():
    if session.get('user_id', None):
        user_id = session.get('user_id')
        return redirect(url_for('main.dashboard', user_id=session.get('user_id')))
    else:
        return redirect(url_for('auth.login'))


@main_bp.route('/<uuid:user_id>/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard(user_id):
    if request.method == 'POST':
        # process ticker input
        ticker = request.form['ticker'].upper()
        if not ticker:
            flash('Ticker is required.')
            return redirect(url_for('main.dashboard', user_id=user_id))
        else:
            if request.form['submit'] == 'Search':
                # "search" button - open the ticker snapshot page
                return redirect(url_for('main.stocksnap.snapshot', ticker=ticker))
            elif request.form['submit'] == 'Add':
                # "add" button - add the ticker to watchlist
                action.asset.add(ticker=ticker)
                action.user_asset_relation.add(user_id=session.get('user_id'), ticker=ticker)
                action.commit()
            elif request.form['submit'] == 'Remove':
                # "remove" button - remove the ticker from watchlist
                action.user_asset_relation.remove(user_id=session.get('user_id'), ticker=ticker)
                action.commit()

    # get all watchlist items
    posts = action.user_asset_relation.get_user_assets(user_id=session.get('user_id'))
    return render_template('main/dashboard.html', user_id=user_id, posts=posts)


@main_bp.route('/profile', methods=('GET', 'POST'))
@login_required
def user_profile():
    if request.method == 'POST':
        ticker = request.form['ticker']
        error = None

        if not ticker:
            error = 'Ticker is required.'

        if error is not None:
            flash(error)
        else:
            action.asset.add(ticker=ticker)
            action.user_asset_relation.add(user_id=session.get('user_id'), ticker=ticker)
            action.commit()
            return redirect(url_for('main.dashboard'))

    return render_template('main/create.html')
