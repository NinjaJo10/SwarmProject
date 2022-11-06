from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    drones = db.execute(
        'SELECT p.id, drone_name, description, ip_addr, port, u.username, owner_id'
        ' FROM drones p JOIN user u ON p.owner_id = u.id'
        ' ORDER BY p.id DESC'
    ).fetchall()
    return render_template('blog/index.html', drones=drones)


@bp.route('/groups')
def groups():
    db = get_db()
    drones_in_group_dict = {}

    groups1 = get_group()
    for group in groups1:
        temp_id = group['id']
        drones_in_group = get_drones_from_a_group(temp_id)
        count_row = count_drones_a_group(temp_id)
        for item in count_row:
            if item[0] != 0:
                drones_in_group_dict[temp_id] = item[0]

    return render_template('blog/groups.html', groups=groups1, drones_in_group_dict=drones_in_group_dict,
                           drones_in_group=drones_in_group)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_drone(id, check_author=True):
    drone = get_db().execute(
        'SELECT p.id, drone_name, description, ip_addr, port, mac_addr, owner_id'
        ' FROM drones p JOIN user u ON p.owner_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if drone is None:
        abort(404, f"Drone id {id} doesn't exist.")

    if check_author and drone['owner_id'] != g.user['id']:
        abort(403)

    return drone


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    drone = get_drone(id)

    if request.method == 'POST':
        drone_name = request.form['drone_name']
        description = request.form['description']
        ip_addr = request.form['ip_addr']
        port = request.form['port']
        mac_addr = request.form['mac_addr']
        error = None

        if not drone_name:
            error = 'Drone Name is required.'
        elif not description:
            error = 'Description is required.'
        elif not ip_addr:
            error = 'IP Address is required.'
        elif not port:
            error = 'Port is required.'
        elif not mac_addr:
            error = 'Mac Address is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE drones SET drone_name = ?, description = ?, ip_addr = ?, port = ?, mac_addr = ?'
                ' WHERE id = ?',
                (drone_name, description, ip_addr, port, mac_addr, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', drone=drone)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_drone(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


def get_group():
    group = get_db().execute(
        'SELECT *'
        ' FROM groups'
    ).fetchall()

    if group is None:
        abort(404, f"No Groups doesn't exist.")

    return group


def get_drones_from_a_group(group_id):
    drones = get_db().execute(
        'SELECT *'
        ' FROM drones'
        ' WHERE group_id = ?', (group_id,)
    ).fetchall()

    if drones is None:
        abort(404, f"No Drones in this group.")

    return drones


def count_drones_a_group(group_id):
    drones = get_db().execute(
        'SELECT COUNT (*)'
        ' FROM drones'
        ' WHERE group_id = ?', (group_id,)
    ).fetchall()

    if drones is None:
        abort(404, f"No Drones in this group.")

    return drones
