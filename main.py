from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.sql.functions import count
from database import (
    make_DB,
    import_DB,
    rank_import_DB,
    article_DB,
    add_comment,
    comment_DB,
    comment_count,
)
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
app.secret_key = "cGhpbHNjcmFwcGVy"


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


@app.route("/article/<int:id>/")
def article(id):
    rows = article_DB(id)
    comments = comment_DB(id)
    return render_template("article.html", rows=rows, comments=comments)


@app.route("/comment/<int:article_id>", methods=("POST",))
def comment(article_id):
    error = None
    now = datetime.datetime.now()

    articleID = int(article_id)
    content = request.form["commentContent"]
    userid = request.form["userid"]
    created = now.strftime("%Y-%m-%d %H:%M:%S")

    if len(content) == 0 or len(userid) == 0:
        error = "Please fill in the blanks."
        flash(error)
    else:
        add_comment(articleID, content, userid, created)
    return redirect(url_for("article", id=article_id))


if __name__ == "__main__":
    # app.run("0.0.0.0", port=80)
    make_DB()
    app.run()
    atexit.register(lambda: scheduler.shutdown())
