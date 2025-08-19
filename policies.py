import json
import os

def load_policies():
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'data', 'policies.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            policies_list = json.load(f)
        # Convert list to dict for compatibility
        return {p['title']: p for p in policies_list}
    except FileNotFoundError:
        print(f"Error: Could not find policies.json at {json_path}")
        # Check if file exists in current directory
        current_dir_path = 'data/policies.json'
        if os.path.exists(current_dir_path):
            print(f"Found policies.json in current directory: {current_dir_path}")
            with open(current_dir_path, 'r', encoding='utf-8') as f:
                policies_list = json.load(f)
            return {p['title']: p for p in policies_list}
        else:
            print(f"Also checked current directory path: {current_dir_path} - not found")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Files in current directory: {os.listdir('.')}")
            if os.path.exists('data'):
                print(f"Files in data directory: {os.listdir('data')}")
            return {}
    except Exception as e:
        print(f"Error loading policies: {e}")
        return {}

POLICY_DETAILS = load_policies()