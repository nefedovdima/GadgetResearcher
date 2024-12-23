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

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def fetch_apple_i_tochka(query):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.maximize_window()
    wait = WebDriverWait(browser, 10)

    try:
        browser.get("https://appl-i-tochka.ru/")
        time.sleep(3)

        # Нажатие кнопки для активации строки поиска
        try:
            search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ty-search-block")))
            search_button.click()
            logger.info("Кнопка поиска нажата.")
        except Exception as e:
            logger.error(f"Не удалось найти или нажать кнопку поиска: {e}")
            return []

        # Ввод текста в строку поиска
        try:
            search_box = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ty-search-block__input")))
            logger.info("Строка поиска найдена.")
            logger.debug(f"Отображается: {search_box.is_displayed()}, Активна: {search_box.is_enabled()}")

            browser.execute_script("arguments[0].scrollIntoView(true);", search_box)
            browser.execute_script("arguments[0].removeAttribute('tabindex');", search_box)
            browser.execute_script("arguments[0].style.display = 'block';", search_box)

            search_box.click()
            search_box.send_keys(query)
            logger.info(f"Запрос '{query}' введён в строку поиска через send_keys().")

            search_box.send_keys(Keys.RETURN)
            logger.info("Поиск выполнен.")
        except Exception as e:
            logger.error(f"Ошибка при работе со строкой поиска: {e}")
            return []

        def parse_page():
            nonlocal products_info
            try:
                results_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "grid-list")))
                logger.info("Каталог с результатами поиска найден.")

                products = results_container.find_elements(By.CLASS_NAME, "ut2-gl__item")

                if not products:
                    logger.warning("Результатов не найдено.")
                    return False

                logger.info(f"Найдено {len(products)} продуктов.")
            except Exception as e:
                try:
                    no_results_message = browser.find_element(By.CLASS_NAME, "search-page__empty-message")
                    logger.warning(no_results_message.text)
                    return False
                except Exception as inner_e:
                    logger.error("Ошибка при ожидании продуктов и сообщение об отсутствии результатов не найдено.")
                    return False

            for product in products:
                logger.debug('Обработка продукта...')
                try:
                    name = product.find_element(By.CLASS_NAME, "ut2-gl__name").text
                    price_element = product.find_element(By.CSS_SELECTOR, ".ut2-gl__price.pr-row-mix")
                    price = price_element.text.strip() if price_element else "Цена не найдена"

                    try:
                        price = float(price.replace("₽", "").replace(" ", "").strip())
                    except ValueError:
                        logger.warning(f"Не удалось преобразовать цену '{price}' в числовой формат")
                        price = float('inf')

                    products_info.append((name, price))
                    logger.info(f"Название: {name}, Цена: {price}")
                except Exception as e:
                    logger.error(f"Ошибка при обработке продукта: {e}")
            return True

        def go_to_next_page():
            try:
                next_button = browser.find_element(By.CLASS_NAME, "ty-pagination__next")
                if next_button.is_displayed():
                    next_button.click()
                    time.sleep(5)
                    return True
                else:
                    return False
            except Exception as e:
                logger.info("Кнопка 'Следующая страница' не найдена или недоступна.")
                return False

        products_info = []
        for i in range(4):
            has_products = parse_page()
            if not has_products:
                break
            if not go_to_next_page():
                break
        products_info.sort(key=lambda x: x[1])
        filtered_products = [product for product in products_info if query.lower() in product[0].lower()]
        logger.info(f"Всего продуктов обработано: {len(filtered_products)}")
        return filtered_products
    finally:
        browser.quit()


if __name__ == "__main__":
    query = input("Введите название товара: ")
    results = fetch_apple_i_tochka(query)
    if not results:
        logger.info("По вашему запросу ничего не найдено.")
    else:
        logger.info("\nРезультаты поиска:")
        for name, price in results:
            logger.info(f"{name} - {price}")
