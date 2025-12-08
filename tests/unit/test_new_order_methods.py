import pytest
from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import (
    OrderCreateDTO,
    BuyerDTO,
    OrderAccountingRequest,
    OrderPostAuthRequest,
    OrderResponse,
)


@pytest.fixture
def mock_api_request(mocker):
    mock = mocker.patch.object(TapsilatAPI, "_make_request")
    return mock


def test_create_order_new_fields(mock_api_request, mocker):
    # Mock return for create_order (POST)
    mock_api_request.return_value = {"reference_id": "ref123", "order_id": "order123"}

    # Mock get_checkout_url to avoid second API call if implemented that way
    # Based on client.py, create_order calls get_checkout_url internally if reference_id is present
    mock_get_checkout_url = mocker.patch.object(TapsilatAPI, "get_checkout_url")
    mock_get_checkout_url.return_value = "https://checkout.url"

    buyer = BuyerDTO(name="John", surname="Doe")
    order_dto = OrderCreateDTO(
        amount=100.0,
        currency="TRY",
        locale="tr",
        buyer=buyer,
        payment_mode="card",
        redirect_success_url="https://example.com/success",
        redirect_failure_url="https://example.com/fail",
    )

    client = TapsilatAPI()
    client.create_order(order_dto)

    # Verify the first call (POST /order/create) contains new fields
    mock_api_request.assert_any_call(
        "POST", "/order/create", json_payload=order_dto.to_dict()
    )

    # Verify specific fields in the payload
    # We inspect the call args to be sure
    call_args = mock_api_request.call_args_list[0]
    json_payload = call_args.kwargs["json_payload"]
    assert json_payload["payment_mode"] == "card"
    assert json_payload["redirect_success_url"] == "https://example.com/success"
    assert json_payload["redirect_failure_url"] == "https://example.com/fail"


def test_order_accounting(mock_api_request):
    mock_api_request.return_value = {}

    req = OrderAccountingRequest(order_reference_id="ref123")
    client = TapsilatAPI()
    client.order_accounting(req)

    mock_api_request.assert_called_once_with(
        "POST", "/order/accounting", json_payload=req.to_dict()
    )


def test_order_postauth(mock_api_request):
    mock_api_request.return_value = {}

    req = OrderPostAuthRequest(amount=50.0, reference_id="ref123")
    client = TapsilatAPI()
    client.order_postauth(req)

    mock_api_request.assert_called_once_with(
        "POST", "/order/postauth", json_payload=req.to_dict()
    )


def test_get_system_order_statuses(mock_api_request):
    mock_api_request.return_value = {}

    client = TapsilatAPI()
    client.get_system_order_statuses()

    mock_api_request.assert_called_once_with("GET", "/system/order-statuses")
