import pytest
from unittest.mock import patch, MagicMock
from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import (
    OrderPaymentTermDeleteDTO,
    OrderPaymentTermUpdateDTO,
    TerminateRequest,
    RefundAllOrderDTO,
)

@pytest.fixture
def client():
    return TapsilatAPI(api_key="test_key")

@patch('tapsilat_py.client.requests.request')
def test_delete_order_term(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    request_dto = OrderPaymentTermDeleteDTO(order_id="123", term_reference_id="abc")
    response = client.delete_order_term(request_dto)

    assert response == {"success": True}
    mock_request.assert_called_once()
    assert mock_request.call_args[0][0] == "DELETE"
    assert "/order/term" in mock_request.call_args[0][1]


@patch('tapsilat_py.client.requests.request')
def test_update_order_term(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    request_dto = OrderPaymentTermUpdateDTO(
        amount=100.0,
        due_date="2023-12-31",
        paid_date=None,
        required=True,
        status="pending",
        term_reference_id="abc",
        term_sequence=1
    )
    response = client.update_order_term(request_dto)

    assert response == {"success": True}
    mock_request.assert_called_once()
    assert mock_request.call_args[0][0] == "PATCH"
    assert "/order/term" in mock_request.call_args[0][1]

@patch('tapsilat_py.client.requests.request')
def test_get_order_term(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"term_reference_id": "abc"}'
    mock_response.json.return_value = {"term_reference_id": "abc"}
    mock_request.return_value = mock_response

    response = client.get_order_term("abc")

    assert response == {"term_reference_id": "abc"}
    mock_request.assert_called_once()
    assert mock_request.call_args[0][0] == "GET"
    assert "/order/term" in mock_request.call_args[0][1]
    assert mock_request.call_args[1]["params"] == {"term_reference_id": "abc"}

