import os
from tapsilat_py.client import TapsilatAPI
from dotenv import load_dotenv

load_dotenv()
client = TapsilatAPI(api_key=os.environ.get("TAPSILAT_API_KEY"))
print(client.get_orders(per_page="1"))
