import streamlit as st
import pandas as pd
import numpy as np
import random
import json
from policies import POLICY_DETAILS
from interventions import INTERVENTIONS

def load_living_labs():
    """Load living labs data from JSON file"""
    with open("livinglab.json", "r", encoding="utf-8") as f:
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
    st.session_state.previous_scores = {
        k: v + np.random.randint(-10, 10)
        for k, v in st.session_state.policy_scores.items()
    }
    st.session_state.active_interventions = list({
        i for p in st.session_state.selected_policies
        for i in st.session_state.policy_suggestions[p]
    })

def get_detailed_scores():
    """Get detailed scores for each WEFE pillar"""
    return {
        "Water": {"icon": "💧", "Access": {"Drinking Water Access (%)": 97.5, "Sanitation Access (%)": 80.8, "IWRM Implementation (1–100)": 60},
                  "Availability": {"Freshwater Withdrawal (% resources)": 92.1, "Renewable Water per Capita (m³)": 344.9, "Environmental Flow (10⁶ m³/yr)": 2.2, "Avg Precipitation (mm/yr)": 207}},
        "Energy": {"icon": "⚡", "Access": {"Electricity Access (%)": 99.9, "Renewable Energy Consumption (%)": 12.9, "Renewable Electricity Output (%)": 2.8, "CO₂ Emissions (t/capita)": 2.4},
                  "Availability": {"Power Consumption (kWh/capita)": 1408.1, "Net Energy Imports (%)": 36.2}},
        "Food": {"icon": "🌾", "Access": {"Undernourishment (%)": 3.1, "Wasting (children <5) (%)": 2.1, "Stunting (children <5) (%)": 8.6, "Adult Obesity (%)": 26.9},
                 "Availability": {"Protein Supply (g/capita/day)": 99.7, "Cereal Yield (kg/ha)": 1453.8, "Dietary Energy Adequacy (%)": 148}},
        "Ecosystem": {"icon": "🌿", "Health": {"Biodiversity Index (simulated)": 65.0, "Land Degradation Rate (%)": 12.4, "Protected Areas (% land)": 14.8}}
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