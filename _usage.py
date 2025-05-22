import os

from tapsilat_py.client import TapsilatAPI
from tapsilat_py.models import BuyerDTO, OrderCreateDTO

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
