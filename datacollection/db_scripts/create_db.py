import sqlite3

database = "../data/players.db"
create_players = """CREATE TABLE IF NOT EXISTS playersOnline (
    timestamp INTEGER PRIMARY KEY NOT NULL,
    players INT);"""

create_maintenance = """CREATE TABLE IF NOT EXISTS maintenance (
    timestamp INTEGER PRIMARY KEY NOT NULL,
    online BOOLEAN CHECK (online IN (0, 1)),
    estimated_time INT);"""

create_steam_reviews = """CREATE TABLE IF NOT EXISTS steamReviews (
    recommendation_id INTEGER PRIMARY KEY NOT NULL,
    author_id INT,
    playtime_forever INT,
    playtime_last_two_weeks INT,
    playtime_at_review INT,
    last_played INT,
    language TEXT,
    review TEXT,
    timestamp_created INT,
    timestamp_updated INT,
    voted_up INT,
    votes_up INT,
    votes_funny INT,
    comment_count INT
);"""

try:
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(create_players)
        conn.commit()
        cursor.execute(create_maintenance)
        conn.commit()
        #cursor.execute("DROP TABLE steamReviews")
        cursor.execute(create_steam_reviews)
        conn.commit()
        cursor.close()

except sqlite3.OperationalError as e:
    print(e)

print("success")