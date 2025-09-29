from flask import Flask, g, request, render_template, stream_template
from werkzeug.middleware.proxy_fix import ProxyFix
import platform
import sqlite3
import time
import json
import gzip

css_version = str(int(time.time()))
app = Flask(__name__)

@app.route("/api/forecast-performance", methods = ["GET"])
def forecast_performance():
    cur = get_db().cursor()
    cur.execute("""SELECT 
    CASE
        WHEN horizon_steps = 12 THEN "1hr"
        WHEN horizon_steps = 72 THEN "6hr"
        WHEN horizon_steps = 144 THEN "12hr"
        ELSE "24hr"
    END AS horizon,
    ROUND(AVG(mean_absolute_error), 0) AS MAE,
    ROUND(100 * (1 - AVG(mean_absolute_percentage_error)), 1) AS MAPE,
    SUM(
        CASE 
        WHEN actual_value NOT NULL THEN 1
        ELSE 0 END
    ) as n_obs
    FROM forecastHorizon
    WHERE timestamp >= unixepoch() - 2 * 24 * 60 * 60
    AND params = "288:8 2016:7,1 strend ar2"
    GROUP BY horizon
    ORDER BY horizon_steps;
        """)
    results = json.dumps(cur.fetchall())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/reviews", methods = ["GET"])
def review_proportions():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM reviewsGrouped;")
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
    cur.execute("SELECT timestamp, CASE WHEN trustworthiness = 0 THEN null ELSE players END FROM playersCleaned;")
    results = json.dumps(cur.fetchall())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/players-now", methods = ["GET"])
def players_online_now():
    # get latest playercount
    cur = get_db().cursor()
    cur.execute("""SELECT timestamp, 
        CASE WHEN trustworthiness = 0 THEN null ELSE players END 
        FROM playersCleaned 
        WHERE timestamp = (SELECT max(timestamp) FROM playersCleaned);""")
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
        cur.execute("SELECT trustworthiness, online FROM playersGrouped WHERE timestamp = (SELECT max(timestamp) FROM playersGrouped);")
        results = cur.fetchone()
        # if data is currently untrustworthy (bugged + 1h after bugged/maintenance), do not display forecast
        if results[0] < 0.2 or results[1] == 0:
            results = json.dumps([])
        else:
            cur.execute("SELECT * FROM forecast where timestamp >= unixepoch() - 300;")
            results = json.dumps([i[1:-1] for i in cur.fetchall()])
    else:
        cur.execute("SELECT * FROM maintenanceForecast where timestamp >= unixepoch() - 300;")
        results = json.dumps([i[1:] for i in cur.fetchall()])
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

# compress data requests
@app.after_request
def compress(response):
    if response.is_json == True:
        data = gzip.compress(response.get_data(), compresslevel = 3)
        response.set_data(data)
        response.headers["Content-Length"] = len(data)
        response.headers["Content-Encoding"]= "gzip"
    return response

@app.route("/")
async def index():
    return render_template("index.html", css_version = css_version)

@app.route("/about")
async def about():
    return render_template("about.html", css_version = css_version)

@app.route("/robots.txt")
async def robots():
    return app.send_static_file("robots.txt")

@app.route("/favicon.ico")
async def favicon():
    return app.send_static_file("images/favicon.ico")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("../datacollection/data/players.db")
    return db

app.config["SERVER_NAME"] = "localhost:8001" if platform.system() == "Windows" else "realmcharts.swrlly.com"