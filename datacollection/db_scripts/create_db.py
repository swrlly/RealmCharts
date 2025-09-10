import sqlite3

database = "../data/players.db"
create_players = """CREATE TABLE IF NOT EXISTS playersOnline (
    timestamp INTEGER PRIMARY KEY NOT NULL,
    players INT);"""

create_maintenance = """CREATE TABLE IF NOT EXISTS maintenance (
    timestamp INTEGER PRIMARY KEY NOT NULL,
    online BOOLEAN CHECK (online IN (0, 1)),
    estimated_time INT);"""

try:
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(create_players)
        conn.commit()
        cursor.execute(create_maintenance)
        conn.commit()
        cursor.close()

except sqlite3.OperationalError as e:
    print(e)

print("success")