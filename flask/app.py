from flask import Flask, g, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
import time
import json


css_version = str(int(time.time()))
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", css_version = css_version)

@app.route("/api/playercount")
def playerCount():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM playersOnline")
    results = cur.fetchall()
    results = json.dumps(results)
    return app.response_class(response = results, status = 200, mimetype = "application/json")

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("../datacollection/data/players.db")
    return db

@app.teardown_appcontext
def closeConnection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

app.config["SERVER_NAME"] = "localhost:8001"
#app.config["SERVER_NAME"] = "rotmg.swrlly.com"