import streamlit as st
from utils import initialize_session_state
from initial_page import render_initial_page, render_welcome_page
from policy_tab import render_policy_tab
from intervention_tab import render_intervention_tab

# Page configuration
st.set_page_config(layout="wide")
# st.title("WEFE Nexus DSS: Policy & Intervention Simulator")

# Initialize session state
initialize_session_state()

# Sidebar Setup
if not st.session_state.session_started:
    render_initial_page()

# Main Interface
if st.session_state.session_started:
    tabs = st.tabs(["Policy View", "Intervention View"])

    # --- POLICY VIEW ---
    with tabs[0]:
        render_policy_tab()

    # --- INTERVENTION VIEW ---
    with tabs[1]:
        render_intervention_tab()

else:
    render_welcome_page() 