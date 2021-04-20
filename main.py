from flask import Flask, render_template, request
from database import make_DB, import_DB, rank_import_DB
from apscheduler.schedulers.background import BackgroundScheduler


def updateDB():
    make_DB()


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
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(updateDB, "interval", hours=12)
    scheduler.start()
    app.run()
