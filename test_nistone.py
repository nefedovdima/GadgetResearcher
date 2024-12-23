import unittest
from unittest.mock import patch, MagicMock

from selenium.webdriver import Keys

from nistone import (
    sep_text_numb,
    initialize_browser,
    perform_search,
    check_no_results,
    extract_products,
    get_the_cheapest,
)


class TestFindProductsNistone(unittest.TestCase):

    def test_sep_text_numb(self):
        self.assertEqual(sep_text_numb("Товар123"), "Товар 123")
        self.assertEqual(sep_text_numb("Цена2000₽"), "Цена 2000")
        self.assertEqual(sep_text_numb("БезЦифр"), "БезЦифр")

    @patch("nistone.webdriver.Chrome")
    def test_initialize_browser(self, mock_chrome):
        mock_browser = MagicMock()
        mock_chrome.return_value = mock_browser
        browser = initialize_browser()
        self.assertEqual(browser, mock_browser)
        mock_chrome.assert_called_once()

    @patch("nistone.WebDriverWait")
    def test_perform_search(self, mock_wait):
        mock_browser = MagicMock()
        mock_search_element = MagicMock()
        mock_wait.return_value.until.return_value = mock_search_element

        perform_search(mock_browser, "Запрос")

        mock_wait.assert_called_once_with(mock_browser, 10)
        mock_search_element.send_keys.assert_any_call("Запрос")
        mock_search_element.send_keys.assert_any_call(Keys.RETURN)

    @patch("nistone.webdriver.Chrome")
    def test_check_no_results(self, mock_chrome):
        mock_browser = MagicMock()
        mock_error_element = MagicMock()
        mock_error_element.text = 'Нет результатов поиска :('
        mock_browser.find_element.return_value = mock_error_element

        self.assertTrue(check_no_results(mock_browser))

        mock_browser.find_element.side_effect = Exception("Нет результатов")
        self.assertFalse(check_no_results(mock_browser))

    @patch("nistone.WebDriverWait")
    def test_extract_products(self, mock_wait):
        mock_browser = MagicMock()
        mock_product_block = MagicMock()
        mock_thumb = MagicMock()

        mock_thumb.find_element.side_effect = [
            MagicMock(text="Товар"),
            MagicMock(text="40 000₽"),
        ]

        mock_product_block.find_elements.return_value = [mock_thumb]
        mock_wait.return_value.until.return_value = [mock_product_block]

        products = extract_products(mock_browser)

        self.assertEqual(products, [("Товар", 40000)])

    def test_get_the_cheapest(self):
        product_info = [("dyson", 70000), ("iphone 12", 40000), ("macbook pro m4", 200000)]
        cheapest = get_the_cheapest(product_info)
        self.assertEqual(cheapest, ("iphone 12", 40000))


if __name__ == "__main__":
    unittest.main()
