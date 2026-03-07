import json

sw = json.load(open('../swagger.json'))
defs = sw.get('definitions', {})

print("OrderCreateRequest in swagger:")
print(list(defs.get('v1.OrderCreateRequest', {}).get('properties', {}).keys()))

print("\nSubscriptionCreateRequest in swagger:")
print(list(defs.get('v1.SubscriptionCreateRequest', {}).get('properties', {}).keys()))
