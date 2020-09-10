import requests
from lxml import etree
from selenium import webdriver
import time

chrome = webdriver.Chrome()
chrome.get("https://wenku.baidu.com/view/3980c7ccce22bcd126fff705cc17552707225efc.html?fr=search")
chrome.maximize_window()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
}

input("阻塞，手动点击加载更多的页面")
selection = etree.HTML(chrome.page_source)
print(selection)
print(type(selection))
# 模拟滑动
for i in range(1, 31):
    js = "var q=document.documentElement.scrollTop={}".format(i * 535)  # javascript语句
    chrome.execute_script(js)
    time.sleep(1)

empty_list = []
all_ppt_div = selection.xpath("//div[@class='ppt-image-wrap']/img/@src")
for j in all_ppt_div:
    empty_list.append(j)
time.sleep(3)

selection = etree.HTML(chrome.page_source)
for i in range(4, 34):
    all_ppt_div = selection.xpath(
        "//div[@class='ppt-page-item reader-pageNo-%s ppt-bd hidden-doc-banner']/div/img/@src" % str(i))
    try:
        empty_list.append(all_ppt_div[0])
    except:
        break

cout = 1
empty_list = list(set(empty_list))
for i in empty_list:
    r = requests.get(str(i))
    with open(f'D:/test_file/{cout}.jpg', 'wb') as f:
        f.write(r.content)
    cout += 1
