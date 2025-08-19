import streamlit as st
import os
import base64
from utils import initialize_session_state, render_footer
from initial_page import render_sidebar_welcome_page, render_welcome_page
from policy_tab import render_policy_tab
from intervention_tab import render_intervention_tab

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
    tabs = st.tabs(["Policy View", "Intervention View"])
    with tabs[0]:
        render_policy_tab()
    with tabs[1]:
        render_intervention_tab()
else:
    render_sidebar_welcome_page()
    render_welcome_page() 

render_footer()


