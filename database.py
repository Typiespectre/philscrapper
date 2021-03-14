import sqlite3
import datetime
from sites.philosophynews import philosophynews_rss
from sites.guardian import guardian_rss
from sites.apa import apa_scrapping
from sites.brainsblog import brainsblog_scrapping
from sites.warpweftandway import warfweftandway_scrapping


def import_DB():

    scrap_list = {
        # "pn": philosophynews_rss("http://feeds.feedburner.com/philosophynews/jcFI"),
        # "gd": guardian_rss("https://www.theguardian.com/world/philosophy/rss"),
        "ap": apa_scrapping("http://blog.apaonline.org/feed/"),
        "bb": brainsblog_scrapping("https://philosophyofbrains.com/feed"),
        "ww": warfweftandway_scrapping("http://warpweftandway.com/feed/"),
    }

    print("Connecting to Database...")
    conn = sqlite3.connect("philscrapper.db", isolation_level=None)
    c = conn.cursor()

    c.execute(
        "CREATE TABLE IF NOT EXISTS philscrapper (name text NOT NULL, title text NOT NULL, link text NOT NULL, published text NOT NULL, tags text NOT NULL, unique (name, title, link, published))"
    )

    for key in scrap_list.values():
        for i in key:

            c.execute(
                "INSERT OR REPLACE INTO philscrapper(name, title, link, published, tags) VALUES(?,?,?,?,?)",
                (i["name"], i["title"], i["link"], i["published"], i["tags"]),
            )

    c.execute(
        "SELECT * FROM philscrapper WHERE published BETWEEN datetime(date('now','localtime'), '-7 days') AND date('now','localtime') ORDER BY published DESC"
    )

    rows = c.fetchall()

    with conn:
        with open("dump.sql", "w", -1, "utf-8") as f:
            for line in conn.iterdump():
                f.write("%s\n" % line)

    conn.commit()
    conn.close()
    print("Connect Database Finished!")
    return rows