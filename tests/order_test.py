from dataclasses import asdict

import pytest

from tapsilat_py.client import TapsilatAPI
from tapsilat_py.exceptions import APIException
from tapsilat_py.models import (
    BasketItemDTO,
    BasketItemPayerDTO,
    BillingAddressDTO,
    BuyerDTO,
    CheckoutDesignDTO,
    MetadataDTO,
    OrderCardDTO,
    OrderCreateDTO,
    OrderPaymentTermCreateDTO,
    OrderPaymentTermUpdateDTO,
    OrderPFSubMerchantDTO,
    OrderResponse,
    PaymentTermDTO,
    RefundOrderDTO,
    ShippingAddressDTO,
    SubmerchantDTO,
    SubOrganizationDTO,
)


@pytest.fixture
def mock_api_request(mocker):
    mock = mocker.patch.object(TapsilatAPI, "_make_request")
    return mock


def test_order_to_dict():
    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    order = OrderCreateDTO(
        amount=100,
        currency="TRY",
        locale="tr",
        buyer=buyer,
    )
    json_data = order.to_dict()
    assert json_data["amount"] == 100
    assert json_data["currency"] == "TRY"
    assert json_data["locale"] == "tr"
    assert json_data["buyer"]["name"] == "John"
    assert json_data["buyer"]["surname"] == "Doe"
    assert json_data["buyer"]["email"] == "test@example.com"


def test_basket_item_payer_dto_asdict():
    payer = BasketItemPayerDTO(
        address="uskudar", type="PERSONAL", reference_id="123456789"
    )
    payer_dict = asdict(payer)
    assert payer_dict["address"] == "uskudar"
    assert payer_dict["type"] == "PERSONAL"
    assert payer_dict["reference_id"] == "123456789"
    assert payer_dict["tax_office"] is None


def test_basket_item_dto_asdict():
    payer_data = BasketItemPayerDTO(address="uskudar", type="BUSINESS")
    item = BasketItemDTO(
        id="BI101",
        name="Binocular",
        price=19.99,
        quantity=1,
        item_type="PHYSICAL",
        payer=payer_data,
    )
    item_dict = asdict(item)
    assert item_dict["id"] == "BI101"
    assert item_dict["name"] == "Binocular"
    assert item_dict["price"] == 19.99
    assert item_dict["quantity"] == 1
    assert item_dict["item_type"] == "PHYSICAL"
    assert item_dict["payer"]["address"] == "uskudar"
    assert item_dict["payer"]["type"] == "BUSINESS"
    assert item_dict["category1"] is None


def test_billing_address_dto_asdict():
    billing = BillingAddressDTO(
        address="uskudar", city="Istanbul", country="TR", contact_name="Jane Doe"
    )
    billing_dict = asdict(billing)
    assert billing_dict["address"] == "uskudar"
    assert billing_dict["city"] == "Istanbul"
    assert billing_dict["country"] == "TR"
    assert billing_dict["contact_name"] == "Jane Doe"
    assert billing_dict["zip_code"] is None


def test_checkout_design_dto_asdict():
    design = CheckoutDesignDTO(
        pay_button_color="#FF0000", logo="http://example.com/logo.png"
    )
    design_dict = asdict(design)
    assert design_dict["pay_button_color"] == "#FF0000"
    assert design_dict["logo"] == "http://example.com/logo.png"
    assert design_dict["input_background_color"] is None


def test_metadata_dto_asdict():
    meta = MetadataDTO(key="key", value="value")
    meta_dict = asdict(meta)
    assert meta_dict["key"] == "key"
    assert meta_dict["value"] == "value"


def test_order_card_dto_asdict():
    card = OrderCardDTO(card_id="123456789", card_sequence=1)
    card_dict = asdict(card)
    assert card_dict["card_id"] == "123456789"
    assert card_dict["card_sequence"] == 1


