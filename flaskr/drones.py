from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('drones', __name__)


@bp.route('/')
def drones_display():
    db = get_db()
    drones = db.execute(
        'SELECT p.id, drone_name, description, ip_addr, port, u.username, owner_id'
        ' FROM drones p JOIN user u ON p.owner_id = u.id'
        ' ORDER BY p.id DESC'
    ).fetchall()
    return render_template('drones/drones_display.html', drones=drones)


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
def update_info(id):
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
            return redirect(url_for('drones.drones_display'))

    return render_template('drones/update_info.html', drone=drone)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_drone(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('drones.index'))


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
                    "INSERT INTO drones (drone_name, description, ip_addr, port, owner_id, group_id) "
                    "VALUES (?, ?, ?, ?, ?, 0)",
                    (drone_name, description, ip_addr, port, g.user['id']),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Drone {drone_name} is already registered."
            else:
                return redirect(url_for('drones_display'))

        flash(error)

    return render_template('drones/register_drone.html')
