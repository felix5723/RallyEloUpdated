import sqlite3
import os


def database_connect():
    # Use an absolute path for the SQLite database
    # Get the absolute path of the current file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Define the path for the SQLite database
    db_path = os.path.join(BASE_DIR, 'my_database.db')

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return cursor, conn


def database_exit(cursor, conn):
    # Query the database
    print("---------------")
    cursor.execute('SELECT * FROM rallys')
    rows = cursor.fetchall()

    # Print the results
    for row in rows:
        print(row)
    print("---------------")
    cursor.close()
    conn.close()
    return "closed"


def database_check_if_rally_added(cursor, conn, rallyName, rallyDate):
    cursor.execute(
        'SELECT * FROM rallys WHERE rallyName = ? AND rallyDate = ?', (rallyName, rallyDate))
    if_rally = cursor.fetchall()
    return len(if_rally) != 0


def database_check_if_user_added(cursor, conn, driver, name, klubb):
    cursor.execute(
        'SELECT * FROM users WHERE driver = ? AND name = ? AND klubb = ?', (driver, name, klubb))
    if_user = cursor.fetchall()
    if len(if_user) == 0:
        cursor.execute(
            'INSERT INTO users (driver, name, klubb) VALUES (?, ?, ?)', (driver, name, klubb))
        conn.commit()
        cursor.execute(
            'SELECT * FROM users WHERE driver = ? AND name = ? AND klubb = ?', (driver, name, klubb))
        if_user = cursor.fetchall()
    user_id = if_user[0][0]
    return user_id


def database_add(cursor, conn, rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place):
    user_id = database_check_if_user_added(cursor, conn, driver, name, klubb)
    cursor.execute(
        'INSERT INTO userStats (user_id, rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (user_id, rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place))

    conn.commit()
    return cursor, conn


def database_add_rally(cursor, conn, rallyName, rallyDate):
    cursor.execute(
        'INSERT INTO rallys (rallyName, rallyDate) VALUES (?, ?)', (rallyName, rallyDate))
    conn.commit()
    return cursor, conn


def database_start():
    cursor, conn = database_connect()

    # Create a table for users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        driver TEXT NOT NULL,
        name TEXT NOT NULL,
        klubb TEXT NOT NULL
    )
    ''')
    conn.commit()  # Ensure to call commit() correctly

    # Create a table for userStats
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userStats (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,  
        rallyName TEXT NOT NULL,
        rallyDate TEXT NOT NULL,
        driver TEXT NOT NULL,
        name TEXT NOT NULL,
        klubb TEXT NOT NULL,
        klass TEXT NOT NULL,
        driverKlass TEXT NOT NULL,
        time TEXT NOT NULL,
        startnummer INTEGER,
        total_place INTEGER,
        klass_place INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    conn.commit()

    # Create a table for rallys
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rallys (
        id INTEGER PRIMARY KEY,
        rallyName TEXT NOT NULL,
        rallyDate TEXT NOT NULL
    )
    ''')
    conn.commit()

    # Create a table for elo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userselo (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        rallys_id INTEGER,
        rallyName TEXT NOT NULL,
        rallyDate TEXT NOT NULL,
        total_elo TEXT NOT NULL,
        klass_elo TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (rallys_id) REFERENCES rallys(id)
    )
    ''')
    conn.commit()

    # Close the cursor and connection
    database_exit(cursor, conn)
