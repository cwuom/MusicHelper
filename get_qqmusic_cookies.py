from selenium import webdriver
import time

from webdriver_manager.microsoft import EdgeChromiumDriverManager

HOST = 'https://y.qq.com/'

while True:
    driver = webdriver.Edge(executable_path=EdgeChromiumDriverManager().install())
    driver.get(HOST)
    driver.find_element_by_link_text("登录").click()

    time.sleep(3)
    driver.switch_to.frame('login_frame')
    driver.switch_to.frame('ptlogin_iframe')
    driver.find_element_by_xpath(r"""//*[@id="qlogin_list"]/a""").click()

    time.sleep(5)
    if len(driver.get_cookies()) != 0:
        w = open("cookies_qq.txt", "w+")
        w.write("")
        w.close()
        x = 0
        for cookie in driver.get_cookies():
            print(cookie)
            a = open("cookies_qq.txt", "a+")
            if x < (len(driver.get_cookies()) - 1):
                a.write(cookie["name"] + "=" + cookie["value"] + ";")
            else:
                a.write(cookie["name"] + "=" + cookie["value"])
            x += 1

    driver.quit()

    now_hour = time.strftime("%H", time.localtime())
    now_min = time.strftime("%M", time.localtime())
    if now_hour < "08":
        rest = 8 - int(now_hour)
        wait_time = (rest - 1) * 3600 + (60 - int(now_min)) * 60
    elif now_hour > "08":
        rest = 8 - int(now_hour) + 24
        wait_time = (rest - 1) * 3600 + (60 - int(now_min)) * 60
    elif now_hour == "08":
        continue

    wait_time += 3600
    for y in range(wait_time):
        time.sleep(1)
        print("\r下次运行:", wait_time - y, "   ", end="", flush=True)
