import base64
import streamlit as st
import pandas as pd
import numpy as np
import random
import json
from policies import POLICY_DETAILS
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
    st.session_state.previous_scores = {
        k: v + np.random.randint(-10, 10)
        for k, v in st.session_state.policy_scores.items()
    }
    st.session_state.active_interventions = list({
        i for p in st.session_state.selected_policies
        for i in st.session_state.policy_suggestions[p]
    })


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
    
def render_footer():
    """Render the footer of the app"""
    footer_logo_b64 = ""
    try:
        with open("assets/founded-logo.jpg", "rb") as f:
            footer_logo_b64 = base64.b64encode(f.read()).decode()
    except Exception:
        pass

    st.markdown(
        """
        <style>
            .app-footer { background: #ffffff; border-top: 1px solid #e6e6e6; padding: 10px 16px; margin-top: 12px; }
            .app-footer .footer-inner { display: flex; align-items: center; gap: 16px; }
            .app-footer .footer-text { font-size: 12px; color: #333333; }
            .app-footer img { height: 40px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class=\"app-footer\">
            <div class=\"footer-inner\">
                {('<img src=\"data:image/jpeg;base64,' + footer_logo_b64 + '\" alt=\"EU logo\"/>') if footer_logo_b64 else ''}
                <div class=\"footer-text\">
                    Funded by the European Union under the Horizon Europe Framework Programme Grant Agreement Nº: 101182176. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or of the European Research Executive Agency. Neither the European Union nor the granting authority can be held responsible for them.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )