import pytest
from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import SubmerchantCreateDTO, SubmerchantUpdateDTO

@pytest.fixture
def mock_api_request(mocker):
    return mocker.patch("tapsilat_py.client.TapsilatAPI._make_request")

def test_create_submerchant(mock_api_request):
    mock_api_request.return_value = {}
    client = TapsilatAPI()
    req = SubmerchantCreateDTO(name="Test")
    client.create_submerchant(req)
    mock_api_request.assert_called_once_with("POST", "/submerchants", json_payload=req.to_dict())

def test_get_submerchant(mock_api_request):
    mock_api_request.return_value = {}
    client = TapsilatAPI()
    client.get_submerchant("123")
    mock_api_request.assert_called_once_with("GET", "/submerchants/123")

def test_get_suborganization_by_submerchant(mock_api_request):
    mock_api_request.return_value = {}
    client = TapsilatAPI()
    client.get_suborganization_by_submerchant("123")
    mock_api_request.assert_called_once_with("GET", "/submerchants/123/suborganization")

def test_update_submerchant(mock_api_request):
    mock_api_request.return_value = {}
    client = TapsilatAPI()
    req = SubmerchantUpdateDTO(name="Updated")
    client.update_submerchant("123", req)
    mock_api_request.assert_called_once_with("PATCH", "/submerchants/123", json_payload=req.to_dict())

def test_delete_submerchant(mock_api_request):
    mock_api_request.return_value = {}
    client = TapsilatAPI()
    client.delete_submerchant("123")
    mock_api_request.assert_called_once_with("DELETE", "/submerchants/123")

def test_list_submerchants(mock_api_request):
    mock_api_request.return_value = {}
    client = TapsilatAPI()
    client.list_submerchants(1, 10)
    mock_api_request.assert_called_once_with("GET", "/submerchants", params={"page": 1, "per_page": 10})