def test_payment_term_dto_asdict():
    term = PaymentTermDTO(
        amount=50.0, due_date="2025-10-21T23:59:59Z", status="PENDING", term_sequence=1
    )
    term_dict = asdict(term)
    assert term_dict["amount"] == 50.0
    assert term_dict["due_date"] == "2025-10-21T23:59:59Z"
    assert term_dict["status"] == "PENDING"
    assert term_dict["term_sequence"] == 1
    assert term_dict["data"] is None


def test_order_pf_sub_merchant_dto_asdict():
    pf_sub = OrderPFSubMerchantDTO(id="123456789", name="John Doe", mcc="1234")
    pf_sub_dict = asdict(pf_sub)
    assert pf_sub_dict["id"] == "123456789"
    assert pf_sub_dict["name"] == "John Doe"
    assert pf_sub_dict["mcc"] == "1234"
    assert pf_sub_dict["address"] is None


def test_shipping_address_dto_asdict():
    shipping = ShippingAddressDTO(
        address="uskudar", city="Istanbul", country="Turkey", contact_name="Jane Doe"
    )
    shipping_dict = asdict(shipping)
    assert shipping_dict["address"] == "uskudar"
    assert shipping_dict["city"] == "Istanbul"
    assert shipping_dict["country"] == "Turkey"
    assert shipping_dict["contact_name"] == "Jane Doe"


def test_sub_organization_dto_asdict():
    sub_org = SubOrganizationDTO(
        organization_name="ACME Inc.",
        sub_merchant_key="sub merchant key",
        legal_company_title="ACME Inc.",
    )
    sub_org_dict = asdict(sub_org)
    assert sub_org_dict["organization_name"] == "ACME Inc."
    assert sub_org_dict["sub_merchant_key"] == "sub merchant key"
    assert sub_org_dict["legal_company_title"] == "ACME Inc."
    assert sub_org_dict["acquirer"] is None


def test_submerchant_dto_asdict():
    submerchant = SubmerchantDTO(
        amount=20.49,
        merchant_reference_id="merchant reference id",
        order_basket_item_id="BI101",
    )
    submerchant_dict = asdict(submerchant)
    assert submerchant_dict["amount"] == 20.49
    assert submerchant_dict["merchant_reference_id"] == "merchant reference id"
    assert submerchant_dict["order_basket_item_id"] == "BI101"


def test_refund_order_dto_to_dict():
    dto = RefundOrderDTO(amount=50.0, reference_id="ref123", order_item_id="item001")
    dto_dict = dto.to_dict()
    assert dto_dict["amount"] == 50.0
    assert dto_dict["reference_id"] == "ref123"
    assert dto_dict["order_item_id"] == "item001"

    dto_full = RefundOrderDTO(
        amount=100.0,
        reference_id="ref456",
        order_item_id="item002",
        order_item_payment_id="payment002",
    )
    dto_full_dict = dto_full.to_dict()
    assert dto_full_dict["amount"] == 100.0
    assert dto_full_dict["reference_id"] == "ref456"
    assert dto_full_dict["order_item_id"] == "item002"
    assert dto_full_dict["order_item_payment_id"] == "payment002"


def test_create_order_success(mock_api_request):
    expected_api_json_response = {
        "order_id": "mock-03d03353-78bc-4432-9da6-1433ecd7fbbb",
        "reference_id": "mock-03d03353-9b5b-4289-b231-ffbe50f8a79d",
    }
    mock_api_request.return_value = expected_api_json_response

    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    order_payload_dto = OrderCreateDTO(
        amount=100,
        currency="TRY",
        locale="tr",
        buyer=buyer,
    )
    client = TapsilatAPI()
    order_response_obj = client.create_order(order_payload_dto)

    mock_api_request.assert_called_once_with(
        "POST", "/order/create", json_payload=order_payload_dto.to_dict()
    )
    assert isinstance(order_response_obj, OrderResponse)
    assert order_response_obj.order_id == expected_api_json_response["order_id"]
    assert order_response_obj.reference_id == expected_api_json_response["reference_id"]


