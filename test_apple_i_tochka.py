import unittest
from unittest.mock import MagicMock, patch
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from apple_i_tochka import fetch_apple_i_tochka


class TestAppliTochkaProducts(unittest.TestCase):
    @patch('apple_i_tochka.webdriver.Chrome')
    @patch('apple_i_tochka.WebDriverWait')
    def test_fetch_apple_i_tochka(self, mock_wait, mock_browser):
        # Mock браузера
        mock_browser.return_value = MagicMock(spec=WebDriver)
        browser_instance = mock_browser.return_value

        # Mock элементов веб-страницы
        wait_instance = mock_wait.return_value
        mock_search_button = MagicMock(spec=WebElement)
        mock_search_box = MagicMock(spec=WebElement)
        mock_results_container = MagicMock(spec=WebElement)
        mock_product_item = MagicMock(spec=WebElement)
        mock_name_element = MagicMock(spec=WebElement)
        mock_price_element = MagicMock(spec=WebElement)

        # Настройка возвращаемых значений
        wait_instance.until.side_effect = [
            mock_search_button,  # Для кнопки поиска
            mock_search_box,  # Для строки поиска
            mock_results_container,  # Для контейнера с результатами
        ]
        mock_search_button.click.return_value = None
        mock_search_box.send_keys.return_value = None
        mock_results_container.find_elements.return_value = [mock_product_item]
        mock_product_item.find_element.side_effect = [mock_name_element, mock_price_element]
        mock_name_element.text = "Тестовый продукт"
        mock_price_element.text = "1 000 ₽"

        # Выполнение тестируемой функции
        results = fetch_apple_i_tochka("Тест")

        # Проверки
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ("Тестовый продукт", 1000.0))

        # Проверяем вызовы методов
        mock_browser.assert_called_once()
        mock_search_button.click.assert_called_once()
        mock_search_box.send_keys.assert_called_with(unittest.mock.ANY)

    @patch('apple_i_tochka.webdriver.Chrome')
    @patch('apple_i_tochka.WebDriverWait')
    def test_no_results(self, mock_wait, mock_browser):
        # Mock браузера
        mock_browser.return_value = MagicMock(spec=WebDriver)
        browser_instance = mock_browser.return_value

        # Mock элементов
        wait_instance = mock_wait.return_value
        mock_search_button = MagicMock(spec=WebElement)
        mock_search_box = MagicMock(spec=WebElement)
        mock_empty_message = MagicMock(spec=WebElement)

        # Настройка
        wait_instance.until.side_effect = [
            mock_search_button,  # Для кнопки поиска
            mock_search_box,  # Для строки поиска
        ]
        mock_search_button.click.return_value = None
        mock_search_box.send_keys.return_value = None
        browser_instance.find_element.return_value = mock_empty_message
        mock_empty_message.text = "Нет результатов."

        # Выполнение
        results = fetch_apple_i_tochka("Несуществующий товар")

        # Проверки
        self.assertEqual(len(results), 0)

    @patch('apple_i_tochka.webdriver.Chrome')
    def test_browser_quit(self, mock_browser):
        # Mock браузера
        mock_browser.return_value = MagicMock(spec=WebDriver)
        browser_instance = mock_browser.return_value

        # Выполнение
        try:
            fetch_apple_i_tochka("Тест")
        except Exception:
            pass  # Игнорируем ошибки для проверки закрытия браузера

        # Проверка, что браузер закрыт
        browser_instance.quit.assert_called_once()

    # def test_price_parsing(self):
    #     # Тестирование преобразования цен
    #     from apple_i_tochka import fetch_apple_i_tochka  # Импортируем функцию для внутреннего тестирования
    #     test_data = [
    #         ("1 000 ₽", 1000.0),
    #         ("500₽", 500.0),
    #         ("Цена не найдена", float('inf')),
    #         ("Invalid Price", float('inf')),
    #     ]
    #     for price_string, expected in test_data:
    #         with patch('apple_i_tochka.fetch_apple_i_tochka.parse_page') as mock_parse_page:
    #             mock_parse_page.price = price_string
    #             self.assertEqual(fetch_apple_i_tochka("Тест"), expected)


if __name__ == '__main__':
    unittest.apple_i_tochka()
