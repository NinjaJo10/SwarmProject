from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr import JO_dronesTello

bp = Blueprint('actions', __name__)


@bp.route('/mainpage', methods=('GET', 'POST'))
def mainpage():
    if request.method == "POST":
        flash("Button Pushed Post")
        selected_swarm = request.form.get('groups_dropdown')
        # selected_item = request.form.get('selected_group')
        # print(selected_swarm)
        connect_to_drones(selected_swarm)
    db = get_db()
    groups = db.execute(
        'SELECT group_name'
        ' FROM groups'
    ).fetchall()
    drones = db.execute(
        'SELECT p.id, drone_name, description, ip_addr, port, u.username, owner_id'
        ' FROM drones p JOIN user u ON p.owner_id = u.id'
        ' ORDER BY p.id DESC'
    ).fetchall()

    return render_template('actions/mainpage.html', groups=groups)


def connect_to_drones(group_name):
    db = get_db()
    get_group_id = db.execute(
        'SELECT id'
        ' FROM groups'
        ' WHERE group_name = ?',
        (group_name,)
    ).fetchall()
    group_id = get_group_id[0][0]
    drones_in_swarm = db.execute(
        'SELECT *'
        ' FROM drones'
        ' WHERE id in '
        '   (SELECT drone_id '
        '     FROM groups_and_drones'
        '     WHERE group_id = ?)',
        (group_id,)
    ).fetchall()
    temp_ips = []
    for d in drones_in_swarm:
        temp_ips.append(d[3])
    # print(temp_ips)
    JO_dronesTello.jo_swarm_connect(temp_ips)
