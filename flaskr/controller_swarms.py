from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.controller_auth import login_required
from flaskr.db import get_db
from flaskr.models.model_swarms import Model_swarm

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
    db = get_db()
    swarm = Model_swarm.get_all_swarms(db)

    if swarm is None:
        abort(404, f"No Swarms doesn't exist.")

    return swarm


def get_drones_from_a_swarm(swarm_id):
    db = get_db()
    drones = Model_swarm.get_drones_from_a_swarm(db, swarm_id)

    if drones is None:
        abort(404, f"No Drones in this swarm.")

    return drones


def count_drones_a_group(swarm_id):
    db = get_db()
    drones = Model_swarm.count_of_drones_a_group(db, swarm_id)

    if drones is None:
        abort(404, f"No Drones in this Swarm.")

    return drones


@bp.route('/register_swarm', methods=('GET', 'POST'))
def register_swarm():
    if request.method == 'POST':
        swarm_name = request.form['swarm_name']
        error = None

        if not swarm_name:
            error = 'Swarm Name is required.'

        if error is None:
            db = get_db()
            result = Model_swarm.insert_swarm(db, swarm_name)
            print("out of model", result)
            if result is "":
                return redirect(url_for('swarms.swarms'))
            else:
                flash(result)
        else:
            flash(error)

    return render_template('swarms/register_swarm.html')


@bp.route('/<int:id>/add_drone_to_swarm', methods=('GET', 'POST'))
def add_drone_to_swarm(id):
    swarm_id = id
    this_swarm = get_swarm(id)
    user_id = session.get('user_id')
    drones_to_add = get_drones_not_in_swarm(user_id, swarm_id)

    if request.method == "POST":
        db = get_db()
        for items in drones_to_add:
            if request.form['add_button'] == "Add " + items['drone_name'] + " to Swarm":
                temp_id = int(items['id'])
                Model_swarm.add_drone_to_swarm(db, temp_id, swarm_id)
                break
        db.commit()
        return redirect(url_for('swarms.swarms'))

    return render_template('swarms/add_drone_to_swarm.html', drones_to_swarm=drones_to_add, swarm=this_swarm)


def get_drones_not_in_swarm(user_id, swarm_id, check_author=True):
    db = get_db()
    drones_not_in_swarm = Model_swarm.get_drones_not_in_swarm(db, user_id, swarm_id)

    if drones_not_in_swarm is None:
        abort(404, f"Drone doesn't exist.")

    return drones_not_in_swarm


def get_swarm(id, check_author=True):
    db = get_db()
    swarm = Model_swarm.get_swarm(db, id)

    if swarm is None:
        abort(404, f"Swarm id {id} doesn't exist.")

    return swarm
