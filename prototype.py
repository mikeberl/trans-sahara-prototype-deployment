import streamlit as st
import pandas as pd
import numpy as np
import random
import json
from policies import POLICY_DETAILS
from interventions import INTERVENTIONS

st.set_page_config(layout="wide")
st.title("WEFE Nexus DSS: Policy & Intervention Simulator")

if "session_started" not in st.session_state:
    st.session_state.session_started = False
if "selected_policies" not in st.session_state:
    st.session_state.selected_policies = []
if "policy_inputs" not in st.session_state:
    st.session_state.policy_inputs = {}
if "policy_suggestions" not in st.session_state:
    st.session_state.policy_suggestions = {}
if "active_interventions" not in st.session_state:
    st.session_state.active_interventions = []

# Sidebar Setup
if not st.session_state.session_started:
    st.sidebar.header("1. Select Living Lab and Impact Weights")

    # Load living labs from JSON
    with open("assets/data/livinglab.json", "r", encoding="utf-8") as f:
        livinglabs = json.load(f)
    regions = [lab["name"] for lab in livinglabs]
    selected_lab = st.sidebar.selectbox("Select a Living Lab", regions, key="select_lab")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Indicator Weights")
    water_w = st.sidebar.slider("Water Availability", 0, 5, 3, key="water_weight")
    energy_w = st.sidebar.slider("Energy Demand", 0, 5, 3, key="energy_weight")
    food_w = st.sidebar.slider("Agricultural Production", 0, 5, 3, key="food_weight")
    eco_w = st.sidebar.slider("Ecosystem Health", 0, 5, 3, key="eco_weight")

    budget = st.sidebar.number_input("Budget (Million USD)", 0, 1000, 10, 1, key="budget")
    time_range = st.sidebar.number_input("Simulation Year", 2030, 2100, 2030, 5, key="sim_year")
    time_interval = st.sidebar.number_input("Interval (years)", 1, 20, 5, 1, key="interval")

    if st.sidebar.button("Start Session", key="start_session"):
        st.session_state.session_started = True
        st.session_state.selected_lab = selected_lab
        st.session_state.policy_weights = {
            "Water": water_w, "Energy": energy_w, "Food": food_w, "Ecosystem": eco_w
        }
        st.rerun()

