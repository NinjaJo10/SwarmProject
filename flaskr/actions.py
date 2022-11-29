from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr import JO_dronesTello

from flaskr.models.model_drones import Model_drone
from flaskr.models.model_swarms import Model_swarm

bp = Blueprint('actions', __name__)
_selected_swarm = ""


@bp.route('/actions_connect_to_swarm', methods=('GET', 'POST'))
def actions_connect_to_swarm():
    if request.method == "POST":
        selected_swarm = request.form.get('groups_dropdown')
        if connect_to_drones(selected_swarm):
            return redirect(url_for('actions.swarm_connected', swarm=selected_swarm))

    db = get_db()
    swarms = Model_swarm.get_all_swarms(db)

    return render_template('actions/actions_connect_to_swarm.html', swarms=swarms)


@bp.route('/swarm_connected/<swarm>', methods=('GET', 'POST'))
def swarm_connected(swarm):
    basic_actions_list = ['', 'Takeoff', 'Move Left', 'Rotate', 'Move Forward', 'Land']
    routines_list = {
        '': "",
        'Move Left, Rotate and Forwards': "Drone will takeoff, Move to the left, rotate Left, move forwards and then "
                                          "Land"}
    if request.method == "POST":
        selected_action = request.form.get('actions_dropdown')
        selected_routine = request.form.get('routines_dropdown')

        if selected_action and not selected_routine:
            find_action(selected_action, swarm)
        if selected_routine and not selected_action:
            find_routine(selected_routine, swarm)
        elif not selected_routine and not selected_action:
            flash("No Actions or Routines selected, please select one")
        else:
            flash("You've selected an action and a routine, please only select one")

    return render_template('actions/swarm_connected.html', basic_actions_list=basic_actions_list,
                           routines_list=routines_list, swarm=swarm)


def find_action(action, swarm):
    print(action)
    match action:
        case "Takeoff":
            JO_dronesTello.jo_swarm_takeoff(get_drones(swarm))
            print("doing the takeoff stuff")
        case "Move Left":
            print("doing move left")
        case "Rotate":
            print("doing rotate")
        case "Move Forward":
            print("doing move forward")
        case "Land":
            JO_dronesTello.jo_swarm_land(get_drones(swarm))
            print("landing now")
        case _:
            print("Default")


def find_routine(routine, swarm):
    print(routine)
    match routine:
        case "Move Left, Rotate and Forwards":
            print("doing Move Left, Rotate and Forwards stuff")
            JO_dronesTello.jo_swarm_routine_simple(get_drones(swarm))
        case _:
            print("Default")


def get_drones(swarm):
    db = get_db()
    get_swarm_id = Model_swarm.get_swarm_id_from_name(db, swarm)
    swarm_id = get_swarm_id[0][0]
    drones_in_swarm = Model_drone.get_drones_from_swarm(db, swarm_id)
    temp_ips = []
    for d in drones_in_swarm:
        temp_ips.append(d[3])

    return temp_ips


def connect_to_drones(swarm):
    db = get_db()
    get_swarm_id = Model_swarm.get_swarm_id_from_name(db, swarm)
    swarm_id = get_swarm_id[0][0]
    drones_in_swarm = Model_drone.get_drones_from_swarm(db, swarm_id)
    temp_ips = []
    for d in drones_in_swarm:
        temp_ips.append(d[3])

    return JO_dronesTello.jo_swarm_connect(temp_ips)
