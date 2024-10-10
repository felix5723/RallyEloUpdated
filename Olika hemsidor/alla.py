from infiniteracing import main as infiniteracing
from reallyrally import main as reallyrally
from raceconsult import main as raceconsult
import sqlite3

MAX_RALLYS = 5


def selection():
    print("Go: Will append and if the rally isn't already added it will be added")
    print("Refresh: The database for rallys will be deleted and started from the begining")
    # test = input("Go/Refresh: ").lower()
    test = "refresh"
    return test


def main():
    if selection() == "refresh":
        # Connect to the database
        conn = sqlite3.connect('my_database.db')

        # Create a cursor object
        cursor = conn.cursor()

        # Drop the 'users' table
        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('DROP TABLE IF EXISTS userStats')
        cursor.execute('DROP TABLE IF EXISTS rallys')

        # Commit the changes
        conn.commit()

    infiniteracing(MAX_RALLYS)
    reallyrally(MAX_RALLYS)
    raceconsult(MAX_RALLYS)


main()
