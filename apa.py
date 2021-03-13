import requests
import re
import unicodedata
from bs4 import BeautifulSoup
from datetime import datetime


def apa_rss(url):
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
            name = "APA"

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
        print("APA - The scraping job failed. See exception: ")
        print(e)


def apa_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74"
    }
    text = ""
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        for item in soup.find_all("div", {"class": "tdb-block-inner td-fix-index"}):
            # 필요한 element 내부의 text만 가져와서 text에 합한다.
            element_list = ["p"]
            text_list = [
                t for t in soup.find_all(text=True) if t.parent.name in element_list
            ]
            text = "".join(text_list)
            return text
    except Exception as e:
        print("APA - The scraping job failed. See exception: ")
        print(e)


def clean_text(text):
    cleaned_text = text.strip().replace("\n", "")
    cleaned_text = re.sub(
        "[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\('\"’”“–]", "", cleaned_text
    )
    return cleaned_text


phil_types = ["Aesthetics", "Epistemology", "Ethics", "Logic", "Metaphysics", "Minds"]


def tagging(text):
    tags = []
    for types in phil_types:
        if re.search(types[:5], text, re.IGNORECASE):
            tags.append(types)
    if len(tags) == 0:
        tags.append("others")
    tag = ", ".join(tags)
    return tag


def apa_scrapping(url):
    apa_rss(url)
    for key in article_list:
        text = apa_text(key["link"])
        text = clean_text(text)
        key["text"] = text
        key["tags"] = tagging(key["text"])
        del key["text"]
    return article_list
