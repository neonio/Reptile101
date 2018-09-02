import requests
from typing import Optional
from requests.exceptions import RequestException
from fontTools.ttLib import TTFont
import re, os


def create_font_cloud(font_file) -> TTFont:
    file_list = os.listdir('./font')
    if font_file not in file_list:
        url = 'http://vfile.meituan.net/colorstone/' + font_file
        response = requests.get(url)
        with open('./font/{}'.format(font_file), 'wb') as f:
            f.write(response.content)
    return TTFont('./font/{}'.format(font_file))


def parse_font(html: str):
    result = re.search(r'embedded-opentype.*?vfile\.meituan\.net\/colorstone\/(.*?)\.woff', html, re.S)
    if result is None:
        return
    if result.group(1) is not None:
        site_font = create_font_cloud(result.group(1) + '.woff')
        gly_list = site_font.getGlyphOrder()
        print(gly_list[2:])


def get_headers_for_spider() -> dict:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/68.0.3440.75 Safari/537.36 '
    }
    return headers


def get_page_html(url) -> Optional[str]:
    try:
        headers = get_headers_for_spider()
        response = requests.get(url, headers=headers)
        if response.status_code == requests.codes.ok:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html: str):
    pattern = re.compile(
        r'<dd>.*?board-index.*?>(\d+)</.*?data-src="(.*?)".*?class="name">.*?href="(.*?)".*?title="(.*?)".*?"star">(.*?)</.*?"releasetime">(.*?)</',
        re.S)
    items = re.findall(pattern, html)
    print(items)


def main():

    url = "https://maoyan.com/board/1?"
    html = get_page_html(url)
    parse_font(html)
    # print(html)
    # parse_one_page(html)


if __name__ == '__main__':
    main()
