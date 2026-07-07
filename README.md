# Tapsilat Client SDK for Python

Create orders and retrieve secure checkout URLs.

needs Python3.6+

## Installation
```bash
pip install tapsilat-py
```
or

```bash
pip install git+https://github.com/tapsilat/tapsilat-py.git
```
or
```bash
git clone https://github.com/tapsilat/tapsilat-py.git
cd tapsilat-py
pip install -r requirements.txt
```

## Running Tests

### Unit Tests
```bash
pytest tests/unit
```

### Integration Tests
Integration tests require a valid `TAPSILAT_API_KEY` in a `.env` file.

1. Create a `.env` file in the root directory:
```
TAPSILAT_API_KEY=your_api_key_here
```

2. Run the integration tests:
```bash
pytest tests/integration
```


## Usage
.env file
```.env
TAPSILAT_API_KEY=your_api_key_here
```

### TapsilatAPI initialization
```python
import os

from tapsilat_py.client import TapsilatAPI

API_KEY = str(os.getenv("TAPSILAT_API_KEY"))

client = TapsilatAPI(API_KEY)
```

### Validators
The SDK includes built-in validators for common data types:

#### GSM Number Validation
```python
from tapsilat_py.validators import validate_gsm_number

# Valid formats
valid_gsm = validate_gsm_number("+905551234567")  # International with +
valid_gsm = validate_gsm_number("00905551234567")  # International with 00
valid_gsm = validate_gsm_number("05551234567")     # National format
valid_gsm = validate_gsm_number("5551234567")      # Local format

# Automatically cleans formatting
clean_gsm = validate_gsm_number("+90 555 123-45-67")  # Returns: "+905551234567"

# Raises APIException for invalid formats
try:
    validate_gsm_number("invalid-phone")
except APIException as e:
    print(f"Error: {e.error}")
```

#### Installments Validation
```python
from tapsilat_py.validators import validate_installments

# Valid installment strings
installments = validate_installments("1,2,3,6")     # Returns: [1, 2, 3, 6]
installments = validate_installments("1, 2, 3, 6") # Handles spaces
installments = validate_installments("")            # Returns: [1] (default)

# Raises APIException for invalid values
try:
    validate_installments("1,15,abc")  # 15 > 12, abc is not a number
except APIException as e:
    print(f"Error: {e.error}")
```

### Order create process
```python
from tapsilat_py.models import BuyerDTO, OrderCreateDTO

# GSM number will be automatically validated in create_order
buyer = BuyerDTO(
    name="John", 
    surname="Doe", 
    email="test@example.com",
    gsm_number="+90 555 123-45-67"  # Will be cleaned automatically
)
order = OrderCreateDTO(amount=100, currency="TRY", locale="tr", buyer=buyer)

order_response = client.create_order(order)
```
### General Order Methods
```python
from tapsilat_py.models import (
    CancelOrderDTO, RefundOrderDTO, RefundAllOrderDTO, OrderPaymentDetailDTO,
    GetOrderPaymentsRequest, TerminateRequest, OrderManualCallbackDTO, 
    OrderRelatedReferenceDTO, OrderPaymentOptionsUpdateDTO, SplitOrderItemPaymentDTO,
    AddBasketItemRequest, RemoveBasketItemRequest, UpdateBasketItemRequest, BasketItemDTO,
    OrderAccountingRequest, OrderPostAuthRequest, OrderOIPDTO
)

# Fetch orders
order_details = client.get_order("reference_id")
order_details = client.get_order_by_conversation_id("conversation_id")
order_list = client.get_order_list(page=1, per_page=10)
submerchants = client.get_order_submerchants(page=1, per_page=10)
checkout_url = client.get_checkout_url("reference_id")

# Status and Details
status = client.get_order_status("reference_id")
transactions = client.get_order_transactions("reference_id")
payment_details = client.get_order_payment_details_by_id("reference_id")
payment_details_dto = client.get_order_payment_details(OrderPaymentDetailDTO(reference_id="reference_id"))
payments = client.get_order_payments(GetOrderPaymentsRequest(order_id="order_id"))

# Modifications
client.cancel_order(CancelOrderDTO(reference_id="reference_id"))
client.refund_order(RefundOrderDTO(amount=100.0, reference_id="reference_id"))
client.refund_all_order(RefundAllOrderDTO(reference_id="reference_id"))
client.create_order_refund_request(RefundOrderDTO(amount=100.0, reference_id="reference_id"))

client.terminate_order(TerminateRequest(reference_id="reference_id"))
client.manual_callback(OrderManualCallbackDTO(reference_id="reference_id"))
client.related_update(OrderRelatedReferenceDTO(reference_id="old_ref", related_reference_id="new_ref"))
client.update_payment_options(OrderPaymentOptionsUpdateDTO(payment_options=["credit_card"], reference_id="reference_id"))
client.split_order_item_payment(SplitOrderItemPaymentDTO(amount=100.0, order_id="order_id", order_item_payment_id="item_id"))

# Basket Item Modifications
basket_item = BasketItemDTO(name="Item 1", price=100.0, quantity=1, sub_merchant_key="...")
client.add_basket_item(AddBasketItemRequest(order_reference_id="ref_id", basket_item=basket_item))
client.remove_basket_item(RemoveBasketItemRequest(order_reference_id="ref_id", basket_item_id="basket_item_id"))
client.update_basket_item(UpdateBasketItemRequest(order_reference_id="ref_id", basket_item=basket_item))

# Additional Actions
client.order_callback("order_id")
client.order_vpos_query("order_id")
client.order_accounting(OrderAccountingRequest(order_reference_id="reference_id"))
client.order_postauth(OrderPostAuthRequest(amount=100.0, reference_id="reference_id"))
client.add_order_oip(OrderOIPDTO(order_id="order_id", basket_item_id="item_id", amount=100.0, type=1))
```

