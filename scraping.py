import schedule
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from pymongo import MongoClient
import secret

# MongoDBConnection
client = MongoClient(secret.mongo_db_key)
db = client.dbsparta
itemCollection = db.items


def init():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    sleep(3)

    return driver


def scrap_gs(driver):
    url = "http://gs25.gsretail.com/gscvs/ko/products/youus-freshfood"
    driver.get(url)
    sleep(2)
    driver.execute_script("searchSortCick('searchNewDateSort');")
    sleep(2)

    item_list = []

    for i in range(1, 3):
        if i != 1:
            driver.execute_script('vagelistCommonFn.movePage(%d)' % i)
            sleep(2)

        req = driver.page_source
        soup = BeautifulSoup(req, 'html.parser')
        items = soup.select(".prod_list > li > .prod_box")

        for item in items:
            image = item.select_one(".img > img")['src']
            title = item.select_one(".tit").text
            price = item.select_one(".price").text
            item_list.append({
                "store": "gs",
                "image": image,
                "title": title,
                "price": price,
                "like": 0
            })

        sleep(1)
    return item_list


def scrap_s11(driver):
    url = "https://www.7-eleven.co.kr/product/bestdosirakList.asp"
    driver.get(url)
    sleep(2)

    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')

    items = soup.select(".dosirak_list > ul > li:nth-child(n+1)")
    item_list = []

    for item in items:
        is_new = item.select_one(".tag_list_01 > .ico_tag_03")
        if is_new is not None and is_new.text == "신상품":
            source = item.select_one(".pic_product > img")
            image = source['src']
            title = source['alt']

            item_list.append({
                "store": "s11",
                "image": "https://www.7-eleven.co.kr" + image,
                "title": title,
                "price": 0,
                "like": 0
            })
    sleep(1)
    return item_list


def scrap_cu(driver):
    item_list = []
    for i in range(1, 5):
        url = "https://cu.bgfretail.com/product/product.do?category=product&depth2=4&depth3=%d" % i

        driver.get(url)
        sleep(2)
        driver.execute_script("setCond('setC');")  # 최신순 정렬
        sleep(2)

        req = driver.page_source
        soup = BeautifulSoup(req, 'html.parser')
        items = soup.select(".prod_wrap")

        for item in items:
            image = item.select_one(".prod_img > img")["src"]
            title = item.select_one(".prod_text > .name").text
            price = item.select_one(".prod_text > .price").text
            item_list.append({
                "store": "cu",
                "image": "http:" + image,
                "title": title,
                "price": price,
                "like": 0
            })
        sleep(1)
    return item_list


def scrap_items():
    driver = init()
    itemCollection.insert_many(scrap_gs(driver))
    itemCollection.insert_many(scrap_s11(driver))
    itemCollection.insert_many(scrap_cu(driver))
    driver.close()


def scheduling():
    scrap_items()
    schedule.every(1).monday.at("00:00").do(scrap_items)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    scheduling()
