import unittest
from unittest.mock import MagicMock, patch
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from biggeek import fetch_biggeek, get_number_without_span, get_the_cheapest, perform_search, \
    close_modal, fetch_product_info


class TestBigGeekProducts(unittest.TestCase):
    @patch('biggeek.setup_browser')
    @patch('biggeek.WebDriverWait')
    def test_fetch_biggeek_products(self, mock_wait, mock_browser):
        mock_browser.return_value = MagicMock(spec=WebDriver)

        wait_instance = mock_wait.return_value
        mock_element = MagicMock(spec=WebElement)

        wait_instance.until.side_effect = [
            mock_element,
            mock_element,
            mock_element,
        ]

        with patch('biggeek.fetch_product_info', return_value=[("Тест", 10000)]):
            cheapest = fetch_biggeek("Тест")
            self.assertEqual(cheapest, ("Тест", 10000))

    def test_get_number_without_span(self):
        self.assertEqual(get_number_without_span("<span>1234</span>"), 1234)
        self.assertEqual(get_number_without_span("<span>1&nbsp;234</span>"), 1234)
        self.assertEqual(get_number_without_span("Нет результатов"), 0)

    def test_get_the_cheapest(self):
        products = [("dyson", 70000), ("iphone 12", 40000), ("macbook pro", 200000)]
        self.assertEqual(get_the_cheapest(products), ("iphone 12", 40000))

    @patch('biggeek.WebDriverWait')
    def test_perform_search(self, mock_wait):
        mock_element = MagicMock(spec=WebElement)
        wait_instance = mock_wait.return_value
        wait_instance.until.side_effect = [mock_element, mock_element]

        browser_mock = MagicMock(spec=WebDriver)
        result = perform_search(browser_mock, wait_instance, "Тест")
        self.assertTrue(result)
        wait_instance.until.assert_called()

    @patch('biggeek.WebDriverWait')
    def test_close_modal(self, mock_wait):
        mock_element = MagicMock(spec=WebElement)
        wait_instance = mock_wait.return_value
        wait_instance.until.return_value = mock_element

        browser_mock = MagicMock(spec=WebDriver)
        close_modal(browser_mock, wait_instance)

        wait_instance.until.assert_called_with(unittest.mock.ANY)

    @patch('biggeek.WebDriverWait')
    def test_fetch_product_info(self, mock_wait):
        mock_element = MagicMock(spec=WebElement)
        mock_product_label = MagicMock(spec=WebElement)
        mock_product_label.text = "Тест"

        mock_price_element = MagicMock(spec=WebElement)
        mock_price_element.get_attribute.return_value = "<span>10000</span>"

        mock_element.find_element.return_value = mock_product_label
        mock_element.find_elements.side_effect = [[mock_price_element], []]

        wait_instance = mock_wait.return_value
        wait_instance.until.return_value = [mock_element]

        browser_mock = MagicMock(spec=WebDriver)
        products = fetch_product_info(browser_mock, wait_instance)
        self.assertEqual(products, [("Тест", 10000)])


if __name__ == '__main__':
    unittest.main()
