import json
from dataclasses import asdict

import pytest
from requests.models import Response

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
    OrderPFSubMerchantDTO,
    PaymentTermDTO,
    ShippingAddressDTO,
    SubmerchantDTO,
    SubOrganizationDTO,
)


class DummyResponse(Response):
    def __init__(self, json_data, status_code):
        super().__init__()
        self._json_data = json_data
        self.status_code = status_code

        if isinstance(json_data, dict) or isinstance(json_data, list):
            self._content = json.dumps(json_data).encode('utf-8')
        elif isinstance(json_data, str):
            self._content = json_data.encode('utf-8')
        else:
            self._content = b''
        self.encoding = 'utf-8'

    def json(self, **kwargs):
        return self._json_data


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

    assert json_data["basket_items"] is None
    assert json_data.get("external_reference_id") is None
    assert "external_reference_id" in json_data
    assert json_data["external_reference_id"] is None


def test_create_order_success(monkeypatch):
    expected_api_response = {
        "order_id": "mock-03d03353-78bc-4432-9da6-1433ecd7fbbb",
        "reference_id": "mock-03d03353-9b5b-4289-b231-ffbe50f8a79d",
    }
    dummy = DummyResponse(expected_api_response, 200)

    captured_payloads = []

    def mock_post(url, json, headers, timeout):
        captured_payloads.append(json)
        return dummy

    monkeypatch.setattr("requests.post", mock_post)

    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    order_payload = OrderCreateDTO(
        amount=100,
        currency="TRY",
        locale="tr",
        buyer=buyer,
    )
    client = TapsilatAPI()

    api_response = client.create_order(order_payload)

    assert api_response == expected_api_response

    assert len(captured_payloads) == 1
    sent_payload = captured_payloads[0]
    assert sent_payload["amount"] == 100
    assert sent_payload["currency"] == "TRY"
    assert sent_payload["locale"] == "tr"
    assert sent_payload["buyer"]["name"] == "John"

    assert sent_payload["basket_items"] is None
    assert sent_payload.get("billing_address") is None

def test_basket_item_payer_dto_asdict():
    payer = BasketItemPayerDTO(address="uskudar", type="PERSONAL", reference_id="123456789")
    payer_dict = asdict(payer)
    assert payer_dict["address"] == "uskudar"
    assert payer_dict["type"] == "PERSONAL"
    assert payer_dict["reference_id"] == "123456789"
    assert payer_dict["tax_office"] is None

def test_basket_item_dto_asdict():
    payer_data = BasketItemPayerDTO(address="uskudar", type="BTRINESS")
    item = BasketItemDTO(
        id="BI101",
        name="Binocular",
        price=19.99,
        quantity=1,
        item_type="PHYSICAL",
        payer=payer_data
    )
    item_dict = asdict(item)
    assert item_dict["id"] == "BI101"
    assert item_dict["name"] == "Binocular"
    assert item_dict["price"] == 19.99
    assert item_dict["quantity"] == 1
    assert item_dict["item_type"] == "PHYSICAL"
    assert item_dict["payer"]["address"] == "uskudar"
    assert item_dict["payer"]["type"] == "BTRINESS"
    assert item_dict["category1"] is None

def test_billing_address_dto_asdict():
    billing = BillingAddressDTO(
        address="uskudar",
        city="Istanbul",
        country="TR",
        contact_name="Jane Doe"
    )
    billing_dict = asdict(billing)
    assert billing_dict["address"] == "uskudar"
    assert billing_dict["city"] == "Istanbul"
    assert billing_dict["country"] == "TR"
    assert billing_dict["contact_name"] == "Jane Doe"
    assert billing_dict["zip_code"] is None

def test_checkout_design_dto_asdict():
    design = CheckoutDesignDTO(
        pay_button_color="#FF0000",
        logo="http://example.com/logo.png"
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
        amount=50.0,
        due_date="2025-10-21T23:59:59Z",
        status="PENDING",
        term_sequence=1
    )
    term_dict = asdict(term)
    assert term_dict["amount"] == 50.0
    assert term_dict["due_date"] == "2025-10-21T23:59:59Z"
    assert term_dict["status"] == "PENDING"
    assert term_dict["term_sequence"] == 1
    assert term_dict["data"] is None

def test_order_pf_sub_merchant_dto_asdict():
    pf_sub = OrderPFSubMerchantDTO(
        id="123456789",
        name="John Doe",
        mcc="1234"
    )
    pf_sub_dict = asdict(pf_sub)
    assert pf_sub_dict["id"] == "123456789"
    assert pf_sub_dict["name"] == "John Doe"
    assert pf_sub_dict["mcc"] == "1234"
    assert pf_sub_dict["address"] is None

