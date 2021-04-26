from flask import Flask, render_template, request
from database import make_DB, import_DB, rank_import_DB
from apscheduler.schedulers.background import BackgroundScheduler
import atexit


def updateDB():
    make_DB()


scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(updateDB, "interval", hours=12)
scheduler.start()


app = Flask("philscrapper")


@app.route("/")
def home():
    rows = import_DB()
    return render_template("home.html", rows=rows)


@app.route("/find")
def find():
    rows = rank_import_DB()
    return render_template("find.html", rows=rows)


if __name__ == "__main__":
    app.run("0.0.0.0", port=80)
    atexit.register(lambda: scheduler.shutdown())