### Order Terms Methods
```python
from tapsilat_py.models import (
    OrderPaymentTermCreateDTO, OrderPaymentTermDeleteDTO, OrderPaymentTermUpdateDTO, OrderTermRefundRequest
)

# Create
term_create = OrderPaymentTermCreateDTO(order_id="order_id", term_reference_id="term_ref", amount=5000, due_date="2025-10-10", term_sequence=1, required=True, status="pending")
client.create_order_term(term_create)

# Retrieve
client.get_order_term("term_reference_id")

# Update & Delete
client.update_order_term(OrderPaymentTermUpdateDTO(term_reference_id="term_ref", due_date="2025-12-10", required=True, amount=5000, status="pending", term_sequence=1, paid_date=None))
client.delete_order_term(OrderPaymentTermDeleteDTO(order_id="order_id", term_reference_id="term_ref"))

# Refund
client.refund_order_term(OrderTermRefundRequest(term_id="term_id", amount=1200))
```

### Raw File Downloads (PDF, Excel)
```python
# Raw file downloads return a FileResponse object.
# Use .download(destination) to save it. If destination is None, it saves to the current directory.
pdf_file = client.get_order_pdf("ORDER_ID")
pdf_file.download("/path/to/save.pdf")

excel_file = client.get_order_excel("ORDER_ID")
excel_file.download()
```

## Submerchant Methods
```python
from tapsilat_py.models import SubmerchantCreateDTO, SubmerchantUpdateDTO

client.create_submerchant(SubmerchantCreateDTO(name="Test Submerchant"))
client.get_submerchant("id")
client.get_suborganization_by_submerchant("id")
client.update_submerchant("id", SubmerchantUpdateDTO(name="Updated"))
client.delete_submerchant("id")
client.list_submerchants(page=1, per_page=10)
```

## Organization Management
```python
from tapsilat_py.models import (
    CallbackURLDTO, OrgCreateBusinessRequest, GetUserLimitRequest, SetLimitUserRequest,
    GetVposRequest, OrgCreateUserReq, OrgUserVerifyReq, OrgUserMobileVerifyReq, OrgUserTokenCreateReq
)

# Settings & Metadata
settings = client.get_organization_settings()
callbacks = client.get_organization_callback()
client.update_organization_callback(CallbackURLDTO(callback_url="https://..."))
meta_info = client.get_organization_meta("meta_name")
scopes = client.get_organization_scopes()
presets = client.get_organization_currency_presets()

# Business, Currencies, and VPOS
client.create_organization_business(OrgCreateBusinessRequest(business_name="Test", business_type=1, email="test@test.com", ...))
currencies = client.get_organization_currencies()
vpos_list = client.list_organization_vpos(GetVposRequest(currency_id="currency_id"))

# Limits
limits = client.get_organization_limits()
client.get_organization_limit_user(GetUserLimitRequest(user_id="user_id"))
client.set_organization_limit_user(SetLimitUserRequest(limit_id="limit_id", user_id="user_id"))

# Suborganizations
client.get_organization_suborganizations()
client.get_organization_suborganization_details("suborg_id")
client.get_organization_suborganization_submerchants("suborg_id")

# User Management
client.create_organization_user(OrgCreateUserReq(email="test@example.com", first_name="John", ...))
client.verify_organization_user(OrgUserVerifyReq(user_id="user_id"))
client.verify_organization_user_mobile(OrgUserMobileVerifyReq(user_id="user_id"))
client.create_organization_user_token(OrgUserTokenCreateReq(email="test@example.com", expire=3600))
```