def test_create_order_with_basket_items(mock_api_request):
    expected_api_json_response = {
        "order_id": "order_basket",
        "reference_id": "ref_basket",
    }
    mock_api_request.return_value = expected_api_json_response

    buyer_data = BuyerDTO(name="Test", surname="User")
    basket_item1_payer = BasketItemPayerDTO(reference_id="payer_ref0_item1")
    basket_item1 = BasketItemDTO(
        id="B001", name="Item 1", price=10.0, quantity=1, payer=basket_item1_payer
    )
    basket_item2 = BasketItemDTO(
        id="B002",
        name="Item 2",
        price=20.49,
        quantity=2,
        payer=BasketItemPayerDTO(reference_id="payer_ref1_item2"),
    )

    order_payload_dto = OrderCreateDTO(
        amount=50.98,
        currency="TRY",
        locale="tr",
        buyer=buyer_data,
        basket_items=[basket_item1, basket_item2],
    )
    client = TapsilatAPI()
    api_response = client.create_order(order_payload_dto)

    mock_api_request.assert_called_once_with(
        "POST", "/order/create", json_payload=order_payload_dto.to_dict()
    )
    assert api_response.order_id == expected_api_json_response["order_id"]


def test_get_order_success(mock_api_request):
    reference_id = "mock-03d03353-9b5b-4289-b231-ffbe50f8a79d"
    expected_api_json_response = {
        "checkout_url": "https://checkout.test.dev?reference_id=mock-03d03353-d2be-4094-b5f6-7b7a8473534e",
        "status": 8,
        "reference_id": reference_id,
    }
    mock_api_request.return_value = expected_api_json_response

    client = TapsilatAPI()
    result = client.get_order(reference_id)

    mock_api_request.assert_called_once_with("GET", f"/order/{reference_id}")
    assert isinstance(result, OrderResponse)
    assert result.checkout_url == expected_api_json_response["checkout_url"]
    assert result.get("status") == expected_api_json_response["status"]