def test_shipping_address_dto_asdict():
    shipping = ShippingAddressDTO(
        address="uskudar",
        city="Istanbul",
        country="Turkey",
        contact_name="Jane Doe"
    )
    shipping_dict = asdict(shipping)
    assert shipping_dict["address"] == "uskudar"
    assert shipping_dict["city"] == "Istanbul"
    assert shipping_dict["country"] == "Turkey"
    assert shipping_dict["contact_name"] == "Jane Doe"
    assert shipping_dict["zip_code"] is None

def test_sub_organization_dto_asdict():
    sub_org = SubOrganizationDTO(
        organization_name="ACME Inc.",
        sub_merchant_key="sub merchant key",
        legal_company_title="ACME Inc."
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
        order_basket_item_id="BI101"
    )
    submerchant_dict = asdict(submerchant)
    assert submerchant_dict["amount"] == 20.49
    assert submerchant_dict["merchant_reference_id"] == "merchant reference id"
    assert submerchant_dict["order_basket_item_id"] == "BI101"

def test_create_order_with_basket_items(monkeypatch):
    expected_api_response = {"order_id": "order_basket", "reference_id": "ref_basket"}
    dummy = DummyResponse(expected_api_response, 200)

    captured_payloads = []
    def mock_post(url, json, headers, timeout):
        captured_payloads.append(json)
        return dummy
    monkeypatch.setattr("requests.post", mock_post)

    buyer_data = BuyerDTO(name="Test", surname="User")
    basket_item1_payer = BasketItemPayerDTO(reference_id="payer_ref0_item1")
    basket_item1 = BasketItemDTO(id="B001", name="Item 1", price=10.0, quantity=1, payer=basket_item1_payer)
    basket_item2 = BasketItemDTO(id="B002", name="Item 2", price=20.49, quantity=2,
                                 payer=BasketItemPayerDTO(reference_id="payer_ref1_item2"))

    order_payload = OrderCreateDTO(
        amount=50.0,
        currency="TRD",
        locale="en",
        buyer=buyer_data,
        basket_items=[basket_item1, basket_item2]
    )
    client = TapsilatAPI()
    api_response = client.create_order(order_payload)

    assert api_response == expected_api_response
    assert len(captured_payloads) == 1
    sent_payload = captured_payloads[0]

    assert sent_payload["amount"] == 50.0
    assert sent_payload["buyer"]["name"] == "Test"
    assert len(sent_payload["basket_items"]) == 2
    assert sent_payload["basket_items"][0]["id"] == "B001"
    assert sent_payload["basket_items"][0]["price"] == 10.0
    assert sent_payload["basket_items"][0]["payer"]["reference_id"] == "payer_ref0_item1"
    assert sent_payload["basket_items"][1]["id"] == "B002"
    assert sent_payload["basket_items"][1]["price"] == 20.49
    assert sent_payload["basket_items"][1]["payer"]["reference_id"] == "payer_ref1_item2"


def test_create_order_with_billing_and_shipping_address(monkeypatch):
    expected_api_response = {"order_id": "order_addr", "reference_id": "ref_addr"}
    dummy = DummyResponse(expected_api_response, 200)

    captured_payloads = []
    def mock_post(url, json, headers, timeout):
        captured_payloads.append(json)
        return dummy
    monkeypatch.setattr("requests.post", mock_post)

    buyer_data = BuyerDTO(name="Addr", surname="Test")
    billing_address_data = BillingAddressDTO(address="uskudar", city="Istanbul", country="TR", contact_name="John Doe")
    shipping_address_data = ShippingAddressDTO(address="uskudar", city="Istanbul", country="TR", contact_name="Jane Doe")

    order_payload = OrderCreateDTO(
        amount=25.0,
        currency="EUR",
        locale="de",
        buyer=buyer_data,
        billing_address=billing_address_data,
        shipping_address=shipping_address_data
    )
    client = TapsilatAPI()
    api_response = client.create_order(order_payload)

    assert api_response == expected_api_response
    assert len(captured_payloads) == 1
    sent_payload = captured_payloads[0]

    assert sent_payload["billing_address"]["address"] == "uskudar"
    assert sent_payload["billing_address"]["city"] == "Istanbul"
    assert sent_payload["billing_address"]["contact_name"] == "John Doe"
    assert sent_payload["shipping_address"]["address"] == "uskudar"
    assert sent_payload["shipping_address"]["city"] == "Istanbul"
    assert sent_payload["shipping_address"]["contact_name"] == "Jane Doe"


