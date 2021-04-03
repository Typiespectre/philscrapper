# import sqlite3
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker

from sites.apa import apa_scrapping
from sites.brainsblog import brainsblog_scrapping
from sites.warpweftandway import warpweftandway_scrapping
from sites.aeon import aeon_scrapping

"""
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
"""
timezone(timedelta(hours=9))

scrap_list = [
    apa_scrapping("http://blog.apaonline.org/feed/"),
    # brainsblog_scrapping("https://philosophyofbrains.com/feed"),
    # warpweftandway_scrapping("http://warpweftandway.com/feed/"),
    # aeon_scrapping("https://aeon.co/feed.rss"),
]


def import_DB():
    engine = create_engine("sqlite:///philDB.db", echo=True)
    Base = declarative_base()

    class Article(Base):
        __tablename__ = "Articles"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)
        title = Column(String, nullable=False)
        link = Column(String, nullable=False)
        published = Column(String, nullable=False)
        tags = Column(String, nullable=False)

        def __init__(self, name, title, link, published, tags):
            self.name = name
            self.title = title
            self.link = link
            self.published = published
            self.tags = tags

        def __repr__(self):
            return "<Article('%s','%s','%s','%s','%s')>" % (
                self.name,
                self.title,
                self.link,
                self.published,
                self.tags,
            )

        def as_dict(self):
            return {x.name: getattr(self, x.name) for x in self.__table__.columns}

        @classmethod
        def get_or_create(cls, name, title, link, published, tags):
            exists = session.query(Article.id).filter_by(link=link).scalar() is not None
            if exists:
                return session.query(Article).filter_by(link=link).first()
            return cls(
                name=name, title=title, link=link, published=published, tags=tags
            )

    Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    for elements in scrap_list:
        for i in elements:
            db_article = Article(
                i["name"], i["title"], i["link"], i["published"], i["tags"]
            )
            try:
                article = Article.get_or_create(
                    name=i["name"],
                    title=i["title"],
                    link=i["link"],
                    published=i["published"],
                    tags=i["tags"],
                )
                if article not in session:
                    session.add(article)
                session.commit()
            except Exception as e:
                print("\nDatabase job failed. See exception:")
                print(e)
                session.rollback()

    # raw SQL문을 쓰기 싫지만... 지금은 마땅한 생각이 나지 않는다.
    result = engine.execute(
        "SELECT * FROM Articles WHERE published BETWEEN datetime(date('now','localtime'), '-7 days') AND date('now','localtime') ORDER BY published DESC"
    )
    rows = result.fetchall()
    session.close()
    return rows


def check_DB(article_link):
    engine = create_engine("sqlite:///philDB.db", echo=True)
    Base = declarative_base()

    class Article(Base):
        __tablename__ = "Articles"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)
        title = Column(String, nullable=False)
        link = Column(String, nullable=False)
        published = Column(String, nullable=False)
        tags = Column(String, nullable=False)

    Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