def test_get_order_failure(mock_api_request):
    reference_id = "mock-failed-reference-id"
    api_error_content = {"code": 101160, "error": "ORDER_ORDER_DETAIL_ORDER_NOT_FOUND"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.get_order(reference_id)

    mock_api_request.assert_called_once_with("GET", f"/order/{reference_id}")
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_get_order_by_conversation_id_success(mock_api_request):
    conversation_id = "mock-conversation-id"
    expected_api_json_response = {
        "checkout_url": "https://checkout.test.dev?reference_id=mock-03d03353-d2be-4094-b5f6-7b7a8473534e",
        "status": 8,
    }
    mock_api_request.return_value = expected_api_json_response

    client = TapsilatAPI()
    result = client.get_order_by_conversation_id(conversation_id)

    mock_api_request.assert_called_once_with(
        "GET", f"/order/conversation/{conversation_id}"
    )
    assert isinstance(result, OrderResponse)
    assert result.checkout_url == expected_api_json_response["checkout_url"]


def test_get_order_by_conversation_id_failure(mock_api_request):
    conversation_id = "mock-conversation-id"
    api_error_content = {"code": 101160, "error": "ORDER_ORDER_DETAIL_ORDER_NOT_FOUND"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.get_order_by_conversation_id(conversation_id)

    mock_api_request.assert_called_once_with(
        "GET", f"/order/conversation/{conversation_id}"
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_get_order_list(mock_api_request):
    page = 1
    per_page = 3
    expected_api_json_response = {
        "page": 1,
        "per_page": 3,
        "rows": [{}, {}, {}],
        "total": 24,
        "total_page": 8,
    }
    mock_api_request.return_value = expected_api_json_response

    client = TapsilatAPI()
    result = client.get_order_list(page=page, per_page=per_page)

    expected_params = {"page": page, "per_page": per_page}
    mock_api_request.assert_called_once_with(
        "GET", "/order/list", params=expected_params
    )
    assert result == expected_api_json_response


def test_get_order_submerchants(mock_api_request):
    page = 1
    per_page = 2
    expected_api_json_response = {
        "page": 1,
        "per_page": 2,
        "row": [{}, {}],
        "total": 10,
        "total_pages": 5,
    }
    mock_api_request.return_value = expected_api_json_response

    client = TapsilatAPI()
    result = client.get_order_submerchants(page=page, per_page=per_page)

    expected_params = {"page": page, "per_page": per_page}
    mock_api_request.assert_called_once_with(
        "GET", "/order/submerchants", params=expected_params
    )
    assert result == expected_api_json_response


def test_get_checkout_url_success(mock_api_request):
    reference_id = "mock-ref-for-checkout"
    expected_checkout_url = (
        "https://checkout.test.dev?reference_id=mock-checkout-url-generated"
    )
    get_order_api_json_response = {
        "checkout_url": expected_checkout_url,
        "status": "Waiting for payment",
        "reference_id": reference_id,
    }
    mock_api_request.return_value = OrderResponse(get_order_api_json_response)

    client = TapsilatAPI()
    mock_api_request.return_value = get_order_api_json_response

    checkout_url_result = client.get_checkout_url(reference_id)

    mock_api_request.assert_called_once_with("GET", f"/order/{reference_id}")
    assert checkout_url_result == expected_checkout_url


def test_cancel_order_not_found(mock_api_request):
    reference_id = "mock-reference-id"
    api_error_content = {
        "code": 101550,
        "error": "ORDER_CANCEL_ORDER_GET_ORDER_NOT_FOUND",
    }
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.cancel_order(reference_id)

    expected_payload = {"reference_id": reference_id}
    mock_api_request.assert_called_once_with(
        "POST", "/order/cancel", json_payload=expected_payload
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_cancel_order_success(mock_api_request):
    reference_id = "mock-reference-id"
    expected_api_json_response = {
        "is_success": True,
        "error": "ORDER_CANCEL_SUCCESS",
        "status": "101645",
    }
    mock_api_request.return_value = expected_api_json_response

    client = TapsilatAPI()
    api_response = client.cancel_order(reference_id)

    expected_payload = {"reference_id": reference_id}
    mock_api_request.assert_called_once_with(
        "POST", "/order/cancel", json_payload=expected_payload
    )
    assert api_response == expected_api_json_response


def test_refund_order_success(mock_api_request):
    expected_api_json_response = {"is_success": True, "error": "REFUND_SUCCESSFUL"}
    mock_api_request.return_value = expected_api_json_response

    refund_payload_dto = RefundOrderDTO(amount=50.0, reference_id="mock-reference-id")
    client = TapsilatAPI()
    api_response = client.refund_order(refund_payload_dto)

    mock_api_request.assert_called_once_with(
        "POST", "/order/refund", json_payload=refund_payload_dto.to_dict()
    )
    assert api_response == expected_api_json_response


def test_refund_order_failure(mock_api_request):
    api_error_content = {"code": 201010, "error": "REFUND_VALIDATION_ERROR"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    refund_payload_dto = RefundOrderDTO(amount=0, reference_id="order_ref_invalid")
    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.refund_order(refund_payload_dto)

    mock_api_request.assert_called_once_with(
        "POST", "/order/refund", json_payload=refund_payload_dto.to_dict()
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_refund_all_order_success(mock_api_request):
    reference_id = "order_ref_xyz"
    expected_api_json_response = {"is_success": True, "error": "REFUND_ALL_SUCCESSFUL"}
    mock_api_request.return_value = expected_api_json_response

    client = TapsilatAPI()
    api_response = client.refund_all_order(reference_id)

    expected_payload = {"reference_id": reference_id}
    mock_api_request.assert_called_once_with(
        "POST", "/order/refund-all", json_payload=expected_payload
    )
    assert api_response == expected_api_json_response


def test_refund_all_order_failure(mock_api_request):
    reference_id = "order_ref_nonexistent"
    api_error_content = {"code": 201020, "error": "ORDER_NOT_FOUND_FOR_REFUND_ALL"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.refund_all_order(reference_id)

    expected_payload = {"reference_id": reference_id}
    mock_api_request.assert_called_once_with(
        "POST", "/order/refund-all", json_payload=expected_payload
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_get_order_payment_details_success_with_ref_id(mock_api_request):
    reference_id = "mock-reference-id"
    expected_response = {"id": "mock-payment-details-id"}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.get_order_payment_details(reference_id=reference_id)

    mock_api_request.assert_called_once_with(
        "GET", f"/order/{reference_id}/payment-details"
    )
    assert result == expected_response


def test_get_order_payment_details_success_with_conv_id(mock_api_request):
    reference_id = "mock-reference-id"
    conversation_id = "mock-conversation-id"
    expected_response = {"id": "mock-payment-details-id-conv"}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.get_order_payment_details(
        reference_id=reference_id, conversation_id=conversation_id
    )

    expected_payload = {
        "conversation_id": conversation_id,
        "reference_id": reference_id,
    }
    mock_api_request.assert_called_once_with(
        "POST", "/order/payment-details", json_payload=expected_payload
    )
    assert result == expected_response


def test_get_order_payment_details_not_found(mock_api_request):
    reference_id = "mock-reference-id"
    api_error_content = {
        "code": 101230,
        "error": "ORDER_ORDER_PAYMENT_DETAIL_ORDER_DETAIL_NOT_FOUND",
    }
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.get_order_payment_details(reference_id=reference_id)

    mock_api_request.assert_called_once_with(
        "GET", f"/order/{reference_id}/payment-details"
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_get_order_status_success(mock_api_request):
    reference_id = "mock-reference-id"
    expected_response = {"status": "Refunded"}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.get_order_status(reference_id)

    mock_api_request.assert_called_once_with("GET", f"/order/{reference_id}/status")
    assert result == expected_response


def test_get_order_status_not_found(mock_api_request):
    reference_id = "mock-reference-id"
    api_error_content = {"code": 100810, "error": "ORDER_GET_NOT_FOUND"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.get_order_status(reference_id)

    mock_api_request.assert_called_once_with("GET", f"/order/{reference_id}/status")
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_get_order_transactions_success(mock_api_request):
    reference_id = "mock-reference-id"
    expected_response = [{"id": "mock-transaction-1"}]
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.get_order_transactions(reference_id)

    mock_api_request.assert_called_once_with(
        "GET", f"/order/{reference_id}/transactions"
    )
    assert result == expected_response


def test_get_order_transactions_not_found(mock_api_request):
    reference_id = "mock-reference-id"
    api_error_content = {
        "code": 101260,
        "error": "ORDER_GET_ORDER_TXS_GET_ORDER_NOT_FOUND",
    }
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.get_order_transactions(reference_id)

    mock_api_request.assert_called_once_with(
        "GET", f"/order/{reference_id}/transactions"
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_get_order_term_success(mock_api_request):
    term_reference_id = "mock-term-ref-id"
    expected_response = {
        "term_sequence": 1,
        "amount": 100,
        "status": "PENDING",
        "due_date": {"seconds": 1760486400},
    }
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.get_order_term(term_reference_id)

    expected_params = {"term_reference_id": term_reference_id}
    mock_api_request.assert_called_once_with(
        "GET", "/order/term", params=expected_params
    )
    assert result == expected_response


def test_get_order_term_failure(mock_api_request):
    term_reference_id = "mock-none-term-ref-id"
    api_error_content = {"code": 313010, "error": "ORDER_GET_PAYMENT_TERM_NOT_FOUND"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.get_order_term(term_reference_id)

    expected_params = {"term_reference_id": term_reference_id}
    mock_api_request.assert_called_once_with(
        "GET", "/order/term", params=expected_params
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_create_order_term_success(mock_api_request):
    payload_dto = OrderPaymentTermCreateDTO(
        order_id="order123",
        term_reference_id="term-ref-create",
        amount=200,
        due_date="2025-10-10 00:00:00",
        term_sequence=2,
        required=False,
        status="active",
    )
    expected_response = {"message": "ORDER_ADD_PAYMENT_TERM_SUCCESS", "code": 156050}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.create_order_term(payload_dto)

    mock_api_request.assert_called_once_with(
        "POST", "/order/term", json_payload=payload_dto.to_dict()
    )
    assert result == expected_response


def test_create_order_term_failure_exceeds_order_amount(mock_api_request):
    payload_dto = OrderPaymentTermCreateDTO(
        order_id="order123",
        term_reference_id="term-ref-create",
        amount=600,
        due_date="2025-10-10 00:00:00",
        term_sequence=2,
        required=False,
        status="PENDING",
    )
    api_error_content = {
        "code": 156025,
        "error": "ORDER_ADD_PAYMENT_TERM_AMOUNT_EXCEEDS_ORDER_AMOUNT",
    }
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.create_order_term(payload_dto)

    mock_api_request.assert_called_once_with(
        "POST", "/order/term", json_payload=payload_dto.to_dict()
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_create_order_term_failure_status_invalid(mock_api_request):
    payload_dto = OrderPaymentTermCreateDTO(
        order_id="order123",
        term_reference_id="term-ref-create",
        amount=600,
        due_date="2025-10-10 00:00:00",
        term_sequence=2,
        required=False,
        status="PENDİNG",  # PENDING != PENDİNG because of İ letter not in English alphabet
    )
    api_error_content = {"code": 140141, "error": "TERM_STATUS_INVALID"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.create_order_term(payload_dto)

    mock_api_request.assert_called_once_with(
        "POST", "/order/term", json_payload=payload_dto.to_dict()
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_delete_order_term_success(mock_api_request):
    order_id="mock-order-id"
    term_reference_id="mock-none-term-id"
    expected_response = {"code": 156090, "message": "ORDER_REMOVE_PAYMENT_TERM_SUCCESS"}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.delete_order_term(order_id, term_reference_id)

    mock_api_request.assert_called_once_with(
        "DELETE", "/order/term", json_payload={"order_id":order_id, "term_reference_id":term_reference_id}
    )
    assert result == expected_response


def test_delete_order_term_failure(mock_api_request):
    order_id="mock-order-id"
    term_reference_id="mock-none-term-id"
    api_error_content = {"code": 156070, "error": "ORDER_REMOVE_PAYMENT_TERM_NOT_FOUND"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.delete_order_term(order_id, term_reference_id)

    mock_api_request.assert_called_once_with(
        "DELETE", "/order/term", json_payload={"order_id":order_id, "term_reference_id":term_reference_id}
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]


def test_update_order_term_success(mock_api_request):
    payload_dto = OrderPaymentTermUpdateDTO(
        term_reference_id="term-to-update", amount=60, status="PENDING"
    )
    expected_response = {"message": "ORDER_UPDATE_PAYMENT_TERM_SUCCESS", "code": 156130}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.update_order_term(payload_dto)

    mock_api_request.assert_called_once_with(
        "PATCH", "/order/term", json_payload=payload_dto.to_dict()
    )
    assert result == expected_response


def test_update_order_term_not_found(mock_api_request):
    payload_dto = OrderPaymentTermUpdateDTO(
        term_reference_id="mock-term-id", amount=120
    )
    api_error_content = {"code": 156110, "error": "ORDER_UPDATE_PAYMENT_TERM_NOT_FOUND"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.update_order_term(payload_dto)

    mock_api_request.assert_called_once_with(
        "PATCH", "/order/term", json_payload=payload_dto.to_dict()
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]

def test_order_terminate_order_not_found(mock_api_request):
    reference_id = "mock-reference-id"
    api_error_content = {"code": 338000, "error": "ORDER_TERMINATE_ORDER_NOT_FOUND"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.order_terminate(reference_id)

    mock_api_request.assert_called_once_with(
        "POST", "/order/terminate", json_payload={"reference_id":reference_id}
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]

def test_order_terminate_order_success(mock_api_request):
    reference_id = "mock-reference-id"
    expected_response = {"message": "ORDER_TERMINATE_ORDER_SUCCESS", "code": 338100}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.order_terminate(reference_id)

    mock_api_request.assert_called_once_with(
        "POST", "/order/terminate", json_payload={"reference_id":reference_id}
    )
    assert result == expected_response

def test_order_callback_failed(mock_api_request):
    reference_id = "mock-reference-id"
    conversation_id = "mock-conversation-id"
    api_error_content = {"code": 12000, "error": "ACTION_FAILED"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.order_manual_callback(reference_id, conversation_id)

    mock_api_request.assert_called_once_with(
        "POST", "/order/callback", json_payload={"reference_id":reference_id, "conversation_id":conversation_id}
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]

def test_order_callback_order_success(mock_api_request):
    reference_id = "mock-reference-id"
    conversation_id = "mock-conversation-id"
    expected_response = {"message": "ORDER_MANUAL_CALLBACK_SUCCESS", "code": 337100}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.order_manual_callback(reference_id, conversation_id)

    mock_api_request.assert_called_once_with(
        "POST", "/order/callback", json_payload={"reference_id":reference_id, "conversation_id":conversation_id}
    )
    assert result == expected_response

def test_order_related_update_not_found(mock_api_request):
    reference_id = "mock-reference-id"
    related_reference_id = "mock-related-reference-id"
    api_error_content = {"code": 12000, "error": "ACTION_FAILED"}
    mock_api_request.side_effect = APIException(
        status_code=400,
        code=api_error_content["code"],
        error=api_error_content["error"],
    )

    client = TapsilatAPI()
    with pytest.raises(APIException) as e:
        client.order_related_update(reference_id, related_reference_id)

    mock_api_request.assert_called_once_with(
        "POST", "/order/releated", json_payload={"reference_id":reference_id, "related_reference_id":related_reference_id}
    )
    assert e.value.status_code == 400
    assert e.value.code == api_error_content["code"]
    assert e.value.error == api_error_content["error"]

def test_order_related_update_success(mock_api_request):
    reference_id = "mock-reference-id"
    related_reference_id = "mock-related-reference-id"
    expected_response = {"message": "ORDER_UPDATE_ORDER_SUCCESS", "code": 156170, "is_success":True}
    mock_api_request.return_value = expected_response

    client = TapsilatAPI()
    result = client.order_related_update(reference_id, related_reference_id)

    mock_api_request.assert_called_once_with(
        "POST", "/order/releated", json_payload={"reference_id":reference_id, "related_reference_id":related_reference_id}
    )
    assert result == expected_response


def test_create_order_with_gsm_validation(mock_api_request):
    expected_api_json_response = {
        "order_id": "mock-gsm-validation",
        "reference_id": "mock-gsm-ref",
    }
    mock_api_request.return_value = expected_api_json_response

    buyer = BuyerDTO(
        name="John",
        surname="Doe",
        email="test@example.com",
        gsm_number="+90 555 123-45-67"  # Will be cleaned by validator
    )
    order_payload_dto = OrderCreateDTO(
        amount=100,
        currency="TRY",
        locale="tr",
        buyer=buyer,
    )
    client = TapsilatAPI()
    order_response_obj = client.create_order(order_payload_dto)

    # Verify GSM was cleaned
    assert order_payload_dto.buyer.gsm_number == "+905551234567"
    mock_api_request.assert_called_once()
    assert isinstance(order_response_obj, OrderResponse)


def test_create_order_with_invalid_gsm_raises_exception(mock_api_request):
    buyer = BuyerDTO(
        name="John",
        surname="Doe",
        email="test@example.com",
        gsm_number="invalid-phone"
    )
    order_payload_dto = OrderCreateDTO(
        amount=100,
        currency="TRY",
        locale="tr",
        buyer=buyer,
    )
    client = TapsilatAPI()

    with pytest.raises(APIException) as exc_info:
        client.create_order(order_payload_dto)

    assert exc_info.value.code == 0
    mock_api_request.assert_not_called()
