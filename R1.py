import requests
import re

response = requests.get("https://book.douban.com/")
content = response.text

rex = r'<li.*?cover.*?href="(.*?)" title="(.*?)">.*?<div.*?author">(.*?)</.*?class="year">(.*?)<'
match_list = re.findall(rex, content, re.S)
for item in match_list:
    url = re.sub(r'\s', '', item[0])
    title = re.sub(r'\s', '', item[1])
    author= re.sub(r'\s', '', item[2])
    date = re.sub(r'\s', '', item[3])
    print(url, title, author, date)
