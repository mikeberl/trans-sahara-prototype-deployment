import streamlit as st
import json
import pandas as pd
from typing import Dict, List, Any
import plotly.graph_objects as go
from initial_page import get_selected_lab_info

# Load policies data
def load_policies():
    """Load policies from JSON file"""
    try:
        with open('policies.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Policies file not found!")
        return []

def get_policy_categories(policies: List[Dict]) -> List[str]:
    """Extract unique policy categories from policies"""
    categories = set()
    for policy in policies:
        if 'policy_type' in policy:
            categories.add(policy['policy_type'])
    return sorted(list(categories))

def get_policies_by_category(policies: List[Dict], category: str) -> List[Dict]:
    """Get policies filtered by category"""
    return [policy for policy in policies if policy.get('policy_type') == category]

def get_category_color(category: str) -> str:
    """Get color for WEFE category"""
    colors = {
        'Water': '#3498db',      # Blue
        'Energy': '#f39c12',     # Orange
        'Food': '#27ae60',       # Green
        'Ecosystem': '#8e44ad',  # Purple
        'Economic': '#e74c3c',   # Red
        'Social': '#95a5a6'      # Gray
    }
    return colors.get(category, '#34495e')  # Default dark blue

def get_policy_type_color(policy_type: str) -> str:
    """Get display color for a policy type/category"""
    type_colors = {
        'WEFE': '#2c3e50',        # Dark blue
        'Agroforestry': '#27ae60',# Green
        'Others': '#7f8c8d'       # Gray
    }
    return type_colors.get(policy_type, '#34495e')

def infer_policy_pillar(policy: Dict) -> str:
    """Infer which WEFE pillar (water, energy, food, ecosystems) a policy most closely relates to.

    Falls back to simple heuristics using policy_type and title keywords.
    Returns one of: 'water', 'energy', 'food', 'ecosystems' or '' if unknown.
    """
    ptype = (policy.get('policy_type') or '').lower()
    title = (policy.get('title') or '').lower()

    # Direct mapping if policy_type already matches a pillar
    if ptype in ['water', 'energy', 'food', 'ecosystem', 'ecosystems']:
        return 'ecosystems' if ptype == 'ecosystem' else ptype

    # Heuristics based on title keywords
    if any(k in title for k in ['water', 'irrigation', 'wastewater']):
        return 'water'
    if any(k in title for k in ['energy', 'renewable', 'electric', 'power']):
        return 'energy'
    if any(k in title for k in ['agri', 'food', 'nutrition', 'farm']):
        return 'food'
    if any(k in title for k in ['eco', 'biodiver', 'forest', 'marine', 'green', 'urban green', 'conservation']):
        return 'ecosystems'

    return ''

def render_synergy_tradeoff_item(item: Dict, policy_title: str, is_synergy: bool = True):
    """Render a single synergy or trade-off item"""
    category = item.get('category', 'Unknown')
    color = get_category_color(category)
    
    # Create a container with colored background based on category
    bg_color = color + "20"  # Add transparency to the color
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<span style='color: {color}; font-weight: bold;'>{item['title']}</span>", unsafe_allow_html=True)
        with col2:
            unique_key = f"info_{policy_title}_{item['title']}_{is_synergy}".replace(" ", "_").replace("-", "_")
            show_info = st.button("ℹ️", key=unique_key, help="Click for description")
        
    if show_info:
        st.info(item['description'])
        #   st.write(f"• **Category:** {category}")
        #   st.write(f"• **Affected Indicators:** {item['affected_indicators']}")
    
    # st.divider()

def render_policy_details(policy: Dict):
    """Render detailed view of a single policy"""
    with st.expander(f"📋 {policy['title']}", expanded=False):

        st.write(policy['description'])

        col1, col2, col3 = st.columns(3)
 
        with col1:
            st.markdown("**Implementation Details:**")
            st.write(f"• **Time:** {policy['avg_completion_time']}")
            st.write(f"• **Cost:** {policy['avg_realization_cost']}")
            st.write(f"• **Maintenance:** {policy['avg_maintenance_cost']}")
            st.write(f"• **Type:** {policy['policy_type']}")
        
        with col2:
            st.markdown("**Performance Metrics:**")
            st.write(f"• **Resilience Score:** {policy['resilience_score']}")
            st.write(f"• **Stakeholder Involvement:** {policy['stakeholder_involvement']}")
            st.write(f"• **CO2 Reduction:** {policy['co2_reduction']}")
            st.write(f"• **Biodiversity Impact:** {policy['biodiversity_impact']}")
        
        with col3:
            unique_add_key = f"add_{policy['title']}".replace(" ", "_").replace("-", "_")
            if st.button("➕ Add Policy", key=unique_add_key):
                if 'selected_policies' not in st.session_state:
                    st.session_state.selected_policies = []
                if policy['title'] not in st.session_state.selected_policies:
                    st.session_state.selected_policies.append(policy['title'])
                st.rerun()
        
        st.divider()
        
        # st.markdown("### Synergies & Trade-offs")
        
        col_syn, col_trade = st.columns(2)
        
        with col_syn:
            st.markdown("#### 🟢 Synergies")
            if 'synergies' in policy and policy['synergies']:
                for synergy in policy['synergies']:
                    render_synergy_tradeoff_item(synergy, policy['title'], is_synergy=True)
            else:
                st.info("No synergies identified for this policy.")
        
        with col_trade:
            st.markdown("#### 🔴 Trade-offs")
            if 'trade_offs' in policy and policy['trade_offs']:
                for trade_off in policy['trade_offs']:
                    render_synergy_tradeoff_item(trade_off, policy['title'], is_synergy=False)
            else:
                st.info("No trade-offs identified for this policy.")

def render_policy_tab():
    """Main function to render the entire policy tab"""
    st.subheader(f"Policy View - {st.session_state.selected_lab}")
    
    col1, col2 = st.columns(2)
    with col1:
        # Load policies
        policies = load_policies()
        
        if not policies:
            st.error("No policies available!")
            return
        
        # Get policy categories
        categories = get_policy_categories(policies)
        
        # Category selection
        selected_category = st.selectbox(
            "Select Policy Category:",
            categories,
            key="policy_category_select"
        )
        
        if selected_category:
            # Get policies for selected category
            category_policies = get_policies_by_category(policies, selected_category)
            
            if category_policies:
                # st.markdown(f"### Policies in {selected_category}")
                st.markdown(f"### Found {len(category_policies)} policies in this category.")
                
                # Display policies
                for policy in category_policies:
                    render_policy_details(policy)
            else:
                st.info(f"No policies found in the {selected_category} category.")
        else:
            st.info("Please select a policy category to view available policies.")
    
    with col2:
        # --- Selected Policies (before radar plot)
        st.markdown("### Selected Policies")
        selected_titles = st.session_state.get('selected_policies', [])
        # Build quick lookup map for colors/policy types
        policies_by_title = {p['title']: p for p in load_policies()}
        if selected_titles:
            for sel_title in selected_titles:
                p = policies_by_title.get(sel_title)
                if not p:
                    continue
                color = get_policy_type_color(p.get('policy_type', 'Others'))
                safe_key = sel_title.replace(" ", "_").replace("-", "_")
                row_c1, row_c2, row_c3, row_c4 = st.columns([0.55, 0.15, 0.15, 0.15])
                with row_c1:
                    st.markdown(f"<span style='color:{color}; font-weight:600'>{sel_title}</span>", unsafe_allow_html=True)
                with row_c2:
                    st.button("View similar", key=f"view_sim_{safe_key}")
                with row_c3:
                    st.button("View details", key=f"view_details_{safe_key}")
                with row_c4:
                    if st.button("Remove", key=f"remove_sel_{safe_key}"):
                        st.session_state.selected_policies = [t for t in selected_titles if t != sel_title]
                        st.rerun()
        else:
            st.info("No policies selected yet.")

        selected_lab_name = st.session_state.get('selected_lab')
        lab_info = get_selected_lab_info(selected_lab_name) if selected_lab_name else None
        if lab_info and 'wefe_pillars' in lab_info:
            categories = ["Water", "Energy", "Food", "Ecosystems"]
            pillar_keys = ["water", "energy", "food", "ecosystems"]
            values = [lab_info['wefe_pillars'].get(k, {}).get('score', 0) for k in pillar_keys]

            # Build scenario values (initially equal to base values)
            scenario_values = values.copy()

            # If there are selected policies, boost the corresponding pillar by +3 per policy
            selected_titles_for_boost = st.session_state.get('selected_policies', [])
            if selected_titles_for_boost:
                # We may have a map of policies by title above; rebuild defensively if not present
                try:
                    policies_map_local = policies_by_title  # type: ignore # may be defined above
                except NameError:
                    policies_map_local = {p['title']: p for p in load_policies()}

                boosts = {key: 0 for key in pillar_keys}
                for t in selected_titles_for_boost:
                    p = policies_map_local.get(t)
                    if not p:
                        continue
                    pillar = infer_policy_pillar(p)
                    if pillar in boosts:
                        boosts[pillar] += 10

                # Apply boosts with clamping to [0, 100]
                for idx, key in enumerate(pillar_keys):
                    boosted = scenario_values[idx] + boosts.get(key, 0)
                    if boosted > 100:
                        boosted = 100
                    if boosted < 0:
                        boosted = 0
                    scenario_values[idx] = boosted

            # Close the radar shape by repeating the first point
            r_values = values + [values[0]]
            theta_values = categories + [categories[0]]
            r_values_scenario = scenario_values + [scenario_values[0]]

            fig = go.Figure()
            fig.add_trace(
                go.Scatterpolar(
                    r=r_values,
                    theta=theta_values,
                    fill='toself',
                    name='WEFE Score',
                    line_color='#2c3e50',
                    fillcolor='rgba(44,62,80,0.25)'
                )
            )
            # Add scenario overlay: grey if no policies selected, green if any selected
            has_selection = bool(st.session_state.get('selected_policies'))
            scenario_line_color = '#27ae60' if has_selection else '#7f8c8d'
            scenario_fill_color = 'rgba(39,174,96,0.4)' if has_selection else 'rgba(127,140,141,0.3)'
            fig.add_trace(
                go.Scatterpolar(
                    r=r_values_scenario,
                    theta=theta_values,
                    fill='toself',
                    name='Scenario',
                    line_color=scenario_line_color,
                    fillcolor=scenario_fill_color
                )
            )
            fig.update_layout(
                title=f"WEFE Scores – {lab_info.get('name', selected_lab_name)}",
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)
            # Add a button to show/hide full report
            if st.button("Full Report", key="full_report_button"):
                st.session_state.show_full_report = not st.session_state.get('show_full_report', False)
            
            # Only display the full report if the button has been clicked
            if st.session_state.get('show_full_report', False):
                st.write(lab_info['wefe_pillars'])
        else:
            st.info("WEFE scores not available for the selected living lab.")
			