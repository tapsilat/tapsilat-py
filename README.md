# Tapsilat Client SDK for Python

Create orders and retrieve secure checkout URLs.

needs Python3.6+

## Installation
```bash
pip install git+https://github.com/tapsilat/tapsilat-py.git
```
or
```bash
git clone https://github.com/tapsilat/tapsilat-py.git
cd tapsilat-py
pip install -r requirements.txt
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

### Order create process
```python
from tapsilat_py.models import BuyerDTO, OrderCreateDTO
buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
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
