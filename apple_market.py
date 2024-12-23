import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def fetch_apple_market(query):
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.maximize_window()
    wait = WebDriverWait(browser, 10)
    filtered_products = list()
    try:
        browser.get("https://apple-market.ru/")
        time.sleep(3)

        # Нажатие кнопки для активации строки поиска
        try:
            search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "header__button_search")))
            search_button.click()
            logging.info("Кнопка поиска нажата.")
        except Exception as e:
            logging.error(f"Не удалось найти или нажать кнопку поиска: {e}")
            return []

        # Ввод текста в строку поиска
        try:
            search_box = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search__input")))
            logging.info("Строка поиска найдена.")
            logging.info("Проверка видимости строки поиска:")
            logging.info(f"Отображается: {search_box.is_displayed()}")
            logging.info(f"Активна: {search_box.is_enabled()}")
            logging.debug("HTML элемента строки поиска: %s", search_box.get_attribute("outerHTML"))

            browser.execute_script("arguments[0].scrollIntoView(true);", search_box)
            # Убираем блокировку, если есть
            browser.execute_script("arguments[0].removeAttribute('tabindex');", search_box)
            browser.execute_script("arguments[0].style.display = 'block';", search_box)

            # Ввод текста через send_keys()
            search_box.click()  # Клик для активации поля
            time.sleep(1)  # Задержка для имитации
            search_box.send_keys(query)  # Ввод текста
            logging.info(f"Запрос '{query}' введён в строку поиска через send_keys().")

            # Нажимаем кнопку для выполнения поиска
            search_box.send_keys(Keys.RETURN)
            logging.info("Поиск выполнен.")
        except Exception as e:
            logging.error(f"Ошибка при работе со строкой поиска: {e}")
            return []

        # Ожидание загрузки продуктов
        def parse_page():
            nonlocal products_info
            try:
                results_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-page__results")))
                logging.info("Каталог с результатами поиска найден.")

                # Извлечение всех продуктов из каталога
                products = results_container.find_elements(By.CLASS_NAME, "search-page__results-item")

                if not products:  # Если список продуктов пуст
                    logging.info("Результатов не найдено.")
                    return False

                logging.info(f"Найдено {len(products)} продуктов.")
            except Exception as e:
                try:
                    no_results_message = browser.find_element(By.CLASS_NAME, "search-page__empty-message")
                    logging.info(no_results_message.text)
                    return False
                except Exception as inner_e:
                    logging.error("Ошибка при ожидании продуктов и сообщение об отсутствии результатов не найдено.")
                    return False

            # Сбор информации о продуктах
            for product in products:
                logging.info('Обработка продукта...')
                try:
                    name = product.find_element(By.CLASS_NAME,"product__name").text
                    price = product.find_element(By.CLASS_NAME, "product__prices").text
                    products_info.append((name, price))
                    logging.info(f"Название: {name}, Цена: {price}")
                except Exception as e:
                    logging.error(f"Ошибка при обработке продукта: {e}")
            return True

        def go_to_next_page():
            try:
                next_button = browser.find_element(By.CLASS_NAME, "navigation__right")
                if next_button.is_displayed():
                    next_button.click()
                    time.sleep(5)
                    return True
                else:
                    return False
            except Exception as e:
                logging.info("Кнопка 'Следующая страница' не найдена или недоступна.")
                return False

        products_info = []
        while True:
            has_products = parse_page()
            if not has_products:
                break
            if not go_to_next_page():
                break
        products_info.sort(key=lambda x: x[1])
        filtered_products = [product for product in products_info if query.lower() in product[0].lower()]
        logging.info(f"Всего продуктов обработано: {len(filtered_products)}")
        return filtered_products
    finally:
        return filtered_products
        browser.quit()

if __name__ == "__main__":
    query = input("Введите название товара: ")
    results = fetch_apple_market(query)
    if not results:  # Если список результатов пуст, не выводим ничего
        logging.info("По вашему запросу ничего не найдено.")
    else:
        logging.info("\nРезультаты поиска:")
        for name, price in results:
            logging.info(f"{name} - {price}")
