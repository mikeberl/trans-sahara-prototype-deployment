import streamlit as st
import os
import base64
from utils import initialize_session_state
from initial_page import render_initial_page, render_welcome_page
from policy_tab import render_policy_tab
from intervention_tab import render_intervention_tab

# Page configuration
st.set_page_config(layout="wide", page_title="Trans-Sahara Support Tool")
# st.title("WEFE Nexus DSS: Policy & Intervention Simulator")

# Initialize session state
initialize_session_state()

if not st.session_state.session_started:
    try:
        st.sidebar.image("assets/transahara-logo-fullcolor.jpg", use_column_width=True)
    except Exception:
        st.sidebar.markdown("**Trans-Sahara**")


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

# Page footer (part of main app): EU funding notice
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
