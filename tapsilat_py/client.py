import requests
from dotenv import load_dotenv

from .exceptions import APIException
from .models import OrderCreateDTO, OrderResponse, RefundOrderDTO

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

    def create_order(self, order: OrderCreateDTO) -> OrderResponse:
        url = f"{self.base_url}/order/create"
        payload = order.to_dict()
        response = requests.post(
            url, json=payload, headers=self._get_headers(), timeout=self.timeout
        )
        if not response.ok:
            raise APIException(
                response.status_code, response.json()["code"], response.json()["error"]
            )
        json_data = response.json()
        return OrderResponse(json_data)

    def get_order(self, reference_id: str) -> OrderResponse:
        url = f"{self.base_url}/order/{reference_id}"
        response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
        if not response.ok:
            raise APIException(
                response.status_code, response.json()["code"], response.json()["error"]
            )
        json_data = response.json()
        return OrderResponse(json_data)

    def get_checkout_url(self, reference_id: str) -> str:
        response = self.get_order(reference_id)
        return response["checkout_url"]

    def cancel_order(self, reference_id: str) -> dict:
        url = f"{self.base_url}/order/cancel"
        payload = {"reference_id":reference_id}
        response = requests.post(url,json=payload, headers=self._get_headers(), timeout=self.timeout)
        if not response.ok:
            raise APIException(
                response.status_code, response.json()["code"], response.json()["error"]
            )
        return response.json()

    def refund_order(self, refund_data: RefundOrderDTO) -> dict:
        url = f"{self.base_url}/order/refund"
        payload = refund_data.to_dict()
        response = requests.post(
            url, json=payload, headers=self._get_headers(), timeout=self.timeout
        )
        if not response.ok:
            raise APIException(
                response.status_code, response.json()["code"], response.json()["error"]
            )
        return response.json()

    def refund_all_order(self, reference_id: str) -> dict:
        url = f"{self.base_url}/order/refund-all"
        payload = {"reference_id":reference_id}
        response = requests.post(
            url, json=payload, headers=self._get_headers(), timeout=self.timeout
        )
        if not response.ok:
            raise APIException(
                response.status_code, response.json()["code"], response.json()["error"]
            )
        return response.json()