## System & Webhooks

### Verify Webhook Request
```python
# This verifies the signature sent by Tapsilat webhook
is_valid = client.verify_webhook(
    payload='{"event": "order.completed", "data": {...}}',
    signature="some-hash-signature"
)
```

### Get System Definitions and Statuses
```python
order_statuses = client.get_system_order_statuses()
basket_item_types = client.get_system_basket_item_types()
error_codes = client.get_system_error_codes()
payment_term_statuses = client.get_system_payment_term_statuses()
product_types = client.get_system_product_types()
shortcut_types = client.get_system_shortcut_types()
transaction_payment_types = client.get_system_transaction_payment_types()
transaction_purposes = client.get_system_transaction_purposes()
transaction_statuses = client.get_system_transaction_statuses()
```

## Subscription Management

The SDK provides comprehensive subscription management features.

### Create Subscription
```python
from tapsilat_py.models import (
    SubscriptionCreateRequest,
    SubscriptionUser,
    SubscriptionBilling
)

# Create user and billing information
user = SubscriptionUser(
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
    phone="+905551234567",
    identity_number="12345678901"
)

billing = SubscriptionBilling(
    address="Test Address",
    city="Istanbul",
    country="TR",
    contact_name="John Doe",
    zip_code="34000"
)

# Create subscription request
subscription_request = SubscriptionCreateRequest(
    amount=100.0,
    currency="TRY",
    cycle=12,  # Number of billing cycles
    period=1,  # Billing period (1=monthly, 3=quarterly, 12=yearly)
    payment_date=1,  # Day of month for payment
    title="Monthly Subscription",
    external_reference_id="ext_ref_123",
    user=user,
    billing=billing,
    success_url="https://example.com/success",
    failure_url="https://example.com/failure"
)

response = client.create_subscription(subscription_request)
print(f"Subscription ID: {response.reference_id}")
print(f"Order Reference ID: {response.order_reference_id}")
```

### Get Subscription Details
```python
from tapsilat_py.models import SubscriptionGetRequest

# Get by reference_id
request = SubscriptionGetRequest(reference_id="sub_ref_123")
subscription = client.get_subscription(request)

# Or get by external_reference_id
request = SubscriptionGetRequest(external_reference_id="ext_ref_123")
subscription = client.get_subscription(request)

print(f"Subscription title: {subscription.title}")
print(f"Amount: {subscription.amount} {subscription.currency}")
print(f"Status: {subscription.payment_status}")
print(f"Active: {subscription.is_active}")
```

### List Subscriptions
```python
subscriptions = client.list_subscriptions(page=1, per_page=10)
print(f"Total subscriptions: {subscriptions.get('total')}")
for sub in subscriptions.get('data', []):
    print(f"Subscription: {sub['reference_id']} - {sub['title']}")
```

### Cancel Subscription
```python
from tapsilat_py.models import SubscriptionCancelRequest

# Cancel by reference_id
request = SubscriptionCancelRequest(reference_id="sub_ref_123")
response = client.cancel_subscription(request)

# Or cancel by external_reference_id
request = SubscriptionCancelRequest(external_reference_id="ext_ref_123")
response = client.cancel_subscription(request)
```

### Get Subscription Redirect URL
```python
from tapsilat_py.models import SubscriptionRedirectRequest

request = SubscriptionRedirectRequest(subscription_id="sub_id_123")
response = client.redirect_subscription(request)
print(f"Redirect to: {response.url}")
```

## Error Handling

All API methods raise `APIException` on errors:

```python
from tapsilat_py.exceptions import APIException

try:
    order = client.create_order(order_data)
except APIException as e:
    print(f"Status Code: {e.status_code}")
    print(f"Error Code: {e.code}")
    print(f"Error Message: {e.error}")
```

