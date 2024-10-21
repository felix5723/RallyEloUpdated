import mysql.connector


def database_connect():

    # Database connection settings
    conn = mysql.connector.connect(
        host="felix5723.mysql.pythonanywhere-services.com",
        user="felix5723",
        password="your_mysql_password",  # Replace with your actual MySQL password
        database="your_database_name"  # Replace with the name of your MySQL database
    )

    cursor = conn.cursor()

    # Check connection
    if conn.is_connected():
        print("Successfully connected to the MySQL database")
    else:
        print("Failed to connect to the MySQL database")

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
    if len(if_rally) == 0:
        return False
    else:
        return True


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
    # Insert data
    user_id = database_check_if_user_added(cursor, conn, driver, name, klubb)
    cursor.execute(
        'INSERT INTO userStats (user_id, rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (user_id, rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place))

    # Commit the changes
    conn.commit()
    return cursor, conn


def database_add_rally(cursor, conn, rallyName, rallyDate):
    # Insert data
    cursor.execute(
        'INSERT INTO rallys (rallyName, rallyDate) VALUES (?, ?)', (rallyName, rallyDate))

    # Commit the changes
    conn.commit()
    return cursor, conn


def datebase_start():
    cursor, conn = database_connect()
    data = {'total_place': '27', 'klass_place': '1', 'number': '1', 'klass': 'Ungdom', 'driverklass': 'U',
            'time': '14:44,3', 'name': 'Ludvig Fransson', 'klubb': 'Vimmerby MS', 'driver': 'driver'}

    # Create a table for users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        driver TEXT NOT NULL,
        name TEXT NOT NULL,
        klubb TEXT NOT NULL
    )
    ''')
    conn.commit

    # Create a table for userStats
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userStats (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,  -- Add user_id column for foreign key reference,
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
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE  -- Define the foreign key constraint here
    )
    ''')
    conn.commit

    # Create a table for rallys
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rallys (
        id INTEGER PRIMARY KEY,
        rallyName TEXT NOT NULL,
        rallyDate TEXT NOT NULL
    )
    ''')
    conn.commit

    # Create a table for elo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userselo (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,  -- Add user_id column for foreign key reference,
        rallys_id INTEGER,  -- Add rallys_id column for foreign key reference,
        rallyName TEXT NOT NULL,
        rallyDate TEXT NOT NULL,
        total_elo TEXT NOT NULL,
        klass_elo TEXT NOT NULL
    )
    ''')
    conn.commit

    # Close the cursor and connection
    database_exit(cursor, conn)
