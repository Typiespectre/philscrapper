import requests
from bs4 import BeautifulSoup
from datetime import datetime
from database import check_DB
from functions.cleaning import clean_text
from functions.tagging import tagging

# 사이트의 rss feed에서 갱신되는 기사의 제목, 링크, 시간에 사이트 이름을 붙여서 가져온다.
def psyche_rss(url):
    print("\nConnecting to Psyche rss feed...")
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
            time = a.find("pubDate").text
            name = "Psyche"

            dateFormatter = "%Y-%m-%dT%H:%M:%S.%fZ"
            dt = datetime.strptime(time, dateFormatter)
            published = dt.strftime("%Y-%m-%d")

            # DB에 저장되어 있지 않은 데이터를 list에 append한다.
            if check_DB(link) is not None:
                article = {
                    "name": name,
                    "title": title,
                    "link": link,
                    "published": published,
                }
                article_list.append(article)
        return article_list
    except Exception as e:
        print("Psyche (rss feed) - The scraping job failed. See exception: ")
        print(e)


# 갱신된 기사들의 text 전문을 가져온다.
def psyche_text(url, n, list_len):
    print(f"scrapping article text... {n}/{list_len}")
    text = ""
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        for item in soup.find_all(
            "div",
            {"class": "styled__Container-mut07i-1"},
        ):
            text = text + str(item.find_all(text=True))
            return text
    except Exception as e:
        print("Psyche (scrapping) - The scraping job failed. See exception: ")
        print(e)


def psyche_scrapping(url):
    psyche_rss(url)
    n = 1
    for key in article_list:
        text = psyche_text(key["link"], n, len(article_list))
        text = clean_text(text)
        key["tags"] = tagging(text)
        key["text_rank"] = len(text)
        n += 1

    # 순위 매기기
    # tag가 'others'인 경우, 대부분 뉴스 기사가 아니기에 최하위 rank를 부여함
    sort_article_list = enumerate(
        sorted(article_list, key=lambda rank: (rank["text_rank"]), reverse=True), 1
    )

    for rank, key in sort_article_list:
        if key["tags"] == "others":
            key["rank"] = 99
        else:
            key["rank"] = rank
        del key["text_rank"]

    print("Scrapping Aeon Finished!\n")
    return article_list