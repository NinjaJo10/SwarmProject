from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('swarms', __name__)


@bp.route('/swarms')
def swarms():
    db = get_db()
    drones_in_group_dict = {}
    amt_drones_in_group_dict = {}
    drones_in_group = []

    groups1 = get_group()
    for group in groups1:
        temp_id = group['id']
        drones_in_group = get_drones_from_a_group(temp_id)
        count_row = count_drones_a_group(temp_id)
        for item in count_row:
            if item[0] != 0:
                amt_drones_in_group_dict[temp_id] = item[0]
        drones_in_group_dict[temp_id] = drones_in_group
    return render_template('swarms/swarms_display.html', groups=groups1,
                           amt_drones_in_group_dict=amt_drones_in_group_dict,
                           drones_in_group_dict=drones_in_group_dict)


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
        ' WHERE id in (SELECT drone_id FROM groups_and_drones WHERE groups_and_drones.group_id = ?)', (group_id,)
    ).fetchall()

    if drones is None:
        abort(404, f"No Drones in this group.")

    return drones


def count_drones_a_group(group_id):
    drones = get_db().execute(
        'SELECT COUNT (*)'
        ' FROM drones'
        ' WHERE id in (select drone_id from groups_and_drones where groups_and_drones.group_id = ?)', (group_id,)
    ).fetchall()

    if drones is None:
        abort(404, f"No Drones in this group.")

    return drones


@bp.route('/register_swarm', methods=('GET', 'POST'))
def register_swarm():
    if request.method == 'POST':
        group_name = request.form['group_name']
        db = get_db()
        error = None

        if not group_name:
            error = 'Group Name is required.'

        if error is None:
            try:
                print("Insert here?")
                db.execute(
                    "INSERT INTO groups (group_name) VALUES (?)", (group_name,)
                )
                db.commit()
            except db.IntegrityError:
                error = f"Group {group_name} is already registered."
            else:
                return redirect(url_for('drones.groups'))

        flash(error)

    return render_template('swarms/register_swarm.html')


@bp.route('/<int:id>/add_drone_to_swarm', methods=('GET', 'POST'))
def add_drone_to_swarm(id):
    group_id = id
    group = get_group(id)
    user_id = session.get('user_id')
    # flash(user_id)
    drones_to_add = get_drones_not_in_group(user_id, group_id)

    if request.method == "POST":
        db = get_db()
        for items in drones_to_add:
            if request.form['add_button'] == "Add " + items['drone_name'] + " to Group":
                temp_id = int(items['id'])
                db.execute(
                    'INSERT INTO groups_and_drones (drone_id, group_id)'
                    ' VALUES (?, ?)',
                    (temp_id, group_id, )
                )
                break
        db.commit()
        return redirect(url_for('drones.groups'))

    return render_template('swarms/add_drone_to_swarm.html', drones_to_group=drones_to_add, group=group)


def get_drones_not_in_group(user_id, group_id, check_author=True):
    drones_not_in_group = get_db().execute(
        'SELECT p.id, drone_name, description, ip_addr, port, mac_addr, owner_id'
        ' FROM drones p JOIN user u ON p.owner_id = u.id'
        ' WHERE u.id = ? AND p.id NOT IN (SELECT drone_id FROM groups_and_drones WHERE group_id = ?)',
        (user_id, group_id,)
    ).fetchall()

    if drones_not_in_group is None:
        abort(404, f"Drone doesn't exist.")

    return drones_not_in_group


def get_group(id, check_author=True):
    group = get_db().execute(
        'SELECT id, group_name'
        ' FROM groups '
        ' WHERE id = ?', (id,)
    ).fetchone()

    if group is None:
        abort(404, f"Group id {id} doesn't exist.")

    return group
