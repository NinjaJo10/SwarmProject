import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register_drone', methods=('GET', 'POST'))
def register_drone():
    if request.method == 'POST':
        drone_name = request.form['drone_name']
        description = request.form['description']
        ip_addr = request.form['ip_addr']
        port = request.form['port']
        db = get_db()
        error = None

        if not drone_name:
            error = 'Drone Name is required.'
        elif not description:
            error = 'Description is required.'
        elif not ip_addr:
            error = 'IP Address is required.'
        elif not port:
            error = 'Port is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO drones (drone_name, description, ip_addr, port, owner_id) VALUES (?, ?, ?, ?, ?)",
                    (drone_name, description, ip_addr, port, g.user['id']),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Drone {drone_name} is already registered."
            else:
                return redirect(url_for('index'))

        flash(error)

    return render_template('auth/register_drone.html')


@bp.route('/register_group', methods=('GET', 'POST'))
def register_group():
    if request.method == 'POST':
        group_name = request.form['group_name']
        db = get_db()
        error = None

        if not group_name:
            error = 'Group Name is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO groups (group_name) VALUES (?)," (group_name),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Group {group_name} is already registered."
            else:
                return redirect(url_for('groups'))

        flash(error)

    return render_template('auth/register_group.html')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
