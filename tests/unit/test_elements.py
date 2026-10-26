import dataclasses
import json
import pprint
from unittest.mock import MagicMock, patch

import pytest

from tapsilat_py import (
    APIException,
    ElementsCardBrand,
    ElementsCardSummary,
    ElementsLastError,
    ElementsMode,
    ElementsPurpose,
    ElementsSession,
    ElementsSessionCreateRequest,
    ElementsSessionWithSecret,
    ElementsStatus,
    TapsilatAPI,
)

BASE = "https://panel.test/api/v1"
SECRET = "es_test_8Kq2nV0rX4_secret_q8Zr0bM1"


def make_response(status=200, body="{}", content_type="application/json"):
    response = MagicMock()
    response.status_code = status
    response.content = body.encode() if isinstance(body, str) else body
    response.headers = {"Content-Type": content_type, "Cache-Control": "no-store"}
    response.reason = "Error"
    response.json.side_effect = lambda: json.loads(response.content)
    return response


@pytest.fixture
def client():
    return TapsilatAPI(api_key="token_123", base_url=BASE)


@pytest.fixture
def mock_request():
    with patch("tapsilat_py.client.requests.request") as mock:
        yield mock


def sent(mock_request):
    """Returns (method, url, headers, kwargs) of the last request"""
    args, kwargs = mock_request.call_args
    return args[0], args[1], kwargs["headers"], kwargs


def test_constants():
    assert (ElementsPurpose.TOKENIZE, ElementsPurpose.PAY) == ("tokenize", "pay")
    assert (ElementsMode.SECURE, ElementsMode.HALF_SECURE, ElementsMode.NON_SECURE) == (1, 2, 3)
    assert ElementsStatus.REQUIRES_PAYMENT_METHOD == "requires_payment_method"
    assert ElementsStatus.SUCCEEDED == "succeeded"
    assert ElementsStatus.CANCELED == "canceled"
    assert ElementsCardBrand.VISA == "visa"
    assert ElementsCardBrand.UNKNOWN == "unknown"


def test_create_pay_session(mock_request, client):
    mock_request.return_value = make_response(200, json.dumps({
        "id": "es_test_8Kq2nV0rX4",
        "purpose": "pay",
        "status": "requires_payment_method",
        "order_reference_id": "order-ref-1",
        "attempts": 0,
        "max_attempts": 3,
        "created_at": "2026-10-22T09:00:00Z",
        "expires_at": "2026-10-22T09:30:00Z",
        "client_secret": SECRET,
        "elements_base_url": "https://checkout.tapsilat.dev",
    }))

    session = client.create_elements_session(ElementsSessionCreateRequest(
        purpose=ElementsPurpose.PAY,
        order_reference_id="order-ref-1",
        save_card=True,
    ))

    method, url, headers, kwargs = sent(mock_request)
    assert method == "POST"
    assert url == f"{BASE}/elements/sessions"
    assert headers["Authorization"] == "Bearer token_123"
    assert kwargs["json"] == {"purpose": "pay", "order_reference_id": "order-ref-1", "save_card": True}

    assert isinstance(session, ElementsSessionWithSecret)
    assert session.id == "es_test_8Kq2nV0rX4"
    assert session.purpose == ElementsPurpose.PAY
    assert session.status == ElementsStatus.REQUIRES_PAYMENT_METHOD
    assert session.order_reference_id == "order-ref-1"
    assert session.attempts == 0
    assert session.max_attempts == 3
    assert session.created_at == "2026-10-22T09:00:00Z"
    assert session.expires_at == "2026-10-22T09:30:00Z"
    assert session.completed_at is None
    assert session.user_id is None
    assert session.card is None
    assert session.last_error is None
    assert session.client_secret == SECRET
    assert session.elements_base_url == "https://checkout.tapsilat.dev"


def test_create_tokenize_session(mock_request, client):
    mock_request.return_value = make_response(
        200,
        '{"id":"es_test_1","purpose":"tokenize","status":"requires_payment_method",'
        '"user_id":"user_123","client_secret":"es_test_1_secret_x"}',
    )

    session = client.create_elements_session(ElementsSessionCreateRequest(
        purpose=ElementsPurpose.TOKENIZE,
        user_id="user_123",
        user_email="john@doe.com",
        mode=ElementsMode.NON_SECURE,
    ))

    assert sent(mock_request)[3]["json"] == {
        "purpose": "tokenize",
        "user_id": "user_123",
        "user_email": "john@doe.com",
        "mode": 3,
    }
    assert session.purpose == ElementsPurpose.TOKENIZE
    assert session.user_id == "user_123"
    assert session.client_secret == "es_test_1_secret_x"
    assert session.elements_base_url is None


def test_secret_is_redacted_when_printed_but_kept_in_to_dict():
    session = ElementsSessionWithSecret(
        id="es_test_1", status=ElementsStatus.REQUIRES_PAYMENT_METHOD, client_secret="es_test_1_secret_x"
    )

    for printed in (repr(session), str(session), f"{session}", "%s" % (session,), pprint.pformat(session)):
        assert "es_test_1_secret_x" not in printed
        assert "es_test_1" in printed
        assert "requires_payment_method" in printed

    assert session.to_dict()["client_secret"] == "es_test_1_secret_x"
    assert '"client_secret": "es_test_1_secret_x"' in json.dumps(session.to_dict())
    assert dataclasses.asdict(session)["client_secret"] == "es_test_1_secret_x"


