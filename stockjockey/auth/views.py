# Import dependencies
from . import auth_bp
import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from stockjockey.api import get_db, init_db, query_db


@auth_bp.route('/register', methods=('GET', 'POST'))
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
                query_db(
                        f"""INSERT INTO user_meta (email, username, password) VALUES
                        ('{email}', '{username}', '{generate_password_hash(password)}')"""
                    )
            except g.db.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        # username = email  # maybe change to everything before the @ in the email?
        password = request.form['password']
        db = get_db()
        error = None
        
        user = query_db(
                f"SELECT * FROM user_meta WHERE email = '{email}'"
            )[0]

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


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = query_db(
                f'SELECT * FROM user_meta WHERE id = {user_id}'
            )[0]


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # check if db exists
        # if not os.path.exists(os.path.join(current_app.instance_path, 'stockjockey.sqlite')):
        #    init_db()

        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
