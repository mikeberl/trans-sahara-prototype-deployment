"""
Policy-specific utility functions and constants
"""
import json
import os
from typing import Dict

# Color schemes for visualizations
HEATMAP_COLORS = [
    [0.0, '#d32f2f'],    # Red for low values
    [0.5, '#ffc107'],    # Yellow for medium values  
    [1.0, '#4caf50']     # Green for high values
]

# Pillar configuration for heatmaps
PILLAR_COLUMNS = ['Water', 'Energy', 'Food', 'Ecosystems']
PILLAR_KEYS = ['water', 'energy', 'food', 'ecosystems']

# Styling constants for tables
TABLE_STYLES = {
    'neutral': 'background-color: #f8f9fa; color: #495057',
    'positive': 'background-color: #e8f5e9; color: #1b5e20',
    'negative': 'background-color: #ffebee; color: #b71c1c',
    'info': 'background-color: #e3f2fd; color: #1565c0'
}


def load_policies_as_dict():
    """Load policies from JSON file and return as dictionary (for compatibility with legacy code)"""
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


# Policy details dictionary for legacy compatibility
POLICY_DETAILS = load_policies_as_dict()


def get_safe_key(text: str) -> str:
    """Convert text to a safe key for Streamlit components"""
    return text.replace(" ", "_").replace("-", "_")


def format_policy_column_name(policy_title: str) -> str:
    """Format policy title for use as column name with percentage indicator"""
    return f"{policy_title} (%)"


def clamp_value(value: float, min_val: float = 0, max_val: float = 100) -> float:
    """Clamp a value between min and max bounds"""
    return max(min_val, min(max_val, value))
