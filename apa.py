import requests
import re
import unicodedata
from bs4 import BeautifulSoup
from datetime import datetime

# 사이트의 rss feed에서 갱신되는 기사의 제목, 링크, 시간에 사이트 이름을 붙여서 가져온다.
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


# 갱신된 기사들의 text 전문을 가져온다.
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


# 갱신된 기사의 전문에 포함된 특수문자들을 모두 제거한다. (지금은 크게 쓸모 없는 기능)
def clean_text(text):
    cleaned_text = text.strip().replace("\n", "")
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
def apa_scrapping(url):
    apa_rss(url)
    for key in article_list:
        text = apa_text(key["link"])
        text = clean_text(text)
        key["text"] = text
        key["tags"] = tagging(key["text"])
        del key["text"]
    return article_list
