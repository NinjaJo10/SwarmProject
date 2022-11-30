from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.controller_auth import login_required
from flaskr.db import get_db
# db = get_db()


class Model_drone:
    @staticmethod
    def drones_display(database):
        drones = database.execute(
            'SELECT p.id, drone_name, description, ip_addr, port, u.username, owner_id'
            ' FROM drones p JOIN user u ON p.owner_id = u.id'
            ' ORDER BY p.id DESC'
        ).fetchall()
        return drones

    @staticmethod
    def get_drone(database, id):
        drone = database.execute(
            'SELECT p.id, drone_name, description, ip_addr, port, mac_addr, owner_id'
            ' FROM drones p JOIN user u ON p.owner_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()
        return drone

    @staticmethod
    def update_drone_info(database, drone_name, description, ip_addr, port, mac_addr, drone_id):
        database.execute(
            'UPDATE drones SET drone_name = ?, description = ?, ip_addr = ?, port = ?, mac_addr = ?'
            ' WHERE id = ?',
            (drone_name, description, ip_addr, port, mac_addr, drone_id)
        )
        database.commit()

    @staticmethod
    def delete_drone(database, drone_id):
        database.execute('DELETE FROM drones WHERE id = ?', (drone_id,))
        database.commit()

    @staticmethod
    def insert_drone(database, drone_name, description, ip_addr, port, user_id):
        error = ""
        try:
            database.execute(
                "INSERT INTO drones (drone_name, description, ip_addr, port, owner_id, group_id) "
                "VALUES (?, ?, ?, ?, ?, 0)",
                (drone_name, description, ip_addr, port, user_id),
            )
            database.commit()
        except database.IntegrityError:
            error = f"Drone {drone_name} is already registered."

        return error

    @staticmethod
    def get_drones_from_swarm(database, swarm_id):
        drones_in_swarm = database.execute(
            'SELECT *'
            ' FROM drones'
            ' WHERE id in '
            '   (SELECT drone_id '
            '     FROM groups_and_drones'
            '     WHERE group_id = ?)',
            (swarm_id,)
        ).fetchall()
        return drones_in_swarm
