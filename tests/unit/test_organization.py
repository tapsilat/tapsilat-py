import pytest
from tapsilat_py.client import TapsilatAPI


@pytest.fixture
def mock_api_request(mocker):
    mock = mocker.patch.object(TapsilatAPI, "_make_request")
    return mock


def test_get_organization_settings(mock_api_request):
    expected_response = {"name": "My Org", "settings": {}}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.get_organization_settings()

    mock_api_request.assert_called_once_with("GET", "/organization/settings")
    assert result == expected_response
