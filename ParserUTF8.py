# -*- coding: utf-8 -*-
import argparse
import sys
import time
import json
import io
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from fake_useragent import UserAgent

#useragent = UserAgent()


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

parser = argparse.ArgumentParser()

parser.add_argument("pages", type=int)

args = parser.parse_args()

pages = args.pages

urlFile = open(r"C:\Users\User\Documents\QT_Creator\Megamarket\Parsesr\ParserGui\build\Desktop_Qt_6_9_0_MSVC2022_64bit-Debug\debug\url.txt", 'r', encoding='utf-8')
try:
    base_url = urlFile.read().strip()
except Exception as e:
    print("Ошибка чтения input.txt:", str(e))
    sys.exit(1)

#option = webdriver.FirefoxOptions()
#option.add_argument(f"user-agent={useragent.ie}")

driver = webdriver.Firefox()

def parse_page(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'catalog-item-regular-desktop'))
        )
    except:
        print(f"Не получилось зайти на страницу с  url {url}")
        driver.quit()

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    items = soup.find_all('div', class_=lambda c: c and 'catalog-item-regular-desktop' in c and 'ddl_product' in c and 'catalog-item-desktop' in c)

    products = []

    for item in items:
        link_tag = item.find('a', class_='catalog-item-image-block__image ddl_product_link')
        if not link_tag:
            continue

        name = item.find(class_='catalog-item-regular-desktop__title-link ddl_product_link')
        product_name = name['title']
        product_link = link_tag['href']

        price_block = item.find('div', class_='catalog-item-regular-desktop__price')
        price = price_block.text.strip() if price_block else ''
        price = price.replace("₽", "RUB")

        bonus_block = item.find('div', class_='catalog-item-regular-desktop__bonus money-bonus sm money-bonus_loyalty')
        if not bonus_block:
            continue  

        percent_span = bonus_block.find('span', {'data-test': 'bonus-percent'})
        amount_span = bonus_block.find('span', {'data-test': 'bonus-amount'})

        bonus_percent = percent_span.text.strip() if percent_span else ''
        bonus_amount = amount_span.text.strip() if amount_span else ''

        products.append({
            "Имя": product_name,
            "Ссылка": "https://megamarket.ru" + product_link,
            "Цена": price,
            "Процент бонуса": bonus_percent,
            "Количество бонусов": bonus_amount
        })

    return products


all_products = []

for page in range(1, pages + 1):
    if page == 1:
        url = base_url
    else:
        url = base_url
        if '#' in url:
            url_part, query_part = base_url.split('#', 1)
            url = f"{url_part}/page-{page}" + query_part
        else:
            url_part, query_part = base_url.split('?q', 1)
            url = f"{url_part}page-{page}/?q" + query_part

    results = parse_page(driver, url)
    all_products.extend(results)

    time.sleep(2)  


result = json.dumps(all_products, ensure_ascii=False, indent=2)
safe_result = result.encode('utf-8', errors='replace').decode('utf-8')
print(safe_result)
driver.quit()





