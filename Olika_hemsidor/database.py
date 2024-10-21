import mysql.connector


def database_connect():
    # Database connection settings
    conn = mysql.connector.connect(
        host="felix5723.mysql.pythonanywhere-services.com",
        user="felix5723",
        password="databasepass",  # Replace with your actual MySQL password
        database="felix5723$default"  # Replace with the name of your MySQL database
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
        'SELECT * FROM rallys WHERE rallyName = %s AND rallyDate = %s', (rallyName, rallyDate))
    if_rally = cursor.fetchall()
    if len(if_rally) == 0:
        return False
    else:
        return True


def database_check_if_user_added(cursor, conn, driver, name, klubb):
    cursor.execute(
        'SELECT * FROM users WHERE driver = %s AND name = %s AND klubb = %s', (driver, name, klubb))
    if_user = cursor.fetchall()
    if len(if_user) == 0:
        cursor.execute(
            'INSERT INTO users (driver, name, klubb) VALUES (%s, %s, %s)', (driver, name, klubb))
        conn.commit()
        cursor.execute(
            'SELECT * FROM users WHERE driver = %s AND name = %s AND klubb = %s', (driver, name, klubb))
        if_user = cursor.fetchall()
    user_id = if_user[0][0]
    return user_id


def database_add(cursor, conn, rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place):
    # Insert data
    user_id = database_check_if_user_added(cursor, conn, driver, name, klubb)
    cursor.execute(
        'INSERT INTO userStats (user_id, rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (user_id, rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place))

    # Commit the changes
    conn.commit()
    return cursor, conn


def database_add_rally(cursor, conn, rallyName, rallyDate):
    # Insert data
    cursor.execute(
        'INSERT INTO rallys (rallyName, rallyDate) VALUES (%s, %s)', (rallyName, rallyDate))

    # Commit the changes
    conn.commit()
    return cursor, conn


def datebase_start():
    cursor, conn = database_connect()

    # Create a table for users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        driver VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        klubb VARCHAR(255) NOT NULL
    )
    ''')
    conn.commit()

    # Create a table for userStats
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userStats (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,  -- Add user_id column for foreign key reference,
        rallyName VARCHAR(255) NOT NULL,
        rallyDate VARCHAR(255) NOT NULL,
        driver VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        klubb VARCHAR(255) NOT NULL,
        klass VARCHAR(255) NOT NULL,
        driverKlass VARCHAR(255) NOT NULL,
        time VARCHAR(255) NOT NULL,
        startnummer INT,
        total_place INT,
        klass_place INT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE  -- Define the foreign key constraint here
    )
    ''')
    conn.commit()

    # Create a table for rallys
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rallys (
        id INT AUTO_INCREMENT PRIMARY KEY,
        rallyName VARCHAR(255) NOT NULL,
        rallyDate VARCHAR(255) NOT NULL
    )
    ''')
    conn.commit()

    # Create a table for elo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userselo (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,  -- Add user_id column for foreign key reference,
        rallys_id INT,  -- Add rallys_id column for foreign key reference,
        rallyName VARCHAR(255) NOT NULL,
        rallyDate VARCHAR(255) NOT NULL,
        total_elo VARCHAR(255) NOT NULL,
        klass_elo VARCHAR(255) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (rallys_id) REFERENCES rallys(id) ON DELETE CASCADE
    )
    ''')
    conn.commit()

    # Close the cursor and connection
    database_exit(cursor, conn)


# Call the function to create tables and interact with the database
datebase_start()
