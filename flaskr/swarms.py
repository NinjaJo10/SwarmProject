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
    drones_in_swarm_dict = {}
    amt_drones_in_swarm_dict = {}

    all_swarms = get_all_swarms()
    for swarm in all_swarms:
        temp_id = swarm['id']
        drones_in_group = get_drones_from_a_swarm(temp_id)
        count_of_drones = count_drones_a_group(temp_id)
        for drone in count_of_drones:
            if drone[0] != 0:
                amt_drones_in_swarm_dict[temp_id] = drone[0]
        drones_in_swarm_dict[temp_id] = drones_in_group
    return render_template('swarms/swarms_display.html', swarms=all_swarms,
                           amt_drones_in_group_dict=amt_drones_in_swarm_dict,
                           drones_in_group_dict=drones_in_swarm_dict)


def get_all_swarms():
    swarm = get_db().execute(
        'SELECT *'
        ' FROM groups'
    ).fetchall()

    if swarm is None:
        abort(404, f"No Swarms doesn't exist.")

    return swarm


def get_drones_from_a_swarm(swarm_id):
    drones = get_db().execute(
        'SELECT *'
        ' FROM drones'
        ' WHERE id in (SELECT drone_id FROM groups_and_drones WHERE groups_and_drones.group_id = ?)', (swarm_id,)
    ).fetchall()

    if drones is None:
        abort(404, f"No Drones in this swarm.")

    return drones


def count_drones_a_group(swarm_id):
    drones = get_db().execute(
        'SELECT COUNT (*)'
        ' FROM drones'
        ' WHERE id in (select drone_id from groups_and_drones where groups_and_drones.group_id = ?)', (swarm_id,)
    ).fetchall()

    if drones is None:
        abort(404, f"No Drones in this Swarm.")

    return drones


@bp.route('/register_swarm', methods=('GET', 'POST'))
def register_swarm():
    if request.method == 'POST':
        swarm_name = request.form['swarm_name']
        db = get_db()
        error = None

        if not swarm_name:
            error = 'Swarm Name is required.'

        if error is None:
            try:
                print("Insert here?")
                db.execute(
                    "INSERT INTO groups (group_name) VALUES (?)", (swarm_name,)
                )
                db.commit()
            except db.IntegrityError:
                error = f"Swarm {swarm_name} is already registered."
            else:
                return redirect(url_for('swarms.swarms'))

        flash(error)

    return render_template('swarms/register_swarm.html')


@bp.route('/<int:id>/add_drone_to_swarm', methods=('GET', 'POST'))
def add_drone_to_swarm(id):
    swarm_id = id
    this_swarm = get_swarm(id)
    user_id = session.get('user_id')
    # flash(user_id)
    drones_to_add = get_drones_not_in_swarm(user_id, swarm_id)

    if request.method == "POST":
        db = get_db()
        for items in drones_to_add:
            if request.form['add_button'] == "Add " + items['drone_name'] + " to Swarm":
                temp_id = int(items['id'])
                db.execute(
                    'INSERT INTO groups_and_drones (drone_id, group_id)'
                    ' VALUES (?, ?)',
                    (temp_id, swarm_id, )
                )
                break
        db.commit()
        return redirect(url_for('swarms.swarms'))

    return render_template('swarms/add_drone_to_swarm.html', drones_to_swarm=drones_to_add, swarm=this_swarm)


def get_drones_not_in_swarm(user_id, swarm_id, check_author=True):
    drones_not_in_swarm = get_db().execute(
        'SELECT p.id, drone_name, description, ip_addr, port, mac_addr, owner_id'
        ' FROM drones p JOIN user u ON p.owner_id = u.id'
        ' WHERE u.id = ? AND p.id NOT IN (SELECT drone_id FROM groups_and_drones WHERE group_id = ?)',
        (user_id, swarm_id,)
    ).fetchall()

    if drones_not_in_swarm is None:
        abort(404, f"Drone doesn't exist.")

    return drones_not_in_swarm


def get_swarm(id, check_author=True):
    swarm = get_db().execute(
        'SELECT id, group_name'
        ' FROM groups '
        ' WHERE id = ?', (id,)
    ).fetchone()

    if swarm is None:
        abort(404, f"Swarm id {id} doesn't exist.")

    return swarm
