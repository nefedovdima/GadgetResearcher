import re
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("nistone_search.log"),
            logging.StreamHandler()
        ]
    )

def sep_text_numb(text):
    result = re.findall(r"[a-zA-Zа-яА-Я]+|\d+", text)
    output = " ".join(result)
    return output

def fetch_nistone(query):
    query = sep_text_numb(query)
    logging.info(f"Подготовка поиска по запросу: {query}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Без графического интерфейса
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=chrome_options)

    logging.info('Подключение к сайту nistone. Пожалуйста, ожидайте')
    browser.get('https://nistone.ru/')
    browser.maximize_window()
    wait = WebDriverWait(browser, 10)
    search_element = wait.until(EC.element_to_be_clickable((By.NAME, "search")))
    time.sleep(1)
    search_element.send_keys(query)
    search_element.send_keys(Keys.RETURN)
    time.sleep(2)

    try:
        not_found_elem = browser.find_element(By.CLASS_NAME, "error_text")
        if not_found_elem.text == 'Нет результатов поиска :(':
            logging.warning('Товар не найден. Измените запрос и попробуйте снова')
            return
    except Exception:
        pass

    product_blocks = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product_block")))
    product_info = []
    logging.info("Начинается сбор информации о товарах")

    # for block in product_blocks:
    #     product_thumbs = block.find_elements(By.CLASS_NAME, "product-thumb.transition")
    #     for product_thumb in product_thumbs:
    #         name = product_thumb.find_element(By.CLASS_NAME, "catalog_product_name").text
    #         price = product_thumb.find_element(By.CLASS_NAME, "catalog_product_price").text
    #         price = int(price.replace(' ', '').replace('₽', ''))
    #         product_info.append((name, price))
    #         logging.info(f"Найден товар: {name}, Цена: {price}₽")
    
    for block in product_blocks:
        product_thumbs = block.find_elements(By.CLASS_NAME, "product-thumb.transition")
        for product_thumb in product_thumbs:
            name = product_thumb.find_element(By.CLASS_NAME, "catalog_product_name").text
            price = product_thumb.find_element(By.CLASS_NAME, "catalog_product_price").text
            try:
                price = int(price.replace(' ', '').replace('₽', '').replace('——', '0'))
            except ValueError:
                logging.warning(f"Невозможно преобразовать цену: {price}")
                continue
            product_info.append((name, price))
            logging.info(f"Найден товар: {name}, Цена: {price}₽")


    time.sleep(10)
    logging.info(f'Всего найдено товаров: {len(product_info)}')
    browser.quit()
    get_the_cheapest(product_info)
    return product_info

def get_the_cheapest(product_info):
    product_info.sort(key=lambda tup: tup[1])
    logging.info(f"Самый дешевый товар: {product_info[0]}" if product_info else "Товары отсутствуют")

if __name__ == "__main__":
    setup_logging()
    query = input('Введите товар, который ищете: \n')
    logging.info(f"Выполняется поиск товаров по запросу: {query}")
    fetch_nistone_products(query)