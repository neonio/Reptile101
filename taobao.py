from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from pyquery import PyQuery
from config_toutiao import *
import re
from pymongo import MongoClient

client = MongoClient(MONGO_URL)
db = client[MONGO_DB_TAOBAO]

browser_opts = webdriver.ChromeOptions()
browser_opts.headless = False
browser_path = '/Applications/ChromeDriver/chromedriver'

browser = webdriver.Chrome(executable_path=browser_path, options=browser_opts)
waitdriver = WebDriverWait(driver=browser, timeout=10)


def save_to_mongo(result):
    try:
        if db[MONGO_TABLE_TAOBAO].insert(result):
            pass
    except Exception:
        print("Save error")


def search(url):
    try:
        browser.get(url)
        searbar_elem: WebElement = waitdriver.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))

        )

        submit_elem: WebElement = waitdriver.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-search'))
        )
        searbar_elem.send_keys("玩具")
        submit_elem.click()
        page_count_elem: WebElement = waitdriver.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.total"))
        )
        page_count_text = page_count_elem.text
        get_product_info()
        return page_count_text
    except TimeoutException:
        search(url)


def load_items_page(index: int):
    try:
        input: WebElement = waitdriver.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )

        summit: WebElement = waitdriver.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
        )
        input.clear()
        input.send_keys(index)
        summit.click()
        waitdriver.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > ul > li.item.active"), str(index))
        )
        get_product_info()
    except TimeoutException:
        load_items_page(index)


def get_product_info():
    waitdriver.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-itemlist .items .item"))
    )

    html = browser.page_source
    doc = PyQuery(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('data-src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text(),
            'location': item.find('.location').text(),
        }
        save_to_mongo(product)

def execute_main():
    page_count_text = search('https://www.taobao.com')
    page_count = re.compile('(\d+)').search(page_count_text).group(1)
    for i in range(2, int(page_count) + 1):
        load_items_page(i)
    browser.close()


if __name__ == '__main__':
    execute_main()
