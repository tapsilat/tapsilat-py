import json
import re

sw = json.load(open('../swagger.json'))
client_file = 'tapsilat_py/client.py'

errors = []

with open(client_file, 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        line = line.strip()
        if 'def ' in line:
            current_method_name = line.split('def ')[1].split('(')[0]
        if 'endpoint =' in line:
            if 'f"' in line or "f'" in line:
                m = re.search(r'f[\"\'](.*?)[\"\']', line)
                if not m: continue
                ep = m.group(1)
                ep_swagger = re.sub(r'\{[^\}]+\}', '{id}', ep)
            else:
                m = re.search(r'[\"\'](.*?)[\"\']', line.split('=')[1])
                if not m: continue
                ep = m.group(1)
                ep_swagger = ep
            
            # Find the HTTP method in the same block
            http_method = None
            for j in range(i, min(i+10, len(lines))):
                if '_make_request(' in lines[j]:
                    m = re.search(r'[\"\'](GET|POST|PUT|PATCH|DELETE)[\"\']', lines[j])
                    if m:
                        http_method = m.group(1).lower()
                        break
            
            if ep_swagger not in sw['paths']:
                errors.append(f"❌ {current_method_name}: Endpoint {ep_swagger} NOT FOUND in swagger.json")
            else:
                if http_method:
                    if http_method not in sw['paths'][ep_swagger]:
                        errors.append(f"❌ {current_method_name}: Endpoint {ep_swagger} does not support {http_method.upper()} in swagger.json (supports: {list(sw['paths'][ep_swagger].keys())})")
                else:
                    errors.append(f"⚠️ {current_method_name}: Couldn't determine HTTP method for {ep}")

for err in errors:
    print(err)
if not errors:
    print("All existing client endpoints match Swagger definitions perfectly!")

