import sqlite3

database = "../data/players.db"
create = """CREATE TABLE IF NOT EXISTS playersOnline (
    timestamp INTEGER PRIMARY KEY NOT NULL,
    players INT);"""

try:
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(create)   
        conn.commit()
        print("Successfully created table.")
        cursor.close()

except sqlite3.OperationalError as e:
    print(e)