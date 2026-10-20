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
payments = client.get_order_payments(GetOrderPaymentsRequest(order_reference_id="reference_id"))

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

# Create: order_id is the order's ID (not its reference ID); dates use YYYY-MM-DD
term_create = OrderPaymentTermCreateDTO(order_id="order_id", term_reference_id="term_ref", amount=5000, due_date="2025-10-10", term_sequence=1, required=True, status="pending")
client.create_order_term(term_create)

# Retrieve
client.get_order_term("term_reference_id")

# Update & Delete
client.update_order_term(OrderPaymentTermUpdateDTO(term_reference_id="term_ref", due_date="2025-12-10", required=True, amount=5000, status="pending", term_sequence=1, paid_date=None))
client.delete_order_term(OrderPaymentTermDeleteDTO(order_id="order_id", term_reference_id="term_ref"))

# Refund: term_id is the term's ID and reference_id the order's reference ID
client.refund_order_term(OrderTermRefundRequest(term_id="term_id", reference_id="order_reference_id", amount=1200))
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

# Limits (the organization user limit methods are deprecated: the API has no such route)
limits = client.get_organization_limits("organization_id")

# Suborganizations
client.get_organization_suborganizations()
client.get_organization_suborganization_details("suborg_id")
client.get_organization_suborganization_submerchants("suborg_id")

# User Management
client.create_organization_user(OrgCreateUserReq(email="test@example.com", first_name="John", ...))
client.verify_organization_user(OrgUserVerifyReq(user_id="user_id"))
client.verify_organization_user_mobile(OrgUserMobileVerifyReq(user_id="user_id"))
client.create_organization_user_token(OrgUserTokenCreateRequest(email="test@example.com", expire=60))  # minutes
```

## Card Installments and Charging

```python
from tapsilat_py.models import CardInstallmentsRequest, InstallmentTableRequest, OrderChargeRequest

options = client.get_card_installments(CardInstallmentsRequest(bin="54066200", amount=100, currency="TRY"))
table = client.get_installment_table(InstallmentTableRequest(amount=100, currency="TRY"))

charge = client.charge_order(OrderChargeRequest(order_reference_id="order-reference-id"))
if not charge.get("isSuccess"):
    print(charge.get("errorCode"), charge.get("message"))
```

## Submerchants, VPOS and Tokenization

Currency fields accept a currency UUID or an organization unit such as `TRY`; the server resolves units.

```python
from tapsilat_py.models import CardTokenizeRequest, SubmerchantCreateRequest, VposCreateRequest

client.create_submerchant(SubmerchantCreateRequest(
    locale="tr",
    conversation_id="seller-1",
    name="Example Ltd",
    email="finance@example.test",
    gsm_number="905551112233",
    sub_merchant_type="PRIVATE_COMPANY",
    tax_number="1234567890",
    currency_id="TRY",
))

pos_list = client.list_vpos(page=1, per_page=20)
card = client.tokenize_card(CardTokenizeRequest("4111111111111111", "John Doe", "12", "30", "123", user_id="customer-1"))
```

`update_vpos` and `update_submerchant` replace the stored record: read it first and send every field back. For example, leaving out `failover` or `tls` stores `false`.

## Marketplace

Marketplace methods use the API version 2 routes derived from `base_url`. Revisions are opaque strings: pass them back exactly as received.

```python
from tapsilat_py.models import MarketplacePayoutApproval, MarketplacePayoutOperationInput

payout = client.get_marketplace_payout(payout_id)
if payout["eligibility_status"] == "eligible" and payout["release_status"] == "awaiting_approval":
    client.approve_marketplace_payouts(MarketplacePayoutApproval(ids=[payout["id"]]))

client.run_marketplace_payout_operation(payout_id, MarketplacePayoutOperationInput(
    kind="update_item",
    idempotency_key="booking-123-allocation-change-1",
    revision=payout["revision"],
    seller_reference=seller["routing_reference"],
    net_amount="60.25",
))
```

Approval policies need a currency UUID; `create_marketplace_approval_policy` and `update_marketplace_approval_policy` resolve units such as `TRY` for you, and `client.resolve_currency_id("TRY")` exposes the same lookup.

## System & Webhooks

### Verify Webhook Request
Tapsilat signs every callback it sends to your callback URLs, and to an order's `payment_success_url` and `payment_failure_url`, with the webhook secret from the panel's callback settings. The `Tapsilat-Signature` header looks like `t=1726480000,v1=5257a8…`: `v1` is the hex HMAC-SHA256 of the timestamp, a dot and the raw body.

`TapsilatAPI.verify_webhook` checks it in constant time and rejects a timestamp more than 5 minutes from the server clock, so a captured callback cannot be replayed. Pass the raw body (`str` or `bytes`), not re-encoded JSON. A Flask handler, for example:
```python
from flask import Flask, request

from tapsilat_py import WEBHOOK_SIGNATURE_HEADER, TapsilatAPI, WebhookEvent

app = Flask(__name__)
WEBHOOK_SECRET = "your_webhook_secret"


@app.post("/tapsilat/callback")
def tapsilat_callback():
    payload = request.get_data()  # the raw body
    signature = request.headers.get(WEBHOOK_SIGNATURE_HEADER, "")  # "Tapsilat-Signature"
    if not TapsilatAPI.verify_webhook(payload, signature, WEBHOOK_SECRET):
        return "", 400

    event = WebhookEvent.from_payload(payload)
    event.type             # "order_lite" (the default), "order", "order_payment_detail", ...
    event.reference_id     # the order's reference ID, whatever the callback type
    event.conversation_id
    event.status           # e.g. "Paid", when the callback type carries a status

    if event.is_paid:
        ...  # fulfil the order
    return "", 200
```

A different tolerance in seconds can be passed as `tolerance` (`0` disables the timestamp check). A bare hex HMAC of the body, with or without a `sha256=` prefix, is still accepted for signatures made the way earlier SDK versions documented.

### Order Statuses
`OrderStatus` has the numeric status codes that callbacks carry, the names `get_order_status()` returns, and the groups most integrations need:
```python
from tapsilat_py import OrderStatus

status = client.get_order_status(reference_id)["status"]  # e.g. "Waiting for payment"

OrderStatus.is_paid(status)      # Paid, Completed, Sub merchant payment approved
OrderStatus.is_failed(status)    # Cancelled, Fraud, Rejected, Failure, Expired, Terminated
OrderStatus.is_refunded(status)  # Refunded, Partially refunded
OrderStatus.code(status)         # 7; also accepts "7" or 7
OrderStatus.name(7)              # "Waiting for payment"
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

All API methods raise `APIException` on errors. Besides `status_code`, `code` and `error` (also available as `message`), it carries the body's `status`, per-field validation `errors` and the `raw_body`. Most "not found" errors arrive as HTTP 400, and rejected state changes (for example approving an ineligible payout) as HTTP 424. A successful status with an HTML body, which a deployment serving the panel UI returns for unknown routes, also raises `APIException`.

```python
from tapsilat_py.exceptions import APIException

try:
    order = client.create_order(order_data)
except APIException as e:
    print(f"Status Code: {e.status_code}")
    print(f"Error Code: {e.code}")
    print(f"Error Message: {e.error}")
```

