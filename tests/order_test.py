import json

import pytest
from requests.models import Response

from tapsilat_py.client import TapsilatAPI
from tapsilat_py.exceptions import APIException
from tapsilat_py.models import BuyerDTO, OrderCreateDTO


class DummyResponse(Response):
    def __init__(self, json_data, status_code):
        super().__init__()
        self._json = json_data
        self.status_code = status_code
        self._content = json.dumps(json_data).encode()

    def json(self):
        return self._json


def test_order_to_dict():
    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    order = OrderCreateDTO(
        amount=100,
        currency="TRY",
        locale="tr-TR",
        buyer=buyer,
    )

    json_data = order.to_dict()

    assert json_data["amount"] == 100
    assert json_data["currency"] == "TRY"
    assert json_data["locale"] == "tr-TR"
    assert json_data["buyer"]["name"] == "John"
    assert json_data["buyer"]["surname"] == "Doe"
    assert json_data["buyer"]["email"] == "test@example.com"


def test_create_order_success(monkeypatch):
    expected = {
        "order_id": "mock-03d03353-78bc-4432-9da6-1433ecd7fbbb",
        "reference_id": "mock-03d03353-9b5b-4289-b231-ffbe50f8a79d",
    }
    dummy = DummyResponse(expected, 200)
    monkeypatch.setattr("requests.post", lambda *a, **k: dummy)
    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    order = OrderCreateDTO(
        amount=100,
        currency="TRY",
        locale="tr",
        buyer=buyer,
    )
    client = TapsilatAPI()

    res = client.create_order(order)

    assert res["order_id"] == "mock-03d03353-78bc-4432-9da6-1433ecd7fbbb"
    assert res["reference_id"] == "mock-03d03353-9b5b-4289-b231-ffbe50f8a79d"
    assert res == expected


def test_get_order_success(monkeypatch):
    order_response = {"reference_id": "mock-03d03353-9b5b-4289-b231-ffbe50f8a79d"}
    expected_response = {
        "checkout_url": "https://checkout.tapsilat.dev?reference_id=mock-03d03353-d2be-4094-b5f6-7b7a8473534e"
    }
    dummy = DummyResponse(expected_response, 200)
    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)

    client = TapsilatAPI()
    result = client.get_order(order_response)

    assert (
        result["checkout_url"]
        == "https://checkout.tapsilat.dev?reference_id=mock-03d03353-d2be-4094-b5f6-7b7a8473534e"
    )
    assert result == expected_response


def test_get_order_reference_id_not_defined(monkeypatch):
    order_response = {"error": "ORDER_ORDER_DETAIL_ORDER_NOT_FOUND"}
    dummy = DummyResponse(
        {"code": 101160, "error": "ORDER_ORDER_DETAIL_ORDER_NOT_FOUND"}, 400
    )
    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)

    client = TapsilatAPI()

    with pytest.raises(APIException) as e:
        client.get_order(order_response)

    assert e.value.status_code == 0
    assert e.value.code == 0
    assert e.value.error == "reference_id is not defined!"


def test_get_order_failure(monkeypatch):
    order_response = {
        "order_id": "mock-03d03353-78bc-4432-9da6-1433ecd7fbbb",
        "reference_id": "mock-03d03353-9b5b-4289-b231-ffbe50f8a79d",
    }
    dummy = DummyResponse(
        {"code": 101160, "error": "ORDER_ORDER_DETAIL_ORDER_NOT_FOUND"}, 400
    )
    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)

    client = TapsilatAPI()

    with pytest.raises(APIException) as e:
        client.get_order(order_response)

    assert e.value.status_code == 400
    assert e.value.code == 101160
    assert e.value.error == "ORDER_ORDER_DETAIL_ORDER_NOT_FOUND"


def test_get_checkout_url_success(monkeypatch):
    order_response = {"reference_id": "mock-03d03353-9b5b-4289-b231-ffbe50f8a79d"}
    expected_response = {
        "checkout_url": "https://checkout.tapsilat.dev?reference_id=mock-03d03353-d2be-4094-b5f6-7b7a8473534e"
    }
    dummy = DummyResponse(expected_response, 200)
    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)

    client = TapsilatAPI()
    url = client.get_checkout_url(order_response)

    assert (
        url
        == "https://checkout.tapsilat.dev?reference_id=mock-03d03353-d2be-4094-b5f6-7b7a8473534e"
    )