def test_get_session_with_card_and_last_error(mock_request, client):
    mock_request.return_value = make_response(200, json.dumps({
        "id": "es_test_8Kq2nV0rX4",
        "purpose": "pay",
        "status": "failed",
        "order_reference_id": "order-ref-1",
        "attempts": 3,
        "max_attempts": 3,
        "completed_at": "2026-10-22T09:12:00Z",
        "card": {"id": "card-1", "brand": "visa", "last4": "4242", "exp_month": 12, "exp_year": 2030},
        "last_error": {"code": "card_declined", "message": "The card was declined.", "retryable": False},
    }))

    session = client.get_elements_session("es_test_8Kq2nV0rX4")

    method, url, headers, kwargs = sent(mock_request)
    assert method == "GET"
    assert url == f"{BASE}/elements/sessions/es_test_8Kq2nV0rX4"
    assert headers["Authorization"] == "Bearer token_123"
    assert kwargs.get("json") is None
    assert kwargs.get("data") is None

    assert type(session) is ElementsSession
    assert session.status == ElementsStatus.FAILED
    assert session.attempts == 3
    assert session.completed_at == "2026-10-22T09:12:00Z"
    assert session.card == ElementsCardSummary(
        id="card-1", brand=ElementsCardBrand.VISA, last4="4242", exp_month=12, exp_year=2030
    )
    assert session.last_error == ElementsLastError(
        code="card_declined", message="The card was declined.", retryable=False
    )


def test_get_session_with_null_card_and_last_error(mock_request, client):
    mock_request.return_value = make_response(
        200,
        '{"id":"es_mock_1","purpose":"pay","status":"requires_payment_method","card":null,"last_error":null}',
    )

    session = client.get_elements_session("es_mock_1")

    assert session.id == "es_mock_1"
    assert session.card is None
    assert session.last_error is None


def test_get_session_ignores_unknown_fields_and_values(mock_request, client):
    mock_request.return_value = make_response(200, json.dumps({
        "id": "es_test_1",
        "purpose": "subscribe",
        "status": "requires_review",
        "risk_score": 12,
        "card": {"brand": "elo", "last4": "1234", "issuer": "Bank"},
        "last_error": {"code": "new_code", "message": "m", "details": {}},
    }))

    session = client.get_elements_session("es_test_1")

    assert session.purpose == "subscribe"
    assert session.status == "requires_review"
    assert session.card == ElementsCardSummary(brand="elo", last4="1234")
    assert session.last_error == ElementsLastError(code="new_code", message="m")


def test_cancel_session(mock_request, client):
    mock_request.return_value = make_response(
        200, '{"id":"es_test_8Kq2nV0rX4","purpose":"pay","status":"canceled","attempts":0,"max_attempts":3}'
    )

    session = client.cancel_elements_session("es_test_8Kq2nV0rX4")

    method, url, headers, kwargs = sent(mock_request)
    assert method == "POST"
    assert url == f"{BASE}/elements/sessions/es_test_8Kq2nV0rX4/cancel"
    assert headers["Authorization"] == "Bearer token_123"
    assert kwargs.get("json") is None
    assert kwargs.get("data") is None
    assert session.status == ElementsStatus.CANCELED
    assert session.max_attempts == 3


def test_session_id_is_path_escaped(mock_request, client):
    mock_request.return_value = make_response(200, '{"id":"es_test_1"}')

    client.get_elements_session("es_test_1/../x")
    assert sent(mock_request)[1] == f"{BASE}/elements/sessions/es_test_1%2F..%2Fx"

    client.cancel_elements_session("es_test_1/../x")
    assert sent(mock_request)[1] == f"{BASE}/elements/sessions/es_test_1%2F..%2Fx/cancel"


def test_empty_session_id_is_rejected(mock_request, client):
    with pytest.raises(ValueError):
        client.get_elements_session("")
    with pytest.raises(ValueError):
        client.cancel_elements_session("")
    mock_request.assert_not_called()


@pytest.mark.parametrize(
    "status, body, call, code, message, retryable",
    [
        (
            403,
            '{"error":{"code":"elements_not_enabled","message":"Elements is not enabled for this organization"}}',
            lambda api: api.create_elements_session(ElementsSessionCreateRequest(purpose=ElementsPurpose.PAY)),
            "elements_not_enabled",
            "Elements is not enabled for this organization",
            False,
        ),
        (
            404,
            '{"error":{"code":"session_not_found","message":"session not found","retryable":false}}',
            lambda api: api.get_elements_session("es_test_missing"),
            "session_not_found",
            "session not found",
            False,
        ),
        (
            503,
            '{"error":{"code":"unavailable","message":"try again","retryable":true}}',
            lambda api: api.cancel_elements_session("es_test_1"),
            "unavailable",
            "try again",
            True,
        ),
    ],
    ids=["create_not_enabled", "get_not_found", "cancel_unavailable"],
)
def test_nested_errors(mock_request, client, status, body, call, code, message, retryable):
    mock_request.return_value = make_response(status, body)

    with pytest.raises(APIException) as error:
        call(client)

    assert error.value.status_code == status
    assert error.value.code == code
    assert error.value.error == message
    assert error.value.message == message
    assert error.value.retryable is retryable
    assert error.value.raw_body == body
    assert f"code:{code}" in str(error.value)
    assert f"error:{message}" in str(error.value)
    assert "{" not in str(error.value)


def test_flat_errors_are_not_retryable(mock_request, client):
    mock_request.return_value = make_response(400, '{"error":"bad request","code":9}')

    with pytest.raises(APIException) as error:
        client.get_elements_session("es_test_1")

    assert error.value.code == 9
    assert error.value.error == "bad request"
    assert error.value.retryable is False
