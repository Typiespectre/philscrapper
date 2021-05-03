# import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///data/philDB.db?check_same_thread=False")
Base = declarative_base()


class Article(Base):
    __tablename__ = "Articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False)
    published = Column(String, nullable=False)
    tags = Column(String, nullable=False)
    rank = Column(Integer)

    def __init__(self, name, title, link, published, tags, rank):
        self.name = name
        self.title = title
        self.link = link
        self.published = published
        self.tags = tags
        self.rank = rank

    def __repr__(self):
        return "<Article('%s','%s','%s','%s','%s','%s')>" % (
            self.name,
            self.title,
            self.link,
            self.published,
            self.tags,
            self.rank,
        )

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    @classmethod
    def get_or_create(cls, name, title, link, published, tags, rank):
        exists = session.query(Article.id).filter_by(link=link).scalar() is not None
        if exists:
            return session.query(Article).filter_by(link=link).first()
        return cls(
            name=name,
            title=title,
            link=link,
            published=published,
            tags=tags,
            rank=rank,
        )


Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


def make_DB():

    from apa import apa_scrapping
    from brainsblog import brainsblog_scrapping
    from warpweftandway import warpweftandway_scrapping
    from aeon import aeon_scrapping
    from sep import sep_scrapping

    # from wiley import wiley_scrapping

    # wiley rss feed 스크랩에 사용됨.
    from datetime import datetime, timedelta

    wiley_now = datetime.today().strftime("%Y%m%d")
    wiley_months_ago = (datetime.today() - timedelta(weeks=1)).strftime("%Y%m%d")

    scrap_list = [
        apa_scrapping("http://blog.apaonline.org/feed/"),
        brainsblog_scrapping("https://philosophyofbrains.com/feed"),
        warpweftandway_scrapping("http://warpweftandway.com/feed/"),
        aeon_scrapping("https://aeon.co/feed.rss"),
        sep_scrapping("https://plato.stanford.edu/rss/sep.xml"),
        # wiley_scrapping(
        #    f"https://onlinelibrary.wiley.com/action/showFeed?ui=0&mi=1slcofg&type=search&feed=rss&query=%2526Ppub%253D{wiley_months_ago}-{wiley_now}%2526content%253DarticlesChapters%2526countTerms%253Dtrue%2526field1%253DAllField%2526target%253Ddefault%2526text1%253Dphilosophy"
        # ),
    ]

    for elements in scrap_list:
        for i in elements:
            try:
                article = Article.get_or_create(
                    name=i["name"],
                    title=i["title"],
                    link=i["link"],
                    published=i["published"],
                    tags=i["tags"],
                    rank=i["rank"],
                )
                if article not in session:
                    session.add(article)
                session.commit()
            except Exception as e:
                print("\nDatabase job failed. See exception:")
                print(e)
                session.rollback()


def check_DB(article_link):
    exists = session.query(Article.id).filter_by(link=article_link).scalar() is not None
    if not exists:
        return article_link


def import_DB():
    from datetime import datetime, timedelta, timezone

    # timezone(timedelta(hours=9))
    now = datetime.today().strftime("%Y-%m-%d")
    weeks_ago = (datetime.today() - timedelta(weeks=1)).strftime("%Y-%m-%d")

    results = (
        session.query(
            Article.name,
            Article.link,
            Article.title,
            Article.tags,
            Article.published,
        ).order_by(Article.published.desc())
        # .limit(10)
        # .filter(
        #    Article.published.between(weeks_ago, now),
        # )
        # .filter(~Article.tags.in_(["others"]))
    )
    rows = results
    # session.close()
    return rows


def rank_import_DB():
    results = (
        session.query(
            Article.name,
            Article.link,
            Article.title,
            Article.tags,
            Article.published,
        )
        .filter(Article.rank == 1)
        .filter(~Article.tags.in_(["others"]))
        .distinct(Article.name)
        .group_by(Article.name)
        .order_by(Article.name)
        .order_by(Article.published.desc())
        .all()
    )
    rows = results
    session.close()
    return rows