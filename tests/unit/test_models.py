from tapsilat_py.models import (
    BasketItemDTO,
    BasketItemPayerDTO,
    BillingAddressDTO,
    BuyerDTO,
    CheckoutDesignDTO,
    OrderCardDTO,
    OrderCreateDTO,
    OrderPFSubMerchantDTO,
    PaymentTermDTO,
    OrderConsent,
    MetadataDTO
)

def test_buyer_dto_all_fields():
    buyer = BuyerDTO(
        id="b1",
        name="John",
        surname="Doe",
        identity_number="12345678901",
        email="john@example.com",
        gsm_number="+905555555555",
        registration_date="2025-01-01",
        last_login_date="2025-10-01",
        registration_address="Main St 1",
        city="Istanbul",
        country="Turkey",
        zip_code="34000",
        ip="192.168.1.1",
        title="Mr"
    )
    buyer_dict = buyer.to_dict() if hasattr(buyer, 'to_dict') else buyer.__dict__
    
    assert buyer.registration_address == "Main St 1"
    assert buyer_dict.get("registration_address") == "Main St 1"


def test_basket_item_dto_all_fields():
    payer = BasketItemPayerDTO(
        address="Test Address", 
        reference_id="ref1", 
        tax_office="office", 
        title="Company", 
        type="Corporate", 
        vat="18"
    )

    basket_item = BasketItemDTO(
        id="item1",
        price=100.0,
        name="Product",
        category1="C1",
        category2="C2",
        item_type="PHYSICAL",
        sub_merchant_key="key1",
        sub_merchant_price="100.0",
        coupon="SAVE10",
        coupon_discount=10.0,
        quantity=1,
        quantity_float=1.0,
        quantity_unit="pcs",
        paid_amount=90.0,
        data="extra",
        payer=payer,
        commission_amount=5.0,
        mcc="1234"
    )
    
    assert basket_item.payer.title == "Company"
    assert basket_item.commission_amount == 5.0
    assert basket_item.quantity_float == 1.0


def test_checkout_design_dto_all_fields():
    design = CheckoutDesignDTO(
        logo="logo_url",
        input_background_color="#fff",
        input_text_color="#000",
        label_text_color="#333",
        left_background_color="#eee",
        right_background_color="#ccc",
        text_color="#111",
        pay_button_color="#f00",
        order_detail_html="<p>Details</p>",
        redirect_url="https://example.com/redirect"
    )
    assert design.pay_button_color == "#f00"
    assert design.redirect_url == "https://example.com/redirect"


def test_billing_address_dto_all_fields():
    billing = BillingAddressDTO(
        billing_type="INDIVIDUAL",
        citizenship="TR",
        title="John Doe",
        address="Addr",
        zip_code="34000",
        contact_name="John Doe",
        contact_phone="+905555555555",
        city="Istanbul",
        country="Turkey",
        tax_office="Besiktas",
        vat_number="123456789",
        district="Besiktas",
        neighbourhood="Bebek",
        street1="Street 1",
        street2="Street 2",
        street3="Street 3"
    )
    assert billing.neighbourhood == "Bebek"
    assert billing.street1 == "Street 1"


def test_payment_term_dto_all_fields():
    term = PaymentTermDTO(
        term_sequence=1,
        required=True,
        amount=50.0,
        due_date="2025-01-01",
        paid_date="2025-01-01",
        term_reference_id="termref1",
        status="paid",
        data="some data"
    )
    assert term.term_sequence == 1
    assert term.amount == 50.0


def test_order_pf_submerchant_dto_all_fields():
    pf = OrderPFSubMerchantDTO(
        name="PF Merchant",
        id="pf1",
        postal_code="34000",
        city="Istanbul",
        country="Turkey",
        mcc="5411",
        terminal_no="term123",
        org_id="org1",
        country_iso_code="792",
        address="PF Address",
        submerchant_url="https://pf.example.com",
        submerchant_nin="nin123",
        switch_id="1",
        national_id="nat123"
    )
    assert pf.postal_code == "34000"
    assert pf.country_iso_code == "792"
    assert pf.mcc == "5411"


def test_order_create_dto_all_fields():
    buyer = BuyerDTO(name="John", surname="Doe")
    card = OrderCardDTO(card_id="card1", card_sequence=1)
    consent = OrderConsent(title="Terms", url="https://terms")
    meta = MetadataDTO(key="source", value="web")
    
    order = OrderCreateDTO(
        amount=100.0,
        currency="TRY",
        locale="tr",
        buyer=buyer,
        paid_amount=90.0,
        order_cards=[card],
        consents=[consent],
        metadata=[meta]
    )
    
    data = order.to_dict()
    assert data["amount"] == 100.0
    assert data["currency"] == "TRY"
    assert data["order_cards"][0]["card_sequence"] == 1