def test_create_order_with_metadata_and_order_card(monkeypatch):
    expected_api_response = {"order_id": "order_meta_card", "reference_id": "ref_meta_card"}
    dummy = DummyResponse(expected_api_response, 200)

    captured_payloads = []
    def mock_post(url, json, headers, timeout):
        captured_payloads.append(json)
        return dummy
    monkeypatch.setattr("requests.post", mock_post)

    buyer_data = BuyerDTO(name="John", surname="Doe")
    metadata_list_data = [
        MetadataDTO(key="source", value="mobile_app"),
        MetadataDTO(key="campaign", value="summer_sale")
    ]

    order_card_data = OrderCardDTO(card_id="123456", card_sequence=1)

    order_payload = OrderCreateDTO(
        amount=99.0,
        currency="TRY",
        locale="tr",
        buyer=buyer_data,
        metadata=metadata_list_data,
        order_cards=order_card_data
    )
    client = TapsilatAPI()
    api_response = client.create_order(order_payload)

    assert api_response == expected_api_response
    assert len(captured_payloads) == 1
    sent_payload = captured_payloads[0]

    assert len(sent_payload["metadata"]) == 2
    assert sent_payload["metadata"][0]["key"] == "source"
    assert sent_payload["metadata"][1]["value"] == "summer_sale"
    assert sent_payload["order_cards"]["card_id"] == "123456"
    assert sent_payload["order_cards"]["card_sequence"] == 1


def test_create_order_with_all_optional_fields_none(monkeypatch):
    expected_api_response = {"order_id": "order_none", "reference_id": "ref_none"}
    dummy = DummyResponse(expected_api_response, 200)

    captured_payloads = []
    def mock_post(url, json, headers, timeout):
        captured_payloads.append(json)
        return dummy
    monkeypatch.setattr("requests.post", mock_post)

    buyer_data = BuyerDTO(name="Jane", surname="Doe")
    order_payload = OrderCreateDTO(
        amount=10.0,
        currency="TRY",
        locale="tr",
        buyer=buyer_data
    )

    client = TapsilatAPI()
    api_response = client.create_order(order_payload)

    assert api_response == expected_api_response
    assert len(captured_payloads) == 1
    sent_payload = captured_payloads[0]

    assert sent_payload["amount"] == 10.0
    assert sent_payload["buyer"]["name"] == "Jane"
    assert sent_payload["basket_items"] is None
    assert sent_payload["billing_address"] is None
    assert sent_payload["checkout_design"] is None
    assert sent_payload["conversation_id"] is None
    assert sent_payload["enabled_installments"] is None
    assert sent_payload["external_reference_id"] is None
    assert sent_payload["metadata"] is None
    assert sent_payload["order_cards"] is None
    assert sent_payload["paid_amount"] is None
    assert sent_payload["partial_payment"] is None
    assert sent_payload["payment_failure_url"] is None
    assert sent_payload["payment_methods"] is None
    assert sent_payload["payment_options"] is None
    assert sent_payload["payment_success_url"] is None
    assert sent_payload["payment_terms"] is None
    assert sent_payload["pf_sub_merchant"] is None
    assert sent_payload["shipping_address"] is None
    assert sent_payload["sub_organization"] is None
    assert sent_payload["submerchants"] is None
    assert sent_payload["tax_amount"] is None
    assert sent_payload["three_d_force"] is None


