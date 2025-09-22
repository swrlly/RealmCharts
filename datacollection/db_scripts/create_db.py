import sqlite3

database = "../data/players.db"
create_players = """CREATE TABLE IF NOT EXISTS playersOnline (
    timestamp INTEGER PRIMARY KEY NOT NULL,
    players INT);"""

# trustworthiness = 1 means real data
# 0 means
#  - sequential same counts (bugged from data source)
#  - actual missing data (program down)
create_players_cleaned = """CREATE TABLE IF NOT EXISTS playersCleaned (
    timestamp INTEGER PRIMARY KEY NOT NULL,
    players INT,
    trustworthiness INT);"""

create_players_grouped = """CREATE TABLE IF NOT EXISTS playersGrouped (
    timestamp INTEGER PRIMARY KEY NOT NULL,
    players REAL,
    online REAL,
    trustworthiness REAL);"""

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
    comment_count INT,
    cursor TEXT
);"""

create_forecast = """CREATE TABLE IF NOT EXISTS forecast (
    idx INTEGER PRIMARY KEY NOT NULL,
    timestamp INTEGER NOT NULL,
    forecast_mean REAL,
    one_sd_lower REAL,
    one_sd_upper REAL,
    two_sd_lower REAL,
    two_sd_upper REAL,
    three_sd_lower REAL,
    three_sd_upper REAL
);"""

try:
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(create_players)
        conn.commit()
        cursor.execute(create_players_cleaned)
        conn.commit()
        cursor.execute(create_players_grouped)
        conn.commit()
        cursor.execute(create_maintenance)
        conn.commit()
        cursor.execute(create_steam_reviews)
        conn.commit()
        cursor.execute(create_forecast)
        conn.commit()
        cursor.close()

except sqlite3.OperationalError as e:
    print(e)

print("success")
