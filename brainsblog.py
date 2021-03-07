import requests
import re
import unicodedata
from bs4 import BeautifulSoup
from datetime import datetime

# 사이트의 rss feed에서 갱신되는 기사의 제목, 링크, 시간에 사이트 이름을 붙여서 가져온다.
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


# 갱신된 기사의 text 전문을 가져온다.
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


# 갱신된 기사의 전문에 포함된 특수문자들을 모두 제거한다.
def clean_text(text):
    cleaned_text = re.sub(r"\\x..", "", text).strip()
    cleaned_text = re.sub(
        "[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\('\"’”“–]", "", cleaned_text
    )
    return cleaned_text


phil_types = ["Aesthetics", "Epistemology", "Ethics", "Logic", "Metaphysics", "Minds"]

# 전문 중 phil_types의 문자열의 일부에 맞는 단어가 있을 경우 tag를 한다.
def tagging(text):
    tags = []
    for types in phil_types:
        if re.search(types[:5], text, re.IGNORECASE):
            tags.append(types)
    if len(tags) == 0:
        tags.append("others")
    tag = ", ".join(tags)
    return tag


# 위 함수들을 하나로 통합한 중심 함수!
# rss feed로 갱신된 기사를 스크래핑하는 과정을 모두 포함하는 함수.
def brainsblog_scrapping(url):
    brainsblog_rss(url)
    for link in article_list:
        text = briansblog_text(link["link"])
        text = clean_text(text)
        link["text"] = text
        link["tags"] = tagging(link["text"])
        del link["text"]
    return article_list


url = "https://philosophyofbrains.com/feed"
brainsblog_scrapping(url)
