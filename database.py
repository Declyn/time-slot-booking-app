import sqlite3

database_file = "database.db"

def execute(command, args=(), query=False):
    with sqlite3.connect(database_file) as connection:

        cursor = connection.cursor()
        cursor.execute(command, args)

        if query:
            return cursor.fetchall()

        connection.commit()

def create_defaults():
    execute('''CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(32) PRIMARY KEY,
        password VARCHAR(32) NOT NULL,
        role VARCHAR(16) NOT NULL
    );''')

    execute('''CREATE TABLE IF NOT EXISTS bookable_events (
        name VARCHAR(32) PRIMARY KEY,
        description VARCHAR(128),
        date VARCHAR(16) NOT NULL,
        start_time VARCHAR(16) NOT NULL,
        number_slots INTEGER,
        slot_duration INTEGER
    );''')

    execute('''CREATE TABLE IF NOT EXISTS bookings (
        event_name VARCHAR(32) NOT NULL,
        student_username VARCHAR(32),
        time_slot VARCHAR(16)
    );''')

    query = execute('SELECT * FROM users', query=True)

    if not query:
        execute('''INSERT INTO users VALUES ('admin', 'password', 'admin')''')