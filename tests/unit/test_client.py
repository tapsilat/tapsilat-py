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