def test_create_order_with_payment_terms_and_submerchants(monkeypatch):
    expected_api_response = {"order_id": "order_terms_sub", "reference_id": "ref_terms_sub"}
    dummy = DummyResponse(expected_api_response, 200)

    captured_payloads = []
    def mock_post(url, json, headers, timeout):
        captured_payloads.append(json)
        return dummy
    monkeypatch.setattr("requests.post", mock_post)

    buyer_data = BuyerDTO(name="Jane", surname="Doe")
    payment_terms_data = [
        PaymentTermDTO(amount=50.0, due_date="2025-01-15", term_sequence=1, status="PENDING"),
        PaymentTermDTO(amount=50.0, due_date="2025-02-15", term_sequence=2, status="PENDING")
    ]
    submerchants_list_data = [
        SubmerchantDTO(amount=30.0, merchant_reference_id="sub1", order_basket_item_id="B001"),
        SubmerchantDTO(amount=20.49, merchant_reference_id="sub2", order_basket_item_id="B002")
    ]

    order_payload = OrderCreateDTO(
        amount=100.0,
        currency="TRY",
        locale="tr",
        buyer=buyer_data,
        payment_terms=payment_terms_data,
        submerchants=submerchants_list_data,
        checkout_design=CheckoutDesignDTO(logo="http://logo.url/img.png"),
        pf_sub_merchant=OrderPFSubMerchantDTO(id="pfsm007", name="PF Sub"),
        sub_organization=SubOrganizationDTO(organization_name="Sub Org")
    )
    client = TapsilatAPI()
    api_response = client.create_order(order_payload)

    assert api_response == expected_api_response
    assert len(captured_payloads) == 1
    sent_payload = captured_payloads[0]

    assert len(sent_payload["payment_terms"]) == 2
    assert sent_payload["payment_terms"][0]["amount"] == 50.0
    assert sent_payload["payment_terms"][0]["term_sequence"] == 1
    assert sent_payload["payment_terms"][1]["due_date"] == "2025-02-15"

    assert len(sent_payload["submerchants"]) == 2
    assert sent_payload["submerchants"][0]["merchant_reference_id"] == "sub1"
    assert sent_payload["submerchants"][1]["amount"] == 20.49

    assert sent_payload["checkout_design"]["logo"] == "http://logo.url/img.png"
    assert sent_payload["pf_sub_merchant"]["id"] == "pfsm007"
    assert sent_payload["sub_organization"]["organization_name"] == "Sub Org"

def test_get_order_success(monkeypatch):
    reference_id= "mock-03d03353-9b5b-4289-b231-ffbe50f8a79d"
    expected_api_response = {
        "checkout_url": "https://checkout.test.dev?reference_id=mock-03d03353-d2be-4094-b5f6-7b7a8473534e",
        "status": "PENDING"
    }
    dummy = DummyResponse(expected_api_response, 200)
    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)

    client = TapsilatAPI()
    result = client.get_order(reference_id)

    assert (
        result["checkout_url"]
        == "https://checkout.test.dev?reference_id=mock-03d03353-d2be-4094-b5f6-7b7a8473534e"
    )
    assert result["status"] == "PENDING"
    assert result == expected_api_response


def test_get_order_failure(monkeypatch):
    reference_id= "mock-failed-reference-id"
    api_error_response = {"code": 101160, "error": "ORDER_ORDER_DETAIL_ORDER_NOT_FOUND"}
    dummy = DummyResponse(api_error_response, 400)
    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)

    client = TapsilatAPI()

    with pytest.raises(APIException) as e:
        client.get_order(reference_id)

    assert e.value.status_code == 400
    assert e.value.code == 101160
    assert e.value.error == "ORDER_ORDER_DETAIL_ORDER_NOT_FOUND"


def test_get_checkout_url_success(monkeypatch):
    reference_id = "mock-ref-for-checkout"
    get_order_api_response = {
        "checkout_url": "https://checkout.test.dev?reference_id=mock-checkout-url-generated",
        "status": "Waiting for payment"
    }
    dummy = DummyResponse(get_order_api_response, 200)

    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)

    client = TapsilatAPI()
    checkout_url_result = client.get_checkout_url(reference_id)

    assert (
        checkout_url_result
        == "https://checkout.test.dev?reference_id=mock-checkout-url-generated"
    )

def test_cancel_order_not_found(monkeypatch):
    expected_api_response = {
        "code": 101550,
        "error": "ORDER_CANCEL_ORDER_GET_ORDER_NOT_FOUND"
    }
    dummy = DummyResponse(expected_api_response, 400)

    captured_payloads = []

    def mock_post(url, json, headers, timeout):
        captured_payloads.append(json)
        return dummy

    monkeypatch.setattr("requests.post", mock_post)

    reference_id="mock-reference-id"
    client = TapsilatAPI()

    with pytest.raises(APIException) as e:
        client.cancel_order(reference_id)

    assert e.value.status_code == 400
    assert e.value.code == 101550
    assert e.value.error == "ORDER_CANCEL_ORDER_GET_ORDER_NOT_FOUND"

def test_cancel_order_success(monkeypatch):
    expected_api_response = {
        "is_success": True,
        "message": "ORDER_CANCEL_SUCCESS",
        "status": "101645"
    }
    dummy = DummyResponse(expected_api_response, 200)

    captured_payloads = []

    def mock_post(url, json, headers, timeout):
        captured_payloads.append(json)
        return dummy

    monkeypatch.setattr("requests.post", mock_post)

    reference_id="mock-reference-id"

    client = TapsilatAPI()

    api_response = client.cancel_order(reference_id)

    assert api_response==expected_api_response
    assert len(captured_payloads)==1
    sent_payload = captured_payloads[0]
    assert sent_payload["reference_id"] == "mock-reference-id"
