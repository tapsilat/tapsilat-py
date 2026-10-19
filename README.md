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
### Get order details
```python
reference_id = "mock-uuid-reference-id"
order_details = client.get_order(reference_id)
```
### Get order details by conversation id
```python
conversation_id = "mock-uuid-conversation-id"
order_details = client.get_order_by_conversation_id(reference_id)
```
### Get order list
```python
order_list = client.get_order_list(page=1, per_page=5)
```
### Get order submerchants
```python
order_list = client.get_order_submerchants(page=1, per_page=5)
```
### Get checkout url
```python
reference_id = "mock-uuid-reference-id"
checkout_url = client.get_checkout_url(reference_id)
```
### Order cancel process
```python
reference_id = "mock-uuid-reference-id"
client.cancel_order(reference_id)
```
### Order refund process
```python
from tapsilat_py.models import RefundOrderDTO
refund_data = RefundOrderDTO(amount=100, reference_id="mock-uuid-reference-id")
client.refund_order(refund_data)
```
### Order refund all process
```python
reference_id = "mock-uuid-reference-id"
client.refund_all_order(reference_id)
```
### Get order payment details
```python
reference_id = "mock-uuid-reference-id"
client.get_order_payment_details(reference_id)
# You can get with conversation_id too
conversation_id = "mock-uuid-conversation-id"
client.get_order_payment_details(reference_id, conversation_id)
```
### Get order status
```python
reference_id = "mock-uuid-reference-id"
client.get_order_status(reference_id)
```
### Get order transactions
```python
reference_id = "mock-uuid-reference-id"
client.get_order_transactions(reference_id)
```
### Get order term
```python
reference_id = "mock-uuid-reference-id"
client.get_order_term(reference_id)
```
### Create order term
```python
order_id = "mock-order-id"
terms = [
    OrderPaymentTermCreateDTO(order_id=order_id, amount=5000, term_reference_id="TERM-123000456",due_date="2025-10-10 00:00",term_sequence=1),
    OrderPaymentTermCreateDTO(order_id=order_id, amount=5000, term_reference_id="TERM-123000457",due_date="2025-11-10 00:00",term_sequence=2)
]

for term in terms:
    client.create_order_term(term)
```
### Delete order term
```python
order_id = "mock-uuid-order-id"
term_reference_id = "TERM-123000456"
client.delete_order_term(order_id,term_reference_id)
```
### Update order term
The update replaces the term, so send every field. Dates use `YYYY-MM-DD`.
```python
term = OrderPaymentTermUpdateDTO(
    term_reference_id="TERM-123000457",
    term_sequence=2,
    amount=5000,
    due_date="2025-12-10",
    paid_date=None,
    required=True,
    status="pending",
)
client.update_order_term(term)
```
### Refund order term
`term_id` is the term's ID and `reference_id` the order's reference ID.
```python
term_refund = OrderTermRefundRequest(term_id="term-id", reference_id="order-reference-id", amount=1200)
client.refund_order_term(term_refund)
```
### Terminate order
```python
reference_id = "mock-uuid-reference-id"
client.order_terminate(reference_id)
```
### Manual callback for order
```python
reference_id = "mock-uuid-reference-id"
conversation_id = "mock-conversation-id"
client.order_manual_callback(reference_id, conversation_id)
```
### Order related reference update
```python
reference_id = "mock-uuid-reference-id"
related_reference_id = "mock-related-reference-id"
client.order_related_update(reference_id, related_reference_id)
```

## Additional Methods

### Get Orders with Pagination and Filter
```python
# Get orders with pagination
orders = client.get_orders(page="1", per_page="10")

# Get orders for a specific buyer
orders = client.get_orders(page="1", per_page="10", buyer_id="buyer_123")
```

## Organization Management

### Get Settings
```python
settings = client.get_organization_settings()
```

### Callback URL Configuration
```python
from tapsilat_py.models import CallbackURLDTO

callbacks = client.get_organization_callback()
client.update_organization_callback(CallbackURLDTO(callback_url="https://example.com/callback"))
```

### Currencies and Suborganizations
```python
currencies = client.get_organization_currencies()
presets = client.list_organization_currency_presets()
client.create_organization_currency("USD")

suborganizations = client.get_organization_suborganizations(page=1, per_page=10)
suborganization = client.get_suborganization("suborganization-id")

meta = client.get_organization_meta("meta-name")
limits = client.get_organization_limits("organization-id")
```

### User Management
```python
from tapsilat_py.models import OrgCreateUserReq, OrgUserTokenCreateRequest, OrgUserVerifyReq

client.create_organization_user(OrgCreateUserReq(
    conversation_id="user-1",
    email="test@example.com",
    first_name="John",
    identity_number="11111111111",
    is_mail_verified=False,
    last_name="Doe",
    phone="+905551234567",
    reference_id="user-1",
))
token = client.create_organization_user_token(OrgUserTokenCreateRequest(user_id="user-id", expire=60))
client.verify_organization_user(OrgUserVerifyReq(user_id="user-id"))
```

`get_organization_limit_user` and `set_organization_limit_user` are deprecated: the API has no organization user limit route.

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
```python
# This verifies the signature sent by Tapsilat webhook
is_valid = client.verify_webhook(
    payload='{"event": "order.completed", "data": {...}}',
    signature="some-hash-signature"
)
```

### Get System Order Status
```python
status = client.get_system_order_status()
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

