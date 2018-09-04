import os
from hashlib import md5
import pymongo as pymongo
import requests
import re
from urllib.parse import urlencode, urlparse
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import json
from config_toutiao import *
from multiprocessing import Pool

#MongoClient opened before fork. Create MongoClient only after forking. See PyMongo's documentation for details: http://api.mongodb.org/python/current/faq.html#is-pymongo-fork-safe "MongoClient opened before fork. Create MongoClient only "
client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]
BASEURL = "https://www.toutiao.com/search_content/?"


def parse_url_by_keywords(keyword: str, offset: int):
    try:
        query = {
            "offset": offset,
            "format": "json",
            "keyword": keyword,
            "autoload": True,
            "count": 20,
            "cur_tab": 3,
            "from": "gallery"
        }

        response = requests.get(url=BASEURL, params=urlencode(query))
        if response.status_code == requests.codes.ok:
            return response.text
        return None
    except RequestException:
        print("请求失败")
        return None


def parse_response_json(json_str: str):
    json_obj: dict = json.loads(json_str)
    if json_obj and "data" in json_obj.keys():
        json_data: dict = json_obj.get('data')
        for item in json_data:
            article_url_str: str = item.get('article_url')
            article_url = urlparse(article_url_str)
            if article_url.hostname == "toutiao.com":
                yield article_url_str


def get_gallary_detail(url: str):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/68.0.3440.75 Safari/537.36 '
        }
        response = requests.get(url=url, headers=headers)
        if response.status_code == requests.codes.ok:
            return response.text
        return None
    except RequestException:
        print("请求详情页失败")
        return None


def parse_gallary_json(html_str: str, url: str):
    soup = BeautifulSoup(html_str, 'lxml')
    title = soup.title.get_text()
    json_rex = re.compile(r'gallery: JSON\.parse\("(.*?)"\),', re.S)
    result = re.search(json_rex, html_str)
    if result:
        match_str = result.group(1).replace("\\", "")
        obj = json.loads(match_str)
        if obj and "sub_images" in obj.keys():
            sub_images = obj.get("sub_images")
            images = [item.get("url") for item in sub_images]
            for image_url in images:
                download_image(image_url)
            print("开始下载 {} 共有图片 {}".format(title, images.__len__()))
            return {
                'title': title,
                'images': images,
                'url': url
            }


def save_to_mongo(result: dict):
    if db[MONGO_TABLE].insert(result):
        return True
    else:
        return False


def download_image(url: str):
    print("正在下载 {}".format(url))
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/68.0.3440.75 Safari/537.36 '
        }
        response = requests.get(url=url, headers=headers)
        if response.status_code == requests.codes.ok:
            save_content(response.content)
        return None
    except RequestException:
        print("请求详情页失败")
        return None


def save_content(content):
    file_path = '{0}{1}img{1}{2}.{3}'.format(os.getcwd(), os.sep, md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)


def main(offset):
    KEYWORDS = "钢铁侠"
    query_url_str = parse_url_by_keywords(KEYWORDS, offset)
    for article_url in parse_response_json(query_url_str):
        detail_str = get_gallary_detail(article_url)
        result = parse_gallary_json(detail_str, article_url)
        save_to_mongo(result)

if __name__ == '__main__':
    group = [x * 20 for x in range(INDEX_START, INDEX_END + 1)]
    # 进程池
    pool = Pool()
    pool.map(main, group)

