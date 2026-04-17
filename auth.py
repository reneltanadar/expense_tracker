from db import connect_db
import bcrypt


#  REGISTER (for Flask)
def register_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    # check existing user
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        conn.close()
        return "exists"

    # hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # insert
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, hashed)
    )

    conn.commit()
    conn.close()

    return "success"


#  LOGIN (for Flask)
def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, password FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    conn.close()

    if user:
        user_id, stored_password = user

        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return user_id

    return None