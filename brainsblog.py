import requests
import re
import unicodedata
from bs4 import BeautifulSoup
from datetime import datetime


def brainsblog_rss(url):
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74"
    }
    global article_list
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


def briansblog_text(url):
    text = ""
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        for item in soup.find_all("div", {"class": "entry-content"}):
            text = text + str(item.find_all(text=True))
            return text
    except Exception as e:
        print("The Brains Blog - The scraping job failed. See exception: ")
        print(e)


def clean_text(text):
    cleaned_text = re.sub(r"\\x..", "", text).strip()
    cleaned_text = re.sub(
        "[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\('\"’”“–]", "", cleaned_text
    )
    return cleaned_text


def scrapping(url):
    brainsblog_rss(url)
    for link in article_list:
        text = briansblog_text(link["link"])
        text = clean_text(text)
        link["text"] = text
    print(article_list)
    return article_list


"""
url = "https://philosophyofbrains.com/feed"
scrapping(url)
"""