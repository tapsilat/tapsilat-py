import pytest
from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import (
    SubscriptionGetRequest,
    SubscriptionCancelRequest,
    SubscriptionCreateRequest,
    SubscriptionRedirectRequest,
    SubscriptionDetail,
    SubscriptionCreateResponse,
    SubscriptionRedirectResponse,
)


@pytest.fixture
def mock_api_request(mocker):
    mock = mocker.patch.object(TapsilatAPI, "_make_request")
    return mock


def test_get_subscription(mock_api_request):
    request = SubscriptionGetRequest(reference_id="sub-ref-123")
    expected_response = {
        "external_reference_id": "ext-ref-123",
        "is_active": True,
        "title": "My Subscription",
        "payment_status": "PAID",
    }
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.get_subscription(request)

    mock_api_request.assert_called_once_with(
        "POST", "/subscription", json_payload=request.to_dict()
    )
    assert isinstance(result, SubscriptionDetail)
    assert result.external_reference_id == "ext-ref-123"
    assert result.is_active is True


def test_cancel_subscription(mock_api_request):
    request = SubscriptionCancelRequest(reference_id="sub-ref-123")
    expected_response = {"success": True}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.cancel_subscription(request)

    mock_api_request.assert_called_once_with(
        "POST", "/subscription/cancel", json_payload=request.to_dict()
    )
    assert result == expected_response


def test_create_subscription(mock_api_request):
    request = SubscriptionCreateRequest(
        title="Monthly Plan",
        amount=100.0,
        currency="TRY",
        period=30,
    )
    expected_response = {
        "reference_id": "sub-ref-new",
        "code": 100,
        "message": "Success",
    }
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.create_subscription(request)

    mock_api_request.assert_called_once_with(
        "POST", "/subscription/create", json_payload=request.to_dict()
    )
    assert isinstance(result, SubscriptionCreateResponse)
    assert result.reference_id == "sub-ref-new"


def test_list_subscriptions(mock_api_request):
    expected_response = {"page": 1, "per_page": 10, "items": [], "total": 0}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.list_subscriptions(page=1, per_page=10)

    mock_api_request.assert_called_once_with(
        "GET", "/subscription/list", params={"page": 1, "per_page": 10}
    )
    assert result == expected_response


def test_redirect_subscription(mock_api_request):
    request = SubscriptionRedirectRequest(subscription_id="sub-ref-123")
    expected_response = {"url": "https://redirect.example.com"}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.redirect_subscription(request)

    mock_api_request.assert_called_once_with(
        "POST", "/subscription/redirect", json_payload=request.to_dict()
    )
    assert isinstance(result, SubscriptionRedirectResponse)
    assert result.url == "https://redirect.example.com"
