import streamlit as st
import json
import pandas as pd
from typing import Dict, List, Any
import plotly.graph_objects as go
from initial_page import get_selected_lab_info
from utils import PILLARS, calculate_all_pillar_scores
import os

# Load policies data
def load_policies():
    """Load policies from JSON file"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'data', 'policies.json'), 'r') as f:
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
    """Infer primary WEFE pillar for a policy. Returns one of 'water', 'energy', 'food', 'ecosystems'."""
    title = policy.get('title', '').lower()

    # 1) Look at synergy/trade-off categories first
    def map_category_to_pillar(category: str) -> str | None:
        c = category.strip().lower()
        if c.startswith('water'):
            return 'water'
        if c.startswith('energy'):
            return 'energy'
        if c.startswith('food') or 'agri' in c:
            return 'food'
        if 'ecosystem' in c or 'biodiversity' in c or 'land' in c or 'marine' in c or 'climate' in c:
            return 'ecosystems'
        return None

    for coll_key in ('synergies', 'trade_offs'):
        for item in policy.get(coll_key, []) or []:
            pillar = map_category_to_pillar(str(item.get('category', '')))
            if pillar:
                return pillar

    # 2) Fall back to title keywords
    if 'water' in title:
        return 'water'
    if 'energy' in title or 'renewable' in title:
        return 'energy'
    if 'agri' in title or 'food' in title or 'farm' in title:
        return 'food'
    if 'eco' in title or 'biodiversity' in title or 'green' in title or 'marine' in title or 'climate' in title:
        return 'ecosystems'

    # 3) Default bucket
    return 'ecosystems'

def render_synergy_tradeoff_item(item: Dict, policy_title: str, is_synergy: bool = True):
    """Render a single synergy or trade-off item using Streamlit components only."""
    title_prefix = "🟢" if is_synergy else "🔴"
    header_text = f"{title_prefix} {item.get('title', 'Item')}"

    with st.expander(header_text, expanded=False):
        st.write(item.get('description', ''))
        category = item.get('category')
        if category:
            st.caption(f"Category: {category}")

        indicators = item.get('affected_indicators')
        if indicators:
            st.markdown("**Affected indicators:**")
            for ind in indicators:
                indicator = ind.get('indicator')
                change = ind.get('expected_change')
                if indicator is not None and change is not None:
                    st.write(f"- {indicator}: {change}")

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
                safe_key = sel_title.replace(" ", "_").replace("-", "_")
                row_c1, row_c2, row_c3, row_c4 = st.columns([0.55, 0.15, 0.15, 0.15])
                with row_c1:
                    st.markdown(f"**{sel_title}**")
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
            categories = [pillar["label"] for pillar in PILLARS]
            pillar_keys = [pillar["key"] for pillar in PILLARS]
            
            # Use calculated scores instead of raw scores
            calculated_scores = calculate_all_pillar_scores(lab_info)
            values = [calculated_scores.get(k, 0) for k in pillar_keys]

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

            

            # Build the subpillars list and an index to map indicator -> row name
            subpillar_rows: List[str] = []
            indicator_to_row: Dict[str, str] = {}
            wefe = lab_info.get('wefe_pillars', {}) or {}
            for pillar_key, pillar_obj in wefe.items():
                indicators_obj = (pillar_obj or {}).get('indicators', {}) or {}
                for category_key, indicator_group in indicators_obj.items():
                    if isinstance(indicator_group, dict):
                        for indicator_key in indicator_group.keys():
                            row_name = f"{pillar_key} / {category_key} / {indicator_key}"
                            subpillar_rows.append(row_name)
                            indicator_to_row[indicator_key] = row_name

            selected_policy_titles: List[str] = st.session_state.get('selected_policies', []) or []

            if not subpillar_rows:
                st.info("No subpillars available for this living lab.")
            elif not selected_policy_titles:
                st.info("No policies selected. Add policies to populate table columns.")
            else:
                # Helper to parse expected_change values (e.g., "+10%", "-3", 5)
                def _parse_change(raw: Any) -> float:
                    if raw is None:
                        return 0
                    if isinstance(raw, (int, float)):
                        return float(raw)
                    try:
                        s = str(raw).strip()
                        # Remove any units except % and sign
                        if s.endswith('%'):
                            return float(s.replace('%', ''))
                        # Fallback: extract leading signed float
                        return float(s)
                    except Exception:
                        return 0

                # Create a zero-filled table with subpillars as rows and applied policies as columns
                # Add % to policy column names to indicate they are percentages
                policy_columns_with_percent = [f"{title} (%)" for title in selected_policy_titles]
                value_table = pd.DataFrame(0, index=subpillar_rows, columns=policy_columns_with_percent)

                # Fill each policy column based on its synergies and trade-offs
                for idx, policy_title in enumerate(selected_policy_titles):
                    policy_column = policy_columns_with_percent[idx]
                    policy_obj = policies_by_title.get(policy_title)
                    if not policy_obj:
                        continue
                    for coll_key in ('synergies', 'trade_offs'):
                        for item in policy_obj.get(coll_key, []) or []:
                            for ind in (item.get('affected_indicators') or []):
                                indicator_key = ind.get('indicator')
                                change_value = _parse_change(ind.get('expected_change'))
                                row_name = indicator_to_row.get(indicator_key)
                                if row_name is not None and row_name in value_table.index:
                                    current_value = value_table.at[row_name, policy_column]
                                    new_value = current_value + change_value
                                    value_table.at[row_name, policy_column] = round(new_value, 2)

                # Add Actual Value column from living lab data
                actual_values = []
                for row_name in subpillar_rows:
                    # Parse the row name to extract pillar, category, and indicator
                    parts = row_name.split(' / ')
                    if len(parts) == 3:
                        pillar_key, category_key, indicator_key = parts
                        try:
                            actual_value = wefe[pillar_key]['indicators'][category_key][indicator_key]
                            actual_values.append(round(actual_value, 2))
                        except (KeyError, TypeError):
                            actual_values.append(0.00)
                    else:
                        actual_values.append(0.00)
                
                value_table.insert(0, 'Actual Value', actual_values)
                # Ensure Actual Value column is properly rounded
                value_table['Actual Value'] = value_table['Actual Value'].round(2)

                # Ensure all policy columns are properly rounded
                for col in policy_columns_with_percent:
                    value_table[col] = value_table[col].round(2)

                # Add Total Improvement column (%) summing across the policy columns and round to 2 decimals
                total_improvements = value_table[policy_columns_with_percent].sum(axis=1)
                value_table['Total Improvement (%)'] = total_improvements.round(2)
                
                # Add Value of Improvement column (concrete values calculated from percentages)
                value_of_improvement = []
                for idx, actual_val in enumerate(actual_values):
                    total_improvement_percent = value_table.iloc[idx]['Total Improvement (%)']
                    concrete_improvement = (actual_val * total_improvement_percent) / 100
                    value_of_improvement.append(round(concrete_improvement, 2))
                
                value_table['Value of Improvement'] = value_of_improvement
                
                # Add Final State column (actual + concrete improvement) and round to 2 decimals
                final_states = value_table['Actual Value'] + value_table['Value of Improvement']
                value_table['Final State'] = final_states.round(2)
                
                # Force all numeric columns to have exactly 2 decimal places by converting to float and rounding
                numeric_columns = ['Actual Value', 'Total Improvement (%)', 'Value of Improvement', 'Final State'] + policy_columns_with_percent
                for col in numeric_columns:
                    if col in value_table.columns:
                        value_table[col] = value_table[col].astype(float).round(2)

                # Style cells with different logic per column type
                def _style_cell(val, row_idx, col_name):
                    try:
                        num = float(val)
                    except Exception:
                        return ''
                    
                    # Don't style the Actual Value column (neutral)
                    if col_name == 'Actual Value':
                        return 'background-color: #f8f9fa; color: #495057'
                    
                    # Style Value of Improvement: green if positive, red if negative
                    if col_name == 'Value of Improvement':
                        if num > 0:
                            return 'background-color: #e8f5e9; color: #1b5e20'
                        elif num < 0:
                            return 'background-color: #ffebee; color: #b71c1c'
                        else:
                            return 'background-color: #f8f9fa; color: #495057'
                    
                    # Style Final State: green if > actual value, red if < actual value
                    if col_name == 'Final State':
                        # We need to get the actual value for this row to compare
                        if row_idx is not None:
                            try:
                                actual_val = float(value_table.iloc[row_idx]['Actual Value'])
                                if num > actual_val:
                                    return 'background-color: #e8f5e9; color: #1b5e20'
                                elif num < actual_val:
                                    return 'background-color: #ffebee; color: #b71c1c'
                                else:
                                    return 'background-color: #f8f9fa; color: #495057'
                            except:
                                return 'background-color: #e3f2fd; color: #1565c0'
                        else:
                            return 'background-color: #e3f2fd; color: #1565c0'
                    
                    # Style policy columns and Total Improvement with green/red based on value
                    if num > 0:
                        return 'background-color: #e8f5e9; color: #1b5e20'
                    if num < 0:
                        return 'background-color: #ffebee; color: #b71c1c'
                    return ''

                # Create format dictionary for all columns
                format_dict = {}
                for col in value_table.columns:
                    if col in ['Actual Value', 'Value of Improvement', 'Final State']:
                        format_dict[col] = "{:.2f}"
                    else:  # All percentage columns
                        format_dict[col] = "{:.2f}%"
                
                # Apply styling with comprehensive formatting
                styled = value_table.style.format(format_dict)
                
                # Apply cell styling with row index for Final State comparison
                def apply_styling(df):
                    styled_df = pd.DataFrame('', index=df.index, columns=df.columns)
                    for row_idx in range(len(df)):
                        for col in df.columns:
                            styled_df.iloc[row_idx, styled_df.columns.get_loc(col)] = _style_cell(df.iloc[row_idx, df.columns.get_loc(col)], row_idx, col)
                    return styled_df
                
                styled = styled.apply(apply_styling, axis=None)
                st.dataframe(styled, use_container_width=True)
        else:
            st.info("WEFE scores not available for the selected living lab.")
			