import streamlit as st
import os
import base64
from utils import initialize_session_state
from initial_page import render_sidebar_welcome_page, render_welcome_page
from policy_tab import render_policy_tab
from intervention_tab import render_intervention_tab

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

# Page configuration and session state initialization
st.set_page_config(layout="wide", page_title="Trans-Sahara Support Tool")
initialize_session_state()

if not st.session_state.session_started:
    try:
        st.sidebar.image("assets/transahara-logo-fullcolor.jpg", use_container_width=True)
    except Exception:
        st.sidebar.markdown("**Trans-Sahara**")


# Analysis Interface
if st.session_state.session_started:
    # Move weight controls to main area instead of sidebar to allow sidebar to close
    with st.expander("🎛️ WEFE Weight Settings", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            water_w = st.slider("Water", 0, 5, st.session_state.get('policy_weights', {}).get('Water', 3), key="water_weight_session")
        with col2:
            energy_w = st.slider("Energy", 0, 5, st.session_state.get('policy_weights', {}).get('Energy', 3), key="energy_weight_session")
        with col3:
            food_w = st.slider("Food", 0, 5, st.session_state.get('policy_weights', {}).get('Food', 3), key="food_weight_session")
        with col4:
            eco_w = st.slider("Ecosystems", 0, 5, st.session_state.get('policy_weights', {}).get('Ecosystem', 3), key="eco_weight_session")
        
        # Update weights in session state
        st.session_state.policy_weights = {
            "Water": water_w, "Energy": energy_w, "Food": food_w, "Ecosystem": eco_w
        }
    
    tabs = st.tabs(["Policy View", "Intervention View"])
    with tabs[0]:
        render_policy_tab()
    with tabs[1]:
        render_intervention_tab()
else:
    render_sidebar_welcome_page()
    render_welcome_page() 

render_footer()


