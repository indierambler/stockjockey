# Import dependencies
import functools, os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort
from stockjockey.auth import login_required
from stockjockey.db import get_db, init_db


# Create blueprint
bp = Blueprint('main', __name__)


@bp.route('/')
def dashboard():
    if not os.path.exists(os.path.join(current_app.instance_path, 'stockjockey.sqlite')):
        init_db()
    
    db = get_db()
    posts = db.execute(
        'SELECT * FROM asset'
    ).fetchall()
    return render_template('main/dashboard.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        ticker = request.form['ticker']
        exchange = request.form['exchange']
        sector = request.form['sector']
        error = None

        if not ticker:
            error = 'Ticker is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO asset (ticker, exchange, sector)'
                ' VALUES (?, ?, ?)',
                (ticker, exchange, sector)
            )
            db.commit()
            return redirect(url_for('main.dashboard'))

    return render_template('main/create.html')