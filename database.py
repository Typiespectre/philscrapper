import sqlite3
import datetime
from sites.philosophynews import philosophynews_rss
from sites.guardian import guardian_rss
from sites.apa import apa_scrapping
from sites.brainsblog import brainsblog_scrapping
from sites.warpweftandway import warpweftandway_scrapping

scrap_list = [
    apa_scrapping("http://blog.apaonline.org/feed/"),
    brainsblog_scrapping("https://philosophyofbrains.com/feed"),
    warpweftandway_scrapping("http://warpweftandway.com/feed/"),
]
# philosophynews_rss("http://feeds.feedburner.com/philosophynews/jcFI")
# guardian_rss("https://www.theguardian.com/world/philosophy/rss")


def import_DB():
    print("\nConnecting to Database...\n")

    conn = sqlite3.connect("philscrapper.db", isolation_level=None)
    c = conn.cursor()

    c.execute(
        "CREATE TABLE IF NOT EXISTS philscrapper (name text NOT NULL, title text NOT NULL, link text NOT NULL, published text NOT NULL, tags text NOT NULL, unique (name, title, link, published))"
    )

    for elements in scrap_list:
        for i in elements:

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
    print("\nDatabase Task Finished!\n")
    return rows