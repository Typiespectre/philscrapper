from flask import Flask, render_template, request
from database import make_DB, import_DB, rank_import_DB
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import math
import datetime


def updateDB():
    make_DB()


scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(updateDB, "interval", hours=12)
scheduler.start()


app = Flask("philscrapper")


@app.route("/")
def home():
    rows = import_DB()
    page = request.args.get("page", 1, type=int)

    total = rows.count()
    last_page_num = math.ceil(total / 10)
    rows = rows.slice((page - 1) * 10, page * 10).all()

    page_prev_num = (page - 1) * 10 + 1
    page_num = page * 10

    now = datetime.datetime.now()
    update = now.strftime("%Y-%m-%d")

    return render_template(
        "home.html",
        rows=rows,
        page=page,
        last_page_num=last_page_num,
        page_prev_num=page_prev_num,
        page_num=page_num,
        total=total,
        update=update,
    )


@app.route("/rank")
def rank():
    rows = rank_import_DB()

    now = datetime.datetime.now()
    update = now.strftime("%Y-%m-%d")

    return render_template("rank.html", rows=rows, update=update)


if __name__ == "__main__":
    # app.run("0.0.0.0", port=80)
    make_DB()
    app.run()
    atexit.register(lambda: scheduler.shutdown())
