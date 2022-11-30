class Model_swarm:
    @staticmethod
    def get_all_swarms(database):
        swarms = database.execute(
            'SELECT *'
            ' FROM groups'
        ).fetchall()

        return swarms

    @staticmethod
    def get_drones_from_a_swarm(database, swarm_id):
        drones = database.execute(
            'SELECT *'
            ' FROM drones'
            ' WHERE id in (SELECT drone_id FROM groups_and_drones WHERE groups_and_drones.group_id = ?)', (swarm_id,)
        ).fetchall()

        return drones

    @staticmethod
    def count_of_drones_a_group(database, swarm_id):
        drones_count = database.execute(
            'SELECT COUNT (*)'
            ' FROM drones'
            ' WHERE id in (select drone_id from groups_and_drones where groups_and_drones.group_id = ?)', (swarm_id,)
        ).fetchall()

        return drones_count

    @staticmethod
    def insert_swarm(database, swarm_name):
        error = ""
        try:
            database.execute(
                "INSERT INTO groups (group_name) VALUES (?)", (swarm_name,)
            )
            database.commit()
        except database.IntegrityError:
            error = f"Swarm {swarm_name} is already registered."

        return error

    @staticmethod
    def add_drone_to_swarm(database, temp_id, swarm_id):
        database.execute(
            'INSERT INTO groups_and_drones (drone_id, group_id)'
            ' VALUES (?, ?)',
            (temp_id, swarm_id,)
        )

    @staticmethod
    def get_drones_not_in_swarm(database, user_id, swarm_id):
        drones_not_in_swarm = database.execute(
            'SELECT p.id, drone_name, description, ip_addr, port, mac_addr, owner_id'
            ' FROM drones p JOIN user u ON p.owner_id = u.id'
            ' WHERE u.id = ? AND p.id NOT IN (SELECT drone_id FROM groups_and_drones WHERE group_id = ?)',
            (user_id, swarm_id,)
        ).fetchall()

        return drones_not_in_swarm

    @staticmethod
    def get_swarm(database, swarm_id):
        swarm = database.execute(
            'SELECT id, group_name'
            ' FROM groups '
            ' WHERE id = ?', (swarm_id,)
        ).fetchone()

        return swarm

    @staticmethod
    def get_swarm_id_from_name(database, swarm_name):
        get_group_id = database.execute(
            'SELECT id'
            ' FROM groups'
            ' WHERE group_name = ?',
            (swarm_name,)
        ).fetchall()
        return get_group_id
