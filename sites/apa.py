import requests
import re
import unicodedata
from bs4 import BeautifulSoup
from datetime import datetime

# 사이트의 rss feed에서 갱신되는 기사의 제목, 링크, 시간에 사이트 이름을 붙여서 가져온다.
def apa_rss(url):
    print("\nConnecting to APA rss feed...")
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
        print("APA (rss feed) - The scraping job failed. See exception: ")
        print(e)


# 갱신된 기사들의 text 전문을 가져온다.
def apa_text(url, n, list_len):
    print(f"\nscrapping article text... {n}/{list_len}")
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
        print("APA (scrapping) - The scraping job failed. See exception: ")
        print(e)


# 갱신된 기사의 전문에 포함된 특수문자들을 모두 제거한다. (아직은 딱히 쓸모 없는 기능)
def clean_text(text):
    cleaned_text = text.strip().replace("\n", "")
    cleaned_text = re.sub(
        "[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\('\"’”“–]", "", cleaned_text
    )
    cleaned_text = re.sub(r"[0-9]", " ", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text, flags=re.I)
    cleaned_text = re.sub(r"^\s+", " ", cleaned_text)
    cleaned_text = re.sub(r"\s+$", " ", cleaned_text)
    cleaned_text = re.sub(r"\s+[a-zA-Z]\s+", " ", cleaned_text)
    return cleaned_text


# 전문에서 phil_types의 keywords 중 문자열의 일부에 맞는 단어가 있을 경우 tag를 한다.
# keywords 참조 : https://m.blog.naver.com/PostView.nhn?blogId=sgjjojo&logNo=221184479000&proxyReferer=https:%2F%2Fwww.google.com%2F
Aesthetics = ["Aesthetics"]
Epistemology = [
    "Epistemology",
    "causality",
    "freewill",
    "determinism",
    "teleology",
    "anthropology",
]
Ethics = ["Ethics", "moral", "political"]
Logic = [
    "Logic",
    "deduction",
    "induction",
    "dialectic",
    "formal",
    "mathematical",
    "demonstration",
    "analogy",
]
Metaphysics = [
    "Metaphysics",
    "methodology",
    "ontology",
    "cosmology",
]
Eastern = ["Eastern", "chinese", "japan", "korean", "buddhist", "indian"]
Minds = ["Minds", "psychology", "physicalism", "machine", "consciousness", "mentality"]

phil_types = [Aesthetics, Epistemology, Ethics, Logic, Metaphysics, Eastern, Minds]


def tagging(text):
    tags = []
    words = []
    words_count = {}
    for types in phil_types:
        for keywords in types:
            """
            if re.search(keywords[:5], text, re.IGNORECASE):
                if types[0] not in tags:
                    tags.append(types[0])
            """
            word_found = re.findall(keywords[:5], text, re.IGNORECASE)
            if len(word_found) != 0:
                words += word_found
    if len(words) == 0:
        words.append("others")
    # text 내에서 발견된 keyword의 종류와 개수 찾기
    for i in words:
        i = i.lower()
        try:
            words_count[i] += 1
        except:
            words_count[i] = 1
    # text 내 전체 keyword의 평균 개수 미만 keyword는 포함하지 않음
    keyword_average = sum(words_count.values()) // len(words_count)
    for keys, values in words_count.items():
        if values > keyword_average:
            for types in phil_types:
                for keywords in types:
                    if keys == keywords[:5]:
                        tags.append(types[0])
    if len(tags) == 0:
        tags.append("others")
    # tag 중복 제거
    tag_set = set(tags)
    tag_list = list(tag_set)
    tag = ", ".join(tag_list)
    return tag


# 위 함수들을 하나로 통합한 중심 함수!
# rss feed로 갱신된 기사를 스크래핑하는 과정을 모두 포함하는 함수.
def apa_scrapping(url):
    apa_rss(url)
    n = 1
    for key in article_list:
        text = apa_text(key["link"], n, len(article_list))
        text = clean_text(text)
        key["text"] = text
        key["tags"] = tagging(key["text"])
        del key["text"]
        n += 1
    print("\nScrapping APA Finished!\n")
    return article_list