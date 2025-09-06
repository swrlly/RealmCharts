from flask import Flask, g, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

app.config["SERVER_NAME"] = "rotmg.swrlly.com"