import json
import os

def load_policies():
    json_path = os.path.join(os.path.dirname(__file__), 'assets', 'data', 'policies.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        policies_list = json.load(f)
    # Convert list to dict for compatibility
    return {p['title']: p for p in policies_list}

POLICY_DETAILS = load_policies()