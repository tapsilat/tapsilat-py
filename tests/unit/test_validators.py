import pytest

from tapsilat_py.exceptions import APIException
from tapsilat_py.validators import validate_gsm_number, validate_installments


class TestValidateInstallments:
    def test_empty_string_returns_default(self):
        result = validate_installments("")
        assert result == [1]

    def test_none_returns_default(self):
        result = validate_installments(None) # type: ignore
        assert result == [1]

    def test_valid_single_installment(self):
        result = validate_installments("3")
        assert result == [3]

    def test_valid_multiple_installments(self):
        result = validate_installments("1,2,3,6")
        assert result == [1, 2, 3, 6]

    def test_valid_with_spaces(self):
        result = validate_installments("1, 2, 3, 6")
        assert result == [1, 2, 3, 6]

    def test_installment_value_too_low(self):
        with pytest.raises(APIException) as exc_info:
            validate_installments("0,2,3")
        assert exc_info.value.code == 0

    def test_installment_value_too_high(self):
        with pytest.raises(APIException) as exc_info:
            validate_installments("1,15,3")
        assert exc_info.value.code == 0

    def test_invalid_format_letters(self):
        with pytest.raises(APIException) as exc_info:
            validate_installments("1,abc,3")
        assert exc_info.value.code == 0

    def test_invalid_format_mixed(self):
        with pytest.raises(APIException) as exc_info:
            validate_installments("1,2.5,3")
        assert exc_info.value.code == 0


class TestValidateGsmNumber:
    def test_empty_string_returns_empty(self):
        result = validate_gsm_number("")
        assert result == ""

    def test_none_returns_none(self):
        result = validate_gsm_number(None) # type: ignore
        assert result is None

    def test_valid_international_plus_format(self):
        result = validate_gsm_number("+905551234567")
        assert result == "+905551234567"

    def test_valid_international_00_format(self):
        result = validate_gsm_number("00905551234567")
        assert result == "00905551234567"

    def test_valid_national_format(self):
        result = validate_gsm_number("05551234567")
        assert result == "05551234567"

    def test_valid_local_format(self):
        result = validate_gsm_number("5551234567")
        assert result == "5551234567"

    def test_removes_formatting_characters(self):
        result = validate_gsm_number("+90 555 123-45(67)")
        assert result == "+905551234567"

    def test_international_plus_too_short(self):
        with pytest.raises(APIException) as exc_info:
            validate_gsm_number("+90123")
        assert exc_info.value.code == 0
        assert "too short" in exc_info.value.error

    def test_international_00_too_short(self):
        with pytest.raises(APIException) as exc_info:
            validate_gsm_number("0090123")
        assert exc_info.value.code == 0
        assert "too short" in exc_info.value.error

    def test_national_too_short(self):
        with pytest.raises(APIException) as exc_info:
            validate_gsm_number("012345")
        assert exc_info.value.code == 0
        assert "too short" in exc_info.value.error

    def test_local_too_short(self):
        with pytest.raises(APIException) as exc_info:
            validate_gsm_number("12345")
        assert exc_info.value.code == 0
        assert "too short" in exc_info.value.error

    def test_invalid_characters(self):
        with pytest.raises(APIException) as exc_info:
            validate_gsm_number("+90abc1234567")
        assert exc_info.value.code == 0
        assert "Invalid phone number format" in exc_info.value.error

    def test_only_special_characters(self):
        with pytest.raises(APIException) as exc_info:
            validate_gsm_number("+++---")
        assert exc_info.value.code == 0
