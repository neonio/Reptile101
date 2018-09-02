from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

opt = webdriver.ChromeOptions()
opt.headless = True
browser_entity = webdriver.Chrome(executable_path="/Applications/ChromeDriver/chromedriver", options=opt)
# https://chromedriver.storage.googleapis.com/index.html?path=2.41/
try:
    # 浏览器基本操作
    browser_entity.get("https://maoyan.com/board/1?")
    # browser_entity.back()
    # browser_entity.forward()

    # 获取百度输入框的 id
    # op_input = browser_entity.find_element_by_id('kw')
    # op_input = browser_entity.find_element_by_class_name('')
    # op_input = browser_entity.find_element_by_css_selector()
    # op_input = browser_entity.find_element(By.ID, 'kw')
    # 这时候就可以 获得 text、get_attribute('')、location、size 等属性
    # 如果找不到会raise error ，需要try-exception

    # 获取了这些属性可以使用 AutoChain 进行一些类似移动的操作

    # 元素交互
    # op_input.send_keys('Python')
    # op_input.send_keys(Keys.ENTER)
    # op_input.clear()

    # 执行 js
    # browser_entity.execute_script("window.scrollTo(0, document.body.scrollHeight)")

    # 等待
    # browser_entity.implicitly_wait(10)

    # 或者基于某个条件的等待
    # wait = WebDriverWait(browser_entity, 10)
    # wait.until(expected_conditions.presence_of_element_located((By.ID, 'content_left')))
    # wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '.btn-search')))

    # 设置 Cookie
    # browser_entity.add_cookie({})
    # browser_entity.delete_all_cookies()

    print(browser_entity.get_cookies())
    print(browser_entity.current_url)
    print(browser_entity.get_cookies())
    print(browser_entity.page_source)
except TimeoutException:
    print("TIME OUT")
finally:
    browser_entity.close()



