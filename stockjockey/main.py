# Import dependencies
import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.exceptions import abort
from stockjockey.auth import login_required
from stockjockey.db import get_db, init_db


# Create blueprint
bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def dashboard():
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
        error = None

        if not ticker:
            error = 'Ticker is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                f'INSERT INTO asset (ticker)'
                f' VALUES ("{ticker}")'
            )
            db.commit()
            return redirect(url_for('main.dashboard'))

    return render_template('main/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, name, ticker'
        ' FROM post p'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('main.dashboard'))
