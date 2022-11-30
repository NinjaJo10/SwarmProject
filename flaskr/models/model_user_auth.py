class Model_auth:
    @staticmethod
    def insert_user(database, username, password):
        error = ""
        try:
            database.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, password),
            )
            database.commit()
        except database.IntegrityError:
            error = f"User {username} is already registered."

        return error

    @staticmethod
    def get_user_with_name(database, username):
        user = database.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        return user

    @staticmethod
    def get_user_with_id(database, user_id):
        user = database.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

        return user
