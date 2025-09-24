from flask import Flask, g, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import platform
import sqlite3
import time
import json

css_version = str(int(time.time()))
app = Flask(__name__)

# API logic
@app.route("/api/reviews", methods = ["GET"])
def review_proportions():
    # get propotion of positive reviews over entire game history
    # send sums for downstream average calculation in JS because average over averages because days with less reviews (samples) will affect statistics more strongly
    # averaging once over the viewing window weighs each review's statistics equally
    cur = get_db().cursor()
    cur.execute("""-- create cumsum of reviews
    -- recommendation_id 61328679 is botting playtime with online botter
    WITH added_date AS (
        SELECT 
            timestamp_created,
            voted_up,
            playtime_last_two_weeks,
            playtime_forever,
            playtime_at_review,
            SUM(voted_up) OVER (ORDER BY timestamp_created) AS total_votes_up,
            ROW_NUMBER() OVER (ORDER BY timestamp_created) AS total_votes,
            strftime("%Y", DATETIME(timestamp_created, "unixepoch")) AS year,
            strftime("%m", DATETIME(timestamp_created, "unixepoch")) AS month,
            strftime("%d", DATETIME(timestamp_created, "unixepoch")) AS day
        FROM steamReviews)

    -- create statistics by day
    SELECT 
        unixepoch(year || "-" || month || "-" || day) as date,
        COUNT(timestamp_created) as daily_total_reviews,
        ROUND(MAX(total_votes_up)*1.0 / MAX(total_votes), 5) as total_proportion_positive, -- max gets EoD statistics; most updated.
        SUM(playtime_last_two_weeks) as daily_total_playtime_last_two_weeks,
        SUM(voted_up) as daily_total_votes_up, 
        SUM(playtime_at_review) as daily_total_playtime_at_review,
        SUM(playtime_forever) as daily_total_playtime_forever
    FROM added_date
    GROUP BY year, month, day;""")
    results = json.dumps(cur.fetchall())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/reviews-last-scraped", methods = ["GET"])
def steam_last_scraped():
    # get time steam reviews was last scraped
    with open("../datacollection/data/reviews_last_scraped", "r") as f:
        time = f.read().strip()
        return app.response_class(response = time, status = 200, mimetype = "application/json")

@app.route("/api/playercount", methods = ["GET"])
def player_count():
    # get all player counts collected, minute granularity
    cur = get_db().cursor()
    cur.execute("SELECT * FROM playersCleaned")
    results = json.dumps(cur.fetchall())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/players-now", methods = ["GET"])
def players_online_now():
    # get latest playercount
    cur = get_db().cursor()
    cur.execute("SELECT * FROM playersCleaned WHERE timestamp = (SELECT max(timestamp) FROM playersCleaned);")
    results = json.dumps(cur.fetchone())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/players-last-week", methods = ["GET"])
def players_last_week():
    # get last week's playercount vs. latest scraped time
    cur = get_db().cursor()
    cur.execute("""
    SELECT 
        timestamp,
        players,
        (SELECT MAX(timestamp) FROM playersCleaned) - 60 * 60 * 24 * 7 - timestamp AS difference
    FROM playersCleaned
    ORDER BY ABS(difference)
    LIMIT 1;""")
    results = json.dumps(cur.fetchone())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/is-game-online", methods = ["GET"])
def is_game_up():
    # get latest game status with time last checked
    cur = get_db().cursor()
    cur.execute("SELECT timestamp, online FROM maintenance WHERE timestamp = (SELECT max(timestamp) FROM maintenance);")
    results = cur.fetchone()
    cur.close()
    results = json.dumps({"last_checked": time.time() - results[0], "online": results[1]})
    return app.response_class(response = results, status = 200, mimetype = "text/plain")

@app.route("/api/forecast", methods = ["GET"])
def get_forecast():
    cur = get_db().cursor()    
    cur.execute("SELECT online FROM maintenance WHERE timestamp = (SELECT max(timestamp) FROM maintenance);")
    results = cur.fetchone()
    if results[0] == 1:
        cur.execute("SELECT trustworthiness FROM playersGrouped WHERE timestamp = (SELECT max(timestamp) FROM playersGrouped);")
        results = cur.fetchone()
        # if bugged data, do not display forecast
        if results[0] < 0.2:
            results = json.dumps([])
        else:
            cur.execute("SELECT * FROM forecast where timestamp >= unixepoch() - 300;")
            results = json.dumps(cur.fetchall())
    else:
        cur.execute("SELECT * FROM maintenanceForecast where timestamp >= unixepoch() - 300;")
        results = json.dumps(cur.fetchall())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template("index.html", css_version = css_version)

@app.route("/about")
def about():
    return render_template("about.html", css_version = css_version)

@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("../datacollection/data/players.db")
    return db

app.config["SERVER_NAME"] = "localhost:8001" if platform.system() == "Windows" else "realmcharts.swrlly.com"