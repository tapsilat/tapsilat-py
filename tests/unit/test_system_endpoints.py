import unittest
from unittest.mock import MagicMock, patch
from tapsilat_py.client import TapsilatAPI

class TestSystemEndpoints(unittest.TestCase):
    def setUp(self):
        self.api = TapsilatAPI(api_key="test_key")
        self.api._make_request = MagicMock()

    def test_get_system_basket_item_types(self):
        expected_response = {"data": []}
        self.api._make_request.return_value = expected_response
        response = self.api.get_system_basket_item_types()
        self.api._make_request.assert_called_once_with("GET", "/system/basket-item-types")
        self.assertEqual(response, expected_response)

    def test_get_system_error_codes(self):
        expected_response = {"data": []}
        self.api._make_request.return_value = expected_response
        response = self.api.get_system_error_codes()
        self.api._make_request.assert_called_once_with("GET", "/system/error-codes")
        self.assertEqual(response, expected_response)

    def test_get_system_payment_term_statuses(self):
        expected_response = {"data": []}
        self.api._make_request.return_value = expected_response
        response = self.api.get_system_payment_term_statuses()
        self.api._make_request.assert_called_once_with("GET", "/system/payment-term-statuses")
        self.assertEqual(response, expected_response)

    def test_get_system_product_types(self):
        expected_response = {"data": []}
        self.api._make_request.return_value = expected_response
        response = self.api.get_system_product_types()
        self.api._make_request.assert_called_once_with("GET", "/system/product-types")
        self.assertEqual(response, expected_response)

    def test_get_system_shortcut_types(self):
        expected_response = {"data": []}
        self.api._make_request.return_value = expected_response
        response = self.api.get_system_shortcut_types()
        self.api._make_request.assert_called_once_with("GET", "/system/shortcut-types")
        self.assertEqual(response, expected_response)

    def test_get_system_transaction_payment_types(self):
        expected_response = {"data": []}
        self.api._make_request.return_value = expected_response
        response = self.api.get_system_transaction_payment_types()
        self.api._make_request.assert_called_once_with("GET", "/system/transaction-payment-types")
        self.assertEqual(response, expected_response)

    def test_get_system_transaction_purposes(self):
        expected_response = {"data": []}
        self.api._make_request.return_value = expected_response
        response = self.api.get_system_transaction_purposes()
        self.api._make_request.assert_called_once_with("GET", "/system/transaction-purposes")
        self.assertEqual(response, expected_response)

    def test_get_system_transaction_statuses(self):
        expected_response = {"data": []}
        self.api._make_request.return_value = expected_response
        response = self.api.get_system_transaction_statuses()
        self.api._make_request.assert_called_once_with("GET", "/system/transaction-statuses")
        self.assertEqual(response, expected_response)
