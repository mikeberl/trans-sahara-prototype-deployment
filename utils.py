import streamlit as st
import pandas as pd
import numpy as np
import random
import json
import os
from interventions import INTERVENTIONS

def load_living_labs():
    """Load living labs data from JSON file"""
    with open("data/livinglab.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_regions_from_labs(livinglabs):
    """Extract region names from living labs data"""
    return [lab["name"] for lab in livinglabs]

def initialize_session_state():
    """Initialize all session state variables"""
    if "session_started" not in st.session_state:
        st.session_state.session_started = False
    if "current_selected_lab" not in st.session_state:
        st.session_state.current_selected_lab = None
    if "selected_lab" not in st.session_state:
        st.session_state.selected_lab = "Tunis"  # Default lab
    if "selected_policies" not in st.session_state:
        st.session_state.selected_policies = []
    if "policy_inputs" not in st.session_state:
        st.session_state.policy_inputs = {}
    if "policy_suggestions" not in st.session_state:
        st.session_state.policy_suggestions = {}
    if "active_interventions" not in st.session_state:
        st.session_state.active_interventions = []

def run_policy_simulation():
    """Run the policy simulation and update session state"""
    st.session_state.sim_run = True
    st.session_state.policy_scores = {
        "Water": np.random.randint(0, 100),
        "Energy": np.random.randint(0, 100),
        "Food": np.random.randint(0, 100),
        "Ecosystem": np.random.randint(0, 100)
    }


def get_map_data():
    """Get default map data for Tunisia"""
    return pd.DataFrame({"lat": [34.8], "lon": [10.1]})

def calculate_overall_score(policy_scores):
    """Calculate overall WEFE policy score"""
    return round(np.mean(list(policy_scores.values())), 1)

def get_available_policies():
    """Get list of policies not yet selected"""
    return [p for p in POLICY_DETAILS if p not in st.session_state.selected_policies]

def add_policy_to_session(policy_name):
    """Add a new policy to the session state"""
    st.session_state.selected_policies.append(policy_name)
    st.session_state.policy_inputs[policy_name] = {"intensity": 50, "year": 2030}
    st.session_state.policy_suggestions[policy_name] = random.sample(INTERVENTIONS, 3)
    
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

# WEFE Pillars configuration
PILLARS = [
    {
        "key": "water",
        "label": "Water",
        "icon": "💧",
        "color": "#3498db"
    },
    {
        "key": "energy",
        "label": "Energy",
        "icon": "⚡",
        "color": "#f39c12"
    },
    {
        "key": "food",
        "label": "Food",
        "icon": "🌾",
        "color": "#27ae60"
    },
    {
        "key": "ecosystems",
        "label": "Ecosystems",
        "icon": "🌳",
        "color": "#16a085"
    }
] 
    