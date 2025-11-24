import os
import pytest
from dotenv import load_dotenv

from tapsilat_py.client import TapsilatAPI
from tapsilat_py.exceptions import APIException
from tapsilat_py.models import (
    BasketItemDTO,
    BasketItemPayerDTO,
    BillingAddressDTO,
    BuyerDTO,
    CheckoutDesignDTO,
    OrderCreateDTO,
    ShippingAddressDTO,
    SubscriptionBilling,
    SubscriptionCancelRequest,
    SubscriptionCreateRequest,
    SubscriptionGetRequest,
    SubscriptionRedirectRequest,
    SubscriptionUser,
)
from tapsilat_py.validators import validate_gsm_number, validate_installments

# Load environment variables
load_dotenv()


@pytest.fixture
def api_client():
    api_key = os.getenv("TAPSILAT_API_KEY")
    if not api_key:
        pytest.skip("TAPSILAT_API_KEY not set in environment")
    return TapsilatAPI(api_key=api_key)


def test_scenario_1_basic_order(api_client):
    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    order_payload = OrderCreateDTO(
        amount=100.00, currency="TRY", locale="tr", buyer=buyer
    )

    response = api_client.create_order(order_payload)
    assert response.reference_id is not None
    assert response.checkout_url is not None


def test_scenario_2_order_with_basket_items(api_client):
    buyer_data = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    basket_item1_payer = BasketItemPayerDTO(
        reference_id="payer_ref0_item1", type="PERSONAL"
    )
    basket_item1 = BasketItemDTO(
        id="B001",
        name="Item 1",
        price=10.00,
        quantity=1,
        item_type="PHYSICAL",
        payer=basket_item1_payer,
    )
    basket_item2_payer = BasketItemPayerDTO(
        reference_id="payer_ref1_item2", type="BUSINESS"
    )
    basket_item2 = BasketItemDTO(
        id="B002",
        name="Item 2",
        price=20.49,
        quantity=2,
        item_type="PHYSICAL",
        payer=basket_item2_payer,
    )

    order_payload = OrderCreateDTO(
        amount=30.49,
        currency="TRY",
        locale="tr",
        buyer=buyer_data,
        basket_items=[basket_item1, basket_item2],
    )

    response = api_client.create_order(order_payload)
    assert response.reference_id is not None


def test_scenario_3_order_with_addresses(api_client):
    buyer_data = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    billing_address_data = BillingAddressDTO(
        address="123 Main St",
        city="Istanbul",
        country="TR",
        contact_name="John Doe",
        zip_code="34000",
    )
    shipping_address_data = ShippingAddressDTO(
        address="456 Oak Ave",
        city="Istanbul",
        country="TR",
        contact_name="Jane Doe",
        zip_code="34001",
    )

    order_payload = OrderCreateDTO(
        amount=25.00,
        currency="TRY",
        locale="tr",
        buyer=buyer_data,
        billing_address=billing_address_data,
        shipping_address=shipping_address_data,
    )

    response = api_client.create_order(order_payload)
    assert response.reference_id is not None


def test_scenario_4_installments_and_payment_methods(api_client):
    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    payload = OrderCreateDTO(
        amount=1200.00,
        currency="TRY",
        locale="tr",
        buyer=buyer,
        enabled_installments=[2, 3, 6, 9],
        payment_methods=True,
        payment_options=["credit_card", "cash"],
        payment_success_url="https://example.com/install_success_s8",
        payment_failure_url="https://example.com/install_failure_s8",
    )

    response = api_client.create_order(payload)
    assert response.reference_id is not None


def test_scenario_5_detailed_checkout_design_full(api_client):
    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    design = CheckoutDesignDTO(
        pay_button_color="#FF0000",
        logo="http://example.com/logo.png",
        input_background_color="#EEEEEE",
        input_text_color="#333333",
        right_background_color="#FAFAFA",
    )
    payload = OrderCreateDTO(
        amount=55.00, currency="TRY", locale="tr", buyer=buyer, checkout_design=design
    )

    response = api_client.create_order(payload)
    assert response.reference_id is not None


def test_scenario_6_validation_demo(api_client):
    # Test GSM validation
    valid_gsm = validate_gsm_number("+905551234567")
    assert valid_gsm == "+905551234567"

    # Test installments validation
    valid_installments = validate_installments("1,2,3,6")
    assert valid_installments == [1, 2, 3, 6]

    # Create order with validated data
    buyer = BuyerDTO(
        name="John", surname="Doe", email="test@example.com", gsm_number="+905551234567"
    )
    order_payload = OrderCreateDTO(
        amount=100.00,
        currency="TRY",
        locale="tr",
        buyer=buyer,
        enabled_installments=[1, 2, 3, 6],
    )

    response = api_client.create_order(order_payload)
    assert response.reference_id is not None


def test_scenario_7_validation_errors(api_client):
    with pytest.raises(APIException):
        validate_gsm_number("invalid-phone")

    with pytest.raises(APIException):
        validate_installments("1,15,abc")


def test_scenario_8_get_orders(api_client):
    # Get orders for a specific buyer (assuming buyer_123 might not exist but call should succeed)
    # Or just list orders without buyer_id to be safe if buyer_123 doesn't exist
    try:
        response = api_client.get_orders(page="1", per_page="10")
        assert isinstance(response, dict)
    except APIException as e:
        # If no orders, it might return error or empty list depending on API
        # But we expect a successful call structure
        pytest.fail(f"API Error: {e}")


def test_scenario_9_organization_settings(api_client):
    settings = api_client.get_organization_settings()
    assert isinstance(settings, dict)


def test_scenario_10_subscription_lifecycle(api_client):
    # Create Subscription
    user = SubscriptionUser(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+905551234567",
        identity_number="12345678901",
    )
    billing = SubscriptionBilling(
        address="Test Address",
        city="Istanbul",
        country="TR",
        contact_name="John Doe",
        zip_code="34000",
    )
    subscription_request = SubscriptionCreateRequest(
        amount=100.0,
        currency="TRY",
        cycle=12,
        period=1,
        payment_date=1,
        title="Monthly Subscription",
        external_reference_id="ext_ref_test_integration",
        user=user,
        billing=billing,
        success_url="https://example.com/success",
        failure_url="https://example.com/failure",
    )

    create_response = api_client.create_subscription(subscription_request)
    assert create_response.reference_id is not None
    sub_ref_id = create_response.reference_id

    # Get Subscription
    get_request = SubscriptionGetRequest(reference_id=sub_ref_id)
    subscription = api_client.get_subscription(get_request)
    # SubscriptionDetail does not have reference_id in Go SDK, so we don't check it here
    # assert subscription.reference_id == sub_ref_id
    assert subscription.title == "Monthly Subscription"

    # List Subscriptions
    subscriptions = api_client.list_subscriptions(page=1, per_page=10)
    assert isinstance(subscriptions, dict)

    # Redirect Subscription
    redirect_request = SubscriptionRedirectRequest(subscription_id=sub_ref_id)
    redirect_response = api_client.redirect_subscription(redirect_request)
    assert redirect_response.url is not None

    # Cancel Subscription
    cancel_request = SubscriptionCancelRequest(reference_id=sub_ref_id)
    cancel_response = api_client.cancel_subscription(cancel_request)
    # Assuming cancel returns a dict with success or similar
    assert isinstance(cancel_response, dict)
