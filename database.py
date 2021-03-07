import sqlite3
import datetime
from philosophynews import philosophynews_rss
from guardian import guardian_rss
from apa import apa_rss
from brainsblog import brainsblog_rss
from warpweftandway import warfweftandway_rss

scrap_list = {
    "pn": philosophynews_rss("http://feeds.feedburner.com/philosophynews/jcFI"),
    "gd": guardian_rss("https://www.theguardian.com/world/philosophy/rss"),
    "ap": apa_rss("http://blog.apaonline.org/feed/"),
    # "bb": brainsblog_rss("https://philosophyofbrains.com/feed"),
    "ww": warfweftandway_rss("http://warpweftandway.com/feed/"),
}

conn = sqlite3.connect("philscrapper.db", isolation_level=None)
c = conn.cursor()
c.execute(
    "CREATE TABLE IF NOT EXISTS philscrapper (name text not null, title text not null, link text not null, published text not null, unique (name, title, link, published))"
)


for link in scrap_list.values():
    for i in link:
        c.execute(
            "INSERT OR REPLACE INTO philscrapper(name, title, link, published) VALUES(?,?,?,?)",
            (i["name"], i["title"], i["link"], i["published"]),
        )


c.execute(
    "SELECT * FROM philscrapper WHERE published BETWEEN datetime(date('now','localtime'), '-7 days') AND date('now','localtime') ORDER BY published DESC"
)

rows = c.fetchall()


def import_DB():
    return rows


with conn:
    with open("dump.sql", "w", -1, "utf-8") as f:
        for line in conn.iterdump():
            f.write("%s\n" % line)

# c.execute("DELETE FROM philscrapper")
# c.execute("DELETE FROM philscrapper WHERE published BETWEEN '2020-08-31' AND '2021-01-29'")
# conn.commit()
conn.close()
