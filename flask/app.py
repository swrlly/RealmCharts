from flask import Flask, g, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import platform
import sqlite3
import time
import json


css_version = str(int(time.time()))
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", css_version = css_version)

@app.route("/api/review-proportions", methods = ["GET"])
def review_proportions():
    cur = get_db().cursor()
    cur.execute("""-- create cumsum of reviews
WITH added_date AS (
	SELECT 
		timestamp_created,
		voted_up,
		SUM(voted_up) OVER (ORDER BY timestamp_created) AS total_votes_up,
		ROW_NUMBER() OVER (ORDER BY timestamp_created) AS total_votes,
		strftime("%Y", DATETIME(timestamp_created, "unixepoch")) AS year,
		strftime("%m", DATETIME(timestamp_created, "unixepoch")) AS month,
		strftime("%d", DATETIME(timestamp_created, "unixepoch")) AS day
	FROM steamReviews
	ORDER BY timestamp_created ASC)

-- create statistics by day
SELECT 
	year || "-" || month || "-" || day as date,
	COUNT(timestamp_created) as num_reviews,
	ROUND(MAX(total_votes_up)*1.0 / MAX(total_votes), 4) as proportion_positive -- max gets EoD statistics; most updated.
FROM added_date
GROUP BY year, month, day;""")
    results = json.dumps(cur.fetchall())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/playercount", methods = ["GET"])
def player_count():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM playersOnline")
    results = json.dumps(cur.fetchall())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/players-now", methods = ["GET"])
def players_online_now():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM playersOnline WHERE timestamp = (SELECT max(timestamp) FROM playersOnline);")
    results = json.dumps(cur.fetchone())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/players-last-week", methods = ["GET"])
def players_last_week():
    cur = get_db().cursor()
    cur.execute("""
    SELECT 
        timestamp,
        players,
        (SELECT MAX(timestamp) FROM playersOnline) - 10080 - timestamp AS difference
    FROM playersOnline
    ORDER BY ABS(difference)
    LIMIT 1;""")
    results = json.dumps(cur.fetchone())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/is-game-online", methods = ["GET"])
def is_game_up():
    cur = get_db().cursor()
    cur.execute("SELECT timestamp, online FROM maintenance WHERE timestamp = (SELECT max(timestamp) FROM maintenance);")
    results = cur.fetchone()
    results = json.dumps({"last_checked": time.time() - results[0], "online": results[1]})
    return app.response_class(response = results, status = 200, mimetype = "text/plain")

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("../datacollection/data/players.db")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

app.config["SERVER_NAME"] = "localhost:8001" if platform.system() == "Windows" else "realmcharts.swrlly.com"