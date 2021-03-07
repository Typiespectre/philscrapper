import requests
from bs4 import BeautifulSoup
from datetime import datetime


def brainsblog_rss(url):
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74"
    }
    article_list = []
    try:
        r = requests.get(url, headers=request_headers)
        soup = BeautifulSoup(r.content, "xml")
        articles = soup.find_all("item")
        for a in articles:
            title = a.find("title").text.replace("\xa0", "")
            link = a.find("link").text
            time = a.find("pubDate").text.replace("+0000", "")
            name = "The Brains Blog"

            dateFormatter = "%a, %d %b %Y %H:%M:%S "
            dt = datetime.strptime(time, dateFormatter)
            published = dt.strftime("%Y-%m-%d")

            article = {
                "name": name,
                "title": title,
                "link": link,
                "published": published,
            }
            article_list.append(article)
        return article_list
    except Exception as e:
        print("The Brains Blog - The scraping job failed. See exception: ")
        print(e)