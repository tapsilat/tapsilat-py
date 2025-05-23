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

.env file
```
TAPSILAT_API_KEY=your_api_key_here
```

## Usage
```python
import os
from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import OrderCreateDTO, BuyerDTO

API_KEY = str(os.getenv("TAPSILAT_API_KEY"))

buyer = BuyerDTO(name="John", surname="Doe", email="test@example.com")
order = OrderCreateDTO(amount=100, currency="TRY", locale="tr-TR", buyer=buyer)

client = TapsilatAPI(API_KEY)

# Order create process
order_response = client.create_order(order)
print("Order create response: ", order_response)

# Get checkout url
checkout_url = client.get_checkout_url(order_response)
print("Checkout URL: ", checkout_url)
```
