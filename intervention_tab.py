import streamlit as st
import pandas as pd
import random
from interventions import INTERVENTIONS
from utils import get_map_data

def render_intervention_management():
    """Render the intervention management interface"""
    if "sim_run" in st.session_state and st.session_state.sim_run:
        st.markdown("### Suggested Interventions")
        updated = False
        to_remove = []
        to_add = []

        cols = st.columns(3)
        for idx, iv in enumerate(st.session_state.active_interventions):
            with cols[idx % 3]:
                st.write(iv)
                if st.button("❌ Remove", key=f"remove_{iv}"):
                    to_remove.append(iv)
                if st.button("🔁 Replace", key=f"replace_{iv}"):
                    available = [x for x in INTERVENTIONS if x not in st.session_state.active_interventions]
                    if available:
                        new_iv = random.choice(available)
                        to_remove.append(iv)
                        to_add.append(new_iv)
                        updated = True

        for r in to_remove:
            st.session_state.active_interventions.remove(r)
        for a in to_add:
            st.session_state.active_interventions.append(a)

        remaining = [i for i in INTERVENTIONS if i not in st.session_state.active_interventions]
        extra = st.multiselect("Add interventions:", remaining, key="add_interventions_multi")
        if st.button("Add Selected", key="add_selected_btn"):
            st.session_state.active_interventions.extend(extra)
            updated = True

        max_possible = len(st.session_state.selected_policies) * 3
        ratio = min(1.0, len(st.session_state.active_interventions) / max_possible)
        st.progress(ratio, text=f"Policy goal completeness: {int(ratio * 100)}%")

    else:
        st.info("Run the policy simulation first to view interventions.")

def render_intervention_map():
    """Render the map showing intervention locations"""
    st.map(get_map_data(), latitude=34.3, longitude=10.8, zoom=5, use_container_width=True)

def render_intervention_tab():
    """Main function to render the entire intervention tab"""
    col1, col2 = st.columns(2)
    with col1:
        render_intervention_management()
    with col2:
        render_intervention_map() 