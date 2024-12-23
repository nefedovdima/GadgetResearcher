import logging
import re
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


logger = logging.getLogger(__name__)


# Функция для извлечения цены без лишних тегов
def get_number_without_span(text):
    match = re.search(r'<span[^>]*>\s*([\d\s&nbsp;]+)</span>', text)
    if match:
        return int(match.group(1).replace('&nbsp;', '').replace(' ', ''))
    return 0

def fetch_biggeek(query):
    # return [('Смартфон Apple iPhone 15 128 ГБ (Голубой | Blue)', 83990), ('Смартфон Apple iPhone 15 Pro Max 256 ГБ («Белый титан» | White Titanium)', 127990), ('Смартфон Apple iPhone 15 Pro 256 ГБ («Натуральный титан» | Natural Titanium)', 135990), ('Смартфон Apple iPhone 15 Pro Max 512 ГБ («Синий титан» | Blue Titanium)', 142990), ('Смартфон Apple iPhone 15 128 ГБ (Чёрный | Black)', 80990), ('Смартфон Apple iPhone 15 Pro 128 ГБ («Чёрный титан» | Black Titanium)', 113990), ('Смартфон Apple iPhone 15 128 ГБ (Розовый | Pink)', 77990), ('Смартфон Apple iPhone 15 256 ГБ (Чёрный | Black)', 97990), ('Смартфон Apple iPhone 15 Plus 256 ГБ (Чёрный | Black)', 110990), ('Смартфон Apple iPhone 15 Pro 512 ГБ («Натуральный титан» | Natural Titanium)', 143990), ('Смартфон Apple iPhone 15 Pro Max 512 ГБ («Чёрный титан» | Black Titanium)', 142990), ('Смартфон Apple iPhone 15 Plus 128 ГБ (Зелёный | Green)', 86990), ('Смартфон Apple iPhone 15 Pro Max 512 ГБ («Белый титан» | White Titanium)', 142990), ('Смартфон Apple iPhone 15 Plus 256 ГБ (Голубой | Blue)', 110990), ('Смартфон Apple iPhone 15 128 ГБ (Жёлтый | Yellow)', 83990), ('Смартфон Apple iPhone 15 Pro 512 ГБ («Синий титан» | Blue Titanium)', 138990), ('Смартфон Apple iPhone 15 Pro 256 ГБ («Синий титан» | Blue Titanium)', 129990), ('Смартфон Apple iPhone 15 Pro Max 256 ГБ («Синий титан» | Blue Titanium)', 127990), ('Смартфон Apple iPhone 15 Plus 128 ГБ (Чёрный | Black)', 85990), ('Смартфон Apple iPhone 15 Pro Max 256 ГБ («Чёрный титан» | Black Titanium)', 124990)]
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    browser = uc.Chrome(options=options)
    try:
        logger.info(f"Ищу товары по запросу: {query}")
        browser.get('https://biggeek.ru/')
        wait = WebDriverWait(browser, 10)
        time.sleep(2)

        # Закрываем всплывающее окно, если оно есть
        try:
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "we-closed-modal__close"))).click()
            logger.info("Закрыто всплывающее окно.")
        except Exception:
            logger.info("Всплывающее окно отсутствует.")

        # Вводим запрос в строку поиска
        search_box = wait.until(EC.element_to_be_clickable((By.ID, "search-header-middle")))
        search_box.send_keys(query)
        time.sleep(1)

        # Нажимаем кнопку поиска
        try:
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "digi-ac-find__button"))).click()
            logger.info("Кнопка поиска нажата.")
        except Exception:
            logger.warning("Товар не найден. Кнопка поиска недоступна.")
            return []

        # Прокрутка страницы для загрузки данных
        time.sleep(3)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Получаем список товаров
        products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "digi-product__main")))
        product_info = []

        for product in products:
            try:
                name = product.find_element(By.CLASS_NAME, "digi-product__label").text
                price_elements = product.find_elements(By.CLASS_NAME, "digi-product-price-variant_actual") or \
                                 product.find_elements(By.CLASS_NAME, "digi-product-price-variant_old")
                price = get_number_without_span(price_elements[0].get_attribute('outerHTML')) if price_elements else 0
                product_info.append((name, price))
                logger.info(f"Найден товар: {name} - {price}₽")
            except Exception as e:
                logger.error(f"Ошибка при обработке товара: {e}")

        return product_info
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return []
    finally:
        browser.quit()
        logger.info("Браузер закрыт.")