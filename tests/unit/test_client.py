import unittest
from unittest.mock import MagicMock
import sys

# Mock requests module before importing client
sys.modules["requests"] = MagicMock()

from tapsilat_py.client import TapsilatAPI


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = TapsilatAPI("test_key")

    def test_verify_webhook(self):
        payload = "data"
        secret = "key"
        # hmac-sha256 of "data" with key "key"
        signature = (
            "sha256=5031fe3d989c6d1537a013fa6e739da23463fdaec3b70137d828e36ace221bd0"
        )

        self.assertTrue(TapsilatAPI.verify_webhook(payload, signature, secret))
        self.assertFalse(TapsilatAPI.verify_webhook(payload, "sha256=invalid", secret))

    def test_health_check(self):
        expected_response = {"status": "healthy", "timestamp": "2023-10-27T10:00:00Z"}

        # Mock _make_request
        self.client._make_request = MagicMock(return_value=expected_response)

        result = self.client.health_check()

        self.client._make_request.assert_called_once_with("GET", "/health")
        self.assertEqual(result, expected_response)
