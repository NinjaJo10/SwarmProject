from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('actions', __name__)


@bp.route('/mainpage')
def mainpage():
    db = get_db()
    drones = db.execute(
        'SELECT p.id, drone_name, description, ip_addr, port, u.username, owner_id'
        ' FROM drones p JOIN user u ON p.owner_id = u.id'
        ' ORDER BY p.id DESC'
    ).fetchall()
    return render_template('actions/mainpage.html', drones=drones)
