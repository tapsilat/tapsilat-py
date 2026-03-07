import pytest
from unittest.mock import patch, MagicMock
from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import (
    OrgCreateBusinessRequest,
    GetUserLimitRequest,
    SetLimitUserRequest,
    GetVposRequest,
    OrgCreateUserReq,
    OrgUserVerifyReq,
    OrgUserMobileVerifyReq
)

@pytest.fixture
def client():
    return TapsilatAPI(api_key="test_key")

@patch('tapsilat_py.client.requests.request')
def test_create_organization_business(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    req = OrgCreateBusinessRequest(
        address="Test", business_name="test", business_type=0, 
        email="a@b.c", first_name="A", identity_number="1", 
        last_name="B", phone="123", tax_number="1", 
        tax_office="office", zip_code="123"
    )
    response = client.create_organization_business(req)
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/business/create" in mock_request.call_args[0][1]


@patch('tapsilat_py.client.requests.request')
def test_get_organization_currencies(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    response = client.get_organization_currencies()
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/currencies" in mock_request.call_args[0][1]


@patch('tapsilat_py.client.requests.request')
def test_get_organization_limit_user(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    req = GetUserLimitRequest(user_id="123")
    response = client.get_organization_limit_user(req)
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/limit/user" in mock_request.call_args[0][1]


@patch('tapsilat_py.client.requests.request')
def test_set_organization_limit_user(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    req = SetLimitUserRequest(limit_id="1", user_id="123")
    response = client.set_organization_limit_user(req)
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/limit/user" in mock_request.call_args[0][1]
    assert mock_request.call_args[0][0] == "POST"

@patch('tapsilat_py.client.requests.request')
def test_get_organization_limits(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    response = client.get_organization_limits()
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/limits" in mock_request.call_args[0][1]

@patch('tapsilat_py.client.requests.request')
def test_list_organization_vpos(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    req = GetVposRequest(currency_id="TRY")
    response = client.list_organization_vpos(req)
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/list-vpos" in mock_request.call_args[0][1]


@patch('tapsilat_py.client.requests.request')
def test_get_organization_meta(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    response = client.get_organization_meta("meta_name")
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/meta/meta_name" in mock_request.call_args[0][1]

@patch('tapsilat_py.client.requests.request')
def test_get_organization_scopes(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    response = client.get_organization_scopes()
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/scopes" in mock_request.call_args[0][1]

@patch('tapsilat_py.client.requests.request')
def test_get_organization_suborganizations(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    response = client.get_organization_suborganizations(page=1, per_page=10)
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/suborganizations" in mock_request.call_args[0][1]


@patch('tapsilat_py.client.requests.request')
def test_create_organization_user(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    req = OrgCreateUserReq(
        conversation_id="1", email="a@b", first_name="A", 
        identity_number="1", is_mail_verified=True, 
        last_name="B", phone="1", reference_id="1"
    )
    response = client.create_organization_user(req)
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/user/create" in mock_request.call_args[0][1]


@patch('tapsilat_py.client.requests.request')
def test_verify_organization_user(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    req = OrgUserVerifyReq(user_id="1")
    response = client.verify_organization_user(req)
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/user/verify" in mock_request.call_args[0][1]


@patch('tapsilat_py.client.requests.request')
def test_verify_organization_user_mobile(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    mock_request.return_value = mock_response

    req = OrgUserMobileVerifyReq(user_id="1")
    response = client.verify_organization_user_mobile(req)
    assert response == {"success": True}
    mock_request.assert_called_once()
    assert "/organization/user/verify-mobile" in mock_request.call_args[0][1]
