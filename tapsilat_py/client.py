import os
from dotenv import load_dotenv
import requests
from .exceptions import APIException
from .models import OrderCreateDTO
import json

load_dotenv()


class TapsilatAPI:
    def __init__(
        self,
        api_key: str = "",
        timeout: int = 10,
        base_url: str = "https://acquiring.tapsilat.dev/api/v1",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _get_headers(self):
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def create_order(self, order: OrderCreateDTO) -> dict:
        url = f"{self.base_url}/order/create"
        payload = order.to_dict()
        response = requests.post(
            url, json=payload, headers=self._get_headers(), timeout=self.timeout
        )
        if not response.ok:
            raise APIException(
                response.status_code, response.json()["code"], response.json()["error"]
            )
        return response.json()

    def get_order(self, order_response: dict) -> dict:
        if "reference_id" not in order_response:
            raise APIException(0, 0, "reference_id is not defined!")
        url = f"{self.base_url}/order/{order_response['reference_id']}"
        response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
        if not response.ok:
            raise APIException(
                response.status_code, response.json()["code"], response.json()["error"]
            )
        return response.json()

    def get_checkout_url(self, order_response: dict) -> str:
        response = self.get_order(order_response)
        return response["checkout_url"]
