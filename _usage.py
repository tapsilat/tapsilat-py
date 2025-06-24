import json
import os

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
)
from tapsilat_py.validators import validate_gsm_number, validate_installments

# TAPSILAT_API_KEY from environment

def get_api_client():
    api_key = str(os.getenv("TAPSILAT_API_KEY"))
    if not api_key:
        print("Error: TAPSILAT_API_KEY is not set.")
        return None
    return TapsilatAPI(api_key=api_key)

def process_order_creation(client, order_payload, scenario_name):
    print("#"*16)
    print(f"{scenario_name}")
    if not client:
        return

    try:
        print("Request Payload:")
        payload_dict = order_payload.to_dict() if hasattr(order_payload, 'to_dict') and callable(order_payload.to_dict) else {}
        if not payload_dict:
            from dataclasses import asdict
            payload_dict = asdict(order_payload)
        print(json.dumps(payload_dict, indent=2, ensure_ascii=False))

        order_response = client.create_order(order_payload)
        # print("\nCreate Order Response:", json.dumps(order_response, indent=2, ensure_ascii=False))

        if order_response and order_response.get("reference_id"):
            checkout_url = client.get_checkout_url(order_response)
            print("\nCheckout URL:", checkout_url)
            print("#"*16)
            return order_response
        else:
            print("\nOrder creation failed or 'reference_id' not found in response.")
            print("#"*16)
            return None
    except APIException as e:
        print(f"\nAPI Error ({scenario_name}): Status: {e.status_code}, Code: {e.code}, Msg: {e.error}")
        print("#"*16)
        return None
    except Exception as e:
        print(f"\nUnexpected error ({scenario_name}): {e}")
        import traceback
        traceback.print_exc()
        print("#"*16)
        return None

def run_scenario_1_basic_order(client):
    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    order_payload = OrderCreateDTO(amount=100.00, currency="TRY", locale="tr", buyer=buyer)
    process_order_creation(client, order_payload, "Scenario 1: Basic Order")

def run_scenario_2_order_with_basket_items(client):
    buyer_data = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    basket_item1_payer = BasketItemPayerDTO(reference_id="payer_ref0_item1", type="PERSONAL")
    basket_item1 = BasketItemDTO(id="B001", name="Item 1", price=10.00, quantity=1, item_type="PHYSICAL", payer=basket_item1_payer)
    basket_item2_payer = BasketItemPayerDTO(reference_id="payer_ref1_item2", type="BUSINESS")
    basket_item2 = BasketItemDTO(id="B002", name="Item 2", price=20.49, quantity=2, item_type="PHYSICAL", payer=basket_item2_payer)

    order_payload = OrderCreateDTO(
        amount=30.49,
        currency="TRY",
        locale="tr",
        buyer=buyer_data,
        basket_items=[basket_item1, basket_item2]
    )
    process_order_creation(client, order_payload, "Scenario 2: Order with Basket Items")

def run_scenario_3_order_with_addresses(client):
    buyer_data = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    billing_address_data = BillingAddressDTO(address="uskudar", city="Istanbul", country="TR", contact_name="John Doe", zip_code="34000")
    shipping_address_data = ShippingAddressDTO(address="kadikoy", city="Istanbul", country="TR", contact_name="Jane Doe", zip_code="34001")

    order_payload = OrderCreateDTO(
        amount=25.00,
        currency="TRY",
        locale="tr",
        buyer=buyer_data,
        billing_address=billing_address_data,
        shipping_address=shipping_address_data
    )
    process_order_creation(client, order_payload, "Scenario 3: Order with Billing and Shipping Addresses")

def run_scenario_4_installments_and_payment_methods(client):
    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    payload = OrderCreateDTO(amount=1200.00, currency="TRY", locale="tr", buyer=buyer,
        enabled_installments=[2, 3, 6, 9],
        payment_methods=True,
        payment_options=['credit_card','cash'],
        payment_success_url="https://example.com/install_success_s8",
        payment_failure_url="https://example.com/install_failure_s8")
    process_order_creation(client, payload, "Scenario 4: Installments and Payment Methods")

def run_scenario_5_detailed_checkout_design_full(client):
    buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
    design = CheckoutDesignDTO(
        pay_button_color="#FF0000",
        logo="http://example.com/logo.png",
        input_background_color="#EEEEEE",
        input_text_color="#333333",
        right_background_color="#FAFAFA"
    )
    payload = OrderCreateDTO(amount=55.00, currency="TRY", locale="tr", buyer=buyer, checkout_design=design)
    process_order_creation(client, payload, "Scenario 4: Detailed Checkout Design (Full)")

def run_scenario_6_validation_demo(client):
    try:
        # Test GSM validation
        valid_gsm = validate_gsm_number("+905551234567")
        print(f"Valid GSM: {valid_gsm}")

        # Test installments validation
        valid_installments = validate_installments("1,2,3,6")
        print(f"Valid installments: {valid_installments}")

        # Create order with validated data
        buyer = BuyerDTO(
            name="John",
            surname="Doe",
            email="test@example.com",
            gsm_number="+905551234567"
        )
        order_payload = OrderCreateDTO(
            amount=100.00,
            currency="TRY",
            locale="tr",
            buyer=buyer,
            enabled_installments=[1, 2, 3, 6]
        )
        process_order_creation(client, order_payload, "Scenario 6: Validation Demo")

    except APIException as e:
        print(f"Validation Error: {e.error}")

def run_scenario_7_validation_errors(client):
    try:
        validate_gsm_number("invalid-phone")
    except APIException as e:
        print(f"GSM Validation Error: {e.error}")

    try:
        validate_installments("1,15,abc")
    except APIException as e:
        print(f"Installments Validation Error: {e.error}")


if __name__ == "__main__":
    api_client = get_api_client()
    if api_client:
        run_scenario_1_basic_order(api_client)
        run_scenario_2_order_with_basket_items(api_client)
        run_scenario_3_order_with_addresses(api_client)
        run_scenario_4_installments_and_payment_methods(api_client)
        run_scenario_5_detailed_checkout_design_full(api_client)
        run_scenario_6_validation_demo(api_client)
        run_scenario_7_validation_errors(api_client)
        print("\nAll scenarios completed.")
    else:
        print("API client could not be initialized.")
