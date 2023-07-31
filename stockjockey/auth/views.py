# Import dependencies
from . import auth_bp
import functools
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from stockjockey.api import query_db, action
from stockjockey.api.service.util import get_db


@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = email  # maybe change to everything before the @ in the email?
        password = request.form['password']
        get_db()
        error = None
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                action.user.add(email=email, username=username, password=password)
                action.commit()
            except g.db.exc.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)
        return redirect(url_for('auth.register'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        get_db()
        error = None
        if not email:
            error = 'Email is required.'
        else:
            user = action.user.get(email=email)  # TODO: try and except this?
            if not user.password == password:
                error = 'Password is incorrect.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.dashboard', user_id=session['user_id']))

        flash(error)
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = action.user.get(id=user_id)


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
