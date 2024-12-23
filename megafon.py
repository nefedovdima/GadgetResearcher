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

def fetch_megafon(query):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.maximize_window()
    wait = WebDriverWait(browser, 10)

    try:
        browser.get("https://moscow.shop.megafon.ru/")
        time.sleep(5)
        try:
            popup_close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "popmechanic-close")))
            popup_close_button.click()
            logger.info("Всплывающее окно закрыто.")
        except Exception:
            logger.info("Всплывающие окна не найдены.")
        # Нажатие кнопки для активации строки поиска
        try:
            search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ch-search__field")))
            search_button.click()
            logger.info("Кнопка поиска нажата.")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Не удалось найти или нажать кнопку поиска: {e}")
            return []

        # Ввод текста в строку поиска
        try:
            search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".mfui-v6-text-field__field.ch-search__input.ch-search__input_v2")))
            logger.info("Строка поиска найдена.")
            logger.debug(f"Отображается: {search_box.is_displayed()}")
            logger.debug(f"Активна: {search_box.is_enabled()}")
            logger.debug("HTML элемента строки поиска: %s", search_box.get_attribute("outerHTML"))

            browser.execute_script("arguments[0].scrollIntoView(true);", search_box)
            # Убираем блокировку, если есть
            browser.execute_script("arguments[0].removeAttribute('tabindex');", search_box)
            browser.execute_script("arguments[0].style.display = 'block';", search_box)

            # Ввод текста через send_keys()
            search_box.click()  # Клик для активации поля
            search_box.send_keys(query)  # Ввод текста
            logger.info(f"Запрос '{query}' введён в строку поиска через send_keys().")

            # Нажимаем кнопку для выполнения поиска
            search_box.send_keys(Keys.RETURN)
            time.sleep(20)
            logger.info("Поиск выполнен.")
        except Exception as e:
            logger.error(f"Ошибка при работе со строкой поиска: {e}")
            return []

        def parse_page():
            nonlocal products_info
            # Ожидание загрузки продуктов
            try:
                results_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "b-goods-list")))
                logger.info("Каталог с результатами поиска найден.")

                # Извлечение всех продуктов из каталога
                products = results_container.find_elements(By.CLASS_NAME, "b-goods-list__item")

                if not products:  # Если список продуктов пуст
                    logger.warning("Результатов не найдено.")
                    return False

                logger.info(f"Найдено {len(products)} продуктов.")
            except Exception as e:
                try:
                    no_results_message = browser.find_element(By.CLASS_NAME, "b-top-panel__subtitle")
                    logger.warning(no_results_message.text)
                    return False
                except Exception as inner_e:
                    logger.error("Ошибка при ожидании продуктов и сообщение об отсутствии результатов не найдено.")
                    return False

            # Сбор информации о продуктах
            for product in products:
                logger.debug('Обработка продукта...')
                try:
                    name_element = product.find_element(By.CSS_SELECTOR, "input[name='goodName']")
                    name = name_element.get_attribute("value")

                    price_element = product.find_element(By.CSS_SELECTOR, "input[name='goodPriceMain']")
                    price = price_element.get_attribute("value")

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
                pagination_container = browser.find_element(By.CLASS_NAME, "b-pagination__body")
                logger.info("Контейнер пагинации найден.")

                # Поиск кнопки "Следующая страница" внутри контейнера
                next_button = pagination_container.find_element(By.CLASS_NAME, "b-pagination__next")
                logger.info("Кнопка 'Следующая страница' найдена.")

                # Запоминаем текущий URL страницы
                current_url = browser.current_url

                # Прокрутка до кнопки
                browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)

                # Проверяем, доступна ли кнопка
                if not next_button.is_displayed() or not next_button.is_enabled():
                    logger.info("Кнопка 'Следующая страница' не доступна для клика.")
                    return False

                # Клик по кнопке "Следующая страница"
                browser.execute_script("arguments[0].click();", next_button)
                logger.info("Клик по кнопке 'Следующая страница' выполнен.")
                time.sleep(5)  # Ожидание загрузки следующей страницы

                # Проверяем, изменилась ли страница
                if browser.current_url == current_url:
                    logger.info("Достигнута последняя страница.")
                    return False

                return True
            except Exception as e:
                logger.error(f"Ошибка при поиске или клике кнопки 'Следующая страница': {e}")
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
        logger.info(f"Всего продуктов обработано: {len(filtered_products)}")
        return filtered_products
    finally:
        browser.quit()

if __name__ == "__main__":
    query = input("Введите название товара: ")
    results = fetch_megafon(query)
    if not results:  # Если список результатов пуст, не выводим ничего
        logger.info("По вашему запросу ничего не найдено.")
    else:
        logger.info("\nРезультаты поиска:")
        for name, price in results:
            logger.info(f"{name} - {price}")
