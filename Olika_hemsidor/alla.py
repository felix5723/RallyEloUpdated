from .infiniteracing import main as infiniteracing
from .reallyrally import main as reallyrally
from .raceconsult import main as raceconsult
import sqlite3

MAX_RALLYS = 2
SELECTION = "refresh"


def main(max_rallys, choice):
    print(f'Max rallys: {max_rallys} and the choice: {choice}')
    # Connect to the database
    conn = sqlite3.connect('my_database.db')
    if choice == "refresh":
        # Create a cursor object
        cursor = conn.cursor()

        # Drop the 'users' table
        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('DROP TABLE IF EXISTS userStats')
        cursor.execute('DROP TABLE IF EXISTS rallys')
        cursor.execute('DROP TABLE IF EXISTS userselo')

        # Commit the changes
        conn.commit()

    infiniteracing(max_rallys)
    reallyrally(max_rallys)
    raceconsult(max_rallys)


if __name__ == "__main__":
    main(MAX_RALLYS, SELECTION)
