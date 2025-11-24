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
```python
term = OrderPaymentTermUpdateDTO(term_reference_id="TERM-123000457",due_date="2025-12-10 00:00",required=True)
client.update_order_term(term)
```
### Refund order term
```python
term_refund = OrderTermRefundRequest(term_reference_id="TERM-123000456",amount=1200)
client.refund_order_term(term_refund)
```
### Terminate order term
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

### Get Organization Settings
```python
settings = client.get_organization_settings()
print(f"Organization settings: {settings}")
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

