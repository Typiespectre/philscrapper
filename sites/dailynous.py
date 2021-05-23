from database import check_DB
import config
import requests
import json
import re
import textwrap
from datetime import datetime
from database import check_DB


def auth():
    bearer_token = config.bearer_token
    return bearer_token


def create_headers(bearer_token):
    search_headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return search_headers


def search_url():
    query = "from:DailyNousEditor -is:reply -is:retweet"
    tweet_fields = "tweet.fields=author_id,created_at,text"
    user_fields = "user.fields=url"
    max_results = "max_results=50"

    search_url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&{}".format(
        query, tweet_fields, max_results
    )
    return search_url


def connect_to_endpoint(url, headers):
    search_response = requests.request("GET", url, headers=headers)
    if search_response.status_code != 200:
        raise Exception(search_response.status_code, search_response.text)
    return search_response.json()


def dailynous_list(json_obj):
    print("\nConnecting to DailyNous twitter...")
    global article_list
    article_list = []
    try:
        for i in json_obj["data"]:
            text = i["text"]
            regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
            link = re.findall(regex, text)[0]

            title = re.sub(link, "", text, flags=re.I)
            title = textwrap.shorten(title, width=80, placeholder=" ...")

            time = i["created_at"]
            dateformatter = "%Y-%m-%dT%H:%M:%S.%fZ"
            dt = datetime.strptime(time, dateformatter)
            published = dt.strftime("%Y-%m-%d")

            name = "DailyNous(twitter)"

            if check_DB(link) is not None:
                article = {
                    "name": name,
                    "title": title,
                    "link": link,
                    "published": published,
                    "tags": "twitter",
                    "rank": 99,
                }
                article_list.append(article)
        for i in range(len(article_list)):
            print(f"New twitter found... {i}/{len(article_list)}")
        print("Scrapping DailyNous Finished!\n")
        return article_list
    except Exception as e:
        print("DailyNous (twitter) - The scraping job failed. See exception: ")
        print(e)


def dailynous_scrapping():
    bearer_token = auth()
    headers = create_headers(bearer_token)
    url = search_url()
    json_response = connect_to_endpoint(url, headers)
    json_response = json.dumps(json_response, indent=4, sort_keys=True)
    json_obj = json.loads(json_response)
    dailynous_list(json_obj)
    return article_list