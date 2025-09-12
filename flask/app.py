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

@app.route("/api/playercount", methods = ["GET"])
def player_count():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM playersOnline")
    results = json.dumps(cur.fetchall())
    cur.close()
    return app.response_class(response = results, status = 200, mimetype = "application/json")

@app.route("/api/online", methods = ["GET"])
def is_game_up():
    cur = get_db().cursor()
    cur.execute("SELECT timestamp, online FROM maintenance WHERE timestamp = (SELECT max(timestamp) FROM maintenance);")
    results = cur.fetchone()
    results = json.dumps({"last_checked": time.time() - results[0], "online": results[1]})
    print(results)
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