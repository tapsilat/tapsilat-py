import json
import ast

sw = json.load(open('../swagger.json'))
defs = sw.get('definitions', {})

def get_swagger_props(schema_name):
    # Sometimes schema refs exist directly or under definitions
    schema = defs.get(schema_name, {})
    return set(schema.get('properties', {}).keys())

swagger_models = {
    'OrderCreateDTO': 'OrderCreateDTO',
    'SubscriptionCreateRequest': 'v1.CreateSubscriptionRequest',
    'CancelOrderDTO': 'v1.CancelOrderRequest',
    'RefundOrderDTO': 'v1.RefundOrderRequest',
}

with open('tapsilat_py/models.py', 'r') as f:
    tree = ast.parse(f.read())

client_models = {}
for node in tree.body:
    if isinstance(node, ast.ClassDef):
        props = set()
        for child in node.body:
            if isinstance(child, ast.AnnAssign):
                props.add(child.target.id)
        client_models[node.name] = props

for model_name, swagger_ref in swagger_models.items():
    if model_name in client_models:
        s_props = get_swagger_props(swagger_ref)
        c_props = client_models[model_name]
        missing_in_client = s_props - c_props
        extra_in_client = c_props - s_props
        print(f"--- {model_name} ---")
        if missing_in_client: print("  Missing in Client:", missing_in_client)
        if extra_in_client: print("  Extra in Client:", extra_in_client)
        if not missing_in_client and not extra_in_client: print("  Perfect Match!")
    else:
        print(f"Model {model_name} not found in client")