# Main Interface
if st.session_state.session_started:
    tabs = st.tabs(["Policy View", "Intervention View"])

    # --- POLICY VIEW ---
    with tabs[0]:
        st.subheader(f"Policy View - {st.session_state.selected_lab}")

        available_policies = [p for p in POLICY_DETAILS if p not in st.session_state.selected_policies]
        new_policy = st.selectbox(
            "Add a Policy:", available_policies, key="add_policy_select"
        )
        if st.button("Add Policy", key="add_policy_btn"):
            st.session_state.selected_policies.append(new_policy)
            st.session_state.policy_inputs[new_policy] = {"intensity": 50, "year": 2030}
            st.session_state.policy_suggestions[new_policy] = random.sample(INTERVENTIONS, 3)

        for policy in st.session_state.selected_policies:
            details = POLICY_DETAILS[policy]
            with st.container(border=True):
                st.subheader(policy)

                col1, col2 = st.columns([3, 1])
                with col1:
                    intensity = st.select_slider(
                        f"Minimum Expected Goal for {policy}",
                        options=list(range(0, 105, 5)),
                        value=st.session_state.policy_inputs[policy]["intensity"],
                        key=f"intensity_{policy}"
                    )
                    st.session_state.policy_inputs[policy]["intensity"] = intensity

                with col2:
                    st.button("Compare", key=f"compare_{policy}")
                    st.button("Advanced Settings", key=f"adv_{policy}")

                with st.expander("View Details", expanded=False):
                    colA, colB = st.columns(2)
                    with colA:
                        st.markdown("**Implementation Info:**")
                        st.write(f"• Time: {details['avg_completion_time']}")
                        st.write(f"• Cost: {details['avg_realization_cost']}")
                        st.write(f"• Maintenance: {details['avg_maintenance_cost']}")
                        st.write(f"• Policy Type: {details.get('policy_type', '-')}")
                        st.write(f"• SDG Targets: {details.get('sdg_targets', '-')}")
                        st.write(f"• CO2 Reduction: {details.get('co2_reduction', '-')}")
                        st.write(f"• Biodiversity Impact: {details.get('biodiversity_impact', '-')}")
                        st.write(f"• Resilience Score: {details.get('resilience_score', '-')}")
                        st.write(f"• Stakeholder Involvement: {details.get('stakeholder_involvement', '-')}")
                    with colB:
                        st.markdown("**Indicators of Policy Success:**")
                        for idx, (ind_name, ind_value) in enumerate(details.get('indicators', {}).items()):
                            if idx == 0:
                                st.markdown(f"• {ind_name}: {ind_value} <span style='color:red'>Actual state: {ind_value}</span>", unsafe_allow_html=True)
                            elif idx == 1:
                                st.markdown(f"• {ind_name}: {ind_value} <span style='color:green'>Already satisfied</span>", unsafe_allow_html=True)
                            elif idx == 2:
                                st.markdown(f"• {ind_name}: {ind_value} <span style='color:gray'>No data</span>", unsafe_allow_html=True)
                            else:
                                st.write(f"• {ind_name}: {ind_value}")
                        st.markdown("**Expected Impacts:**")
                        for k, v in details['expected_impact'].items():
                            color = "green" if "+" in v else "red" if "-" in v else "gray"
                            st.markdown(f"• {k}: <span style='color:{color}'>{v}</span>", unsafe_allow_html=True)
                    with st.container(border=True):
                        st.markdown("**Suggested Interventions:**")
                        indicator_names = list(details.get('indicators', {}).keys())
                        first_indicator = indicator_names[0] if indicator_names else None
                        for i in st.session_state.policy_suggestions[policy]:
                            if first_indicator:
                                st.markdown(f"• {i} <span style='color:green'>({first_indicator})</span>", unsafe_allow_html=True)
                            else:
                                st.write(f"• {i}")

        if st.button("Run Policy Simulation", key="run_sim_btn"):
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

        if "policy_scores" in st.session_state:
            overall_score = round(np.mean(list(st.session_state.policy_scores.values())), 1)
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.header("Overall WEFE Policy Score")
                with col2:
                    st.markdown(f"<h1 style='text-align: right; color: #2c3e50;'>{overall_score}</h1>", unsafe_allow_html=True)
                st.markdown("""
                    This score reflects the average policy impact across all four pillars of the WEFE Nexus.
                    Explore the breakdown by pillar below. Each pillar shows how Access and Availability are affected
                    by the current policy scenario.
                """, unsafe_allow_html=True)
                st.info("Red and green numbers indicate the delta from the baseline scenario.")

            detailed_scores = {
                "Water": {"icon": "💧", "Access": {"Drinking Water Access (%)": 97.5, "Sanitation Access (%)": 80.8, "IWRM Implementation (1–100)": 60},
                          "Availability": {"Freshwater Withdrawal (% resources)": 92.1, "Renewable Water per Capita (m³)": 344.9, "Environmental Flow (10⁶ m³/yr)": 2.2, "Avg Precipitation (mm/yr)": 207}},
                "Energy": {"icon": "⚡", "Access": {"Electricity Access (%)": 99.9, "Renewable Energy Consumption (%)": 12.9, "Renewable Electricity Output (%)": 2.8, "CO₂ Emissions (t/capita)": 2.4},
                          "Availability": {"Power Consumption (kWh/capita)": 1408.1, "Net Energy Imports (%)": 36.2}},
                "Food": {"icon": "🌾", "Access": {"Undernourishment (%)": 3.1, "Wasting (children <5) (%)": 2.1, "Stunting (children <5) (%)": 8.6, "Adult Obesity (%)": 26.9},
                         "Availability": {"Protein Supply (g/capita/day)": 99.7, "Cereal Yield (kg/ha)": 1453.8, "Dietary Energy Adequacy (%)": 148}},
                "Ecosystem": {"icon": "🌿", "Health": {"Biodiversity Index (simulated)": 65.0, "Land Degradation Rate (%)": 12.4, "Protected Areas (% land)": 14.8}}
            }

            cols = st.columns(4)
            for i, (pillar, data) in enumerate(detailed_scores.items()):
                icon = data.pop("icon", "")
                with cols[i]:
                    with st.container(border=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"<h3>{icon} {pillar}</h3>", unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"<h3 style='text-align:right'>{round(np.random.uniform(50, 100), 1)}</h3>", unsafe_allow_html=True)

                        for subpillar, indicators in data.items():
                            st.divider()
                            st.markdown(f"<h4 style='color:#333;'>{subpillar}</h4>", unsafe_allow_html=True)
                            for ind_name, ind_value in indicators.items():
                                delta = round(np.random.uniform(-10, 10), 1)
                                delta_color = "#2ecc71" if delta >= 0 else "#e74c3c"
                                delta_sign = "+" if delta >= 0 else "−"
                                delta_str = f"<span style='color:{delta_color}; font-weight:500'>{delta_sign}{abs(delta)}</span>"
                                st.markdown(f"<div style='margin-bottom:0.7em'><div style='font-size:0.9rem;color:#444'>{ind_name}</div><div style='font-size:1.4rem;font-weight:600;color:#111'>{ind_value} {delta_str}</div></div>", unsafe_allow_html=True)

    # --- INTERVENTION VIEW ---
    with tabs[1]:
        col1, col2 = st.columns(2)
        with col1:
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
        with col2:
            st.map(pd.DataFrame({"lat": [34.8], "lon": [10.1]}), latitude=34.3, longitude=10.8, zoom=5, use_container_width=True)

else:
    st.info("Please configure the session in the sidebar and start.")
    st.map(pd.DataFrame({"lat": [34.8], "lon": [10.1]}), latitude=34.3, longitude=10.8, zoom=5, use_container_width=True, height=1000)
