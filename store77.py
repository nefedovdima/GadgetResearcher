import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def fetch_store_77(query):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Без графического интерфейса
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=chrome_options)
    logger.info('Подключение к сайту. Пожалуйста, ожидайте')
    browser.get('https://store77.net/')
    browser.maximize_window()
    wait = WebDriverWait(browser, 10)
    try:
        close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "beono-flashmessage-close")))
        close_button.click()
    except Exception:
        pass
    search_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "header_multisearch_link")))
    search_element.click()
    time.sleep(1)
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "ModalMultisearchInput")))
    search_button.send_keys(query)
    search_button.send_keys(Keys.RETURN)
    time.sleep(2)
    try:
        not_found_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "catalog-message")))
        if not_found_element.text == 'По вашему поисковому запросу товаров не найдено.':
            logger.warning('Товар не найден. Измените запрос и попробуйте снова')
            return []
    except Exception:
        pass
    products = browser.find_elements(By.CSS_SELECTOR, ".bp_text")
    product_info = []
    first_prod = False
    type_of_product = ''
    for product in products:
        bp_price = product.find_element(By.CSS_SELECTOR, ".bp_text_price.bp_width_fix")
        bp_text_info = product.find_element(By.CSS_SELECTOR, ".bp_text_info.bp_width_fix")
        name = bp_text_info.text
        price = bp_price.text
        if not first_prod:
            type_of_product = name.split(' ')[0]
            first_prod = True
        price = price.replace('—', '').replace(' ', '')
        try:
            price = int(price)
        except ValueError:
            logger.warning(f"Не удалось преобразовать цену: {price}. Пропускаем товар.")
            continue
        if name.split(' ')[0] == type_of_product:
            product_info.append((name, price))
    time.sleep(10)
    browser.quit()
    logger.info(f"Всего найдено товаров: {len(product_info)}")
    return product_info

def get_the_cheapest(product_info, query):
    if not product_info:
        logger.info(f'Товары по запросу "{query}" не найдены.')
        return None
    product_info.sort(key=lambda tup: tup[1])
    logger.info(f'Самый дешевый товар по запросу "{query}": {product_info[0][0]}\nЦена: {product_info[0][1]}₽')
    return product_info[0]

if __name__ == "__main__":
    query = input('Введите товар, который ищете: \n')
    logger.info(f"Выполняется поиск товаров по запросу: {query}")
    try:
        results = fetch_store_77(query)
        if results:
            get_the_cheapest(results, query)
        else:
            logger.info("Товары не найдены.")
    except Exception:
        try:
            results = fetch_store_77(query)
            if results:
                get_the_cheapest(results, query)
            else:
                logger.info("Товары не найдены.")
        except Exception:
            logger.error('Что-то пошло не так. Попробуйте еще раз повторить попытку')
