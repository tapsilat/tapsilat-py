import json

sw = json.load(open('../swagger.json'))
swagger_endpoints = set()
for path in sw['paths'].keys():
    if any(path.startswith(prefix) for prefix in ['/order', '/subscription', '/organization', '/system']):
        swagger_endpoints.add(path)

client_file = "tapsilat_py/client.py"
client_endpoints = set()
with open(client_file, "r") as f:
    for line in f:
        line = line.strip()
        if 'endpoint =' in line:
            # Extract the API string
            ep = line.split('=')[1].strip().strip('"').strip("'")
            client_endpoints.add(ep)
        elif 'endpoint = f"' in line:
            ep = line.split('f"')[1].strip().strip('"').strip("'")
            # Replace curly braces vars with swagger path format {id} etc.
            if '{reference_id}' in ep:
                ep = ep.replace('{reference_id}', '{id}')
            if '{conversation_id}' in ep:
                ep = ep.replace('{conversation_id}', '{id}')
            client_endpoints.add(ep)

print("Endpoints in Client, but not in Swagger:")
for ep in sorted(client_endpoints - swagger_endpoints):
    print("  ", ep)

print("\nEndpoints in Swagger, but not in Client (for these prefixes):")
for ep in sorted(swagger_endpoints - client_endpoints):
    print("  ", ep)
