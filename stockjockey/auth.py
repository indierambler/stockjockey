# Import dependencies
import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from stockjockey.db import get_db, init_db


# Create blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = email  # maybe change to everything before the @ in the email?
        password = request.form['password']
        db = get_db()
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # db.execute(
                #    "INSERT INTO user (email, username, password) VALUES (?, ?, ?)",
                #    (email, username, generate_password_hash(password)),
                # )
                # db.commit()
                with g.db.cursor() as cursor:
                    cursor.execute(
                        f"""INSERT INTO user_meta (email, username, password) VALUES
                        ('{email}', '{username}', '{generate_password_hash(password)}')"""
                    )
                db.commit()
                db.close()
            except db.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        # username = email  # maybe change to everything before the @ in the email?
        password = request.form['password']
        db = get_db()
        error = None
        # user = db.execute(
        #    f'SELECT * FROM user WHERE email = "{email}"'
        # ).fetchone()
        with g.db.cursor() as cursor:
            user = cursor.execute(
                f'SELECT * FROM user_meta WHERE email = "{email}"'
            ).fetchone()
        db.close()

        if email is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            f'SELECT * FROM user_meta WHERE id = {user_id}'
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not os.path.exists(os.path.join(current_app.instance_path, 'stockjockey.sqlite')):
            init_db()

        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
