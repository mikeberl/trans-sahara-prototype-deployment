import streamlit as st
from src.pages.initial_page import get_selected_lab_info
from src.policy.data import get_policy_categories, get_policies_by_category, load_policies
from src.policy.visualization import create_indicators_heatmap, create_improved_indicators_heatmap
from src.policy.ui import (
    render_policy_details, 
    create_and_display_indicator_table, 
    render_selected_policies_section,
    render_display_controls
)


def render_policy_tab():
    """Main function to render the entire policy tab"""
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Policy View - {st.session_state.selected_lab}")
        
        policies = load_policies()
        if not policies:
            st.error("No policies available!")
            return        
        
        categories = get_policy_categories(policies)
        selected_category = st.selectbox(
            "Select Policy Category:",
            categories,
            key="policy_category_select"
        )
        if selected_category:
            category_policies = get_policies_by_category(policies, selected_category)
            if category_policies:                
                for policy in category_policies:
                    render_policy_details(policy)
            else:
                st.info(f"No policies found in the {selected_category} category.")
        else:
            st.info("Please select a policy category to view available policies.")
            
        # Render selected policies section
        selected_policies = st.session_state.get('selected_policies', [])
        render_selected_policies_section(selected_policies)
            
    with col2:
        selected_lab_name = st.session_state.get('selected_lab')
        lab_info = get_selected_lab_info(selected_lab_name) if selected_lab_name else None
        if lab_info and 'wefe_pillars' in lab_info:
            selected_policies = st.session_state.get('selected_policies', [])
            
            # Render display controls
            show_original, show_improved, show_table = render_display_controls(selected_policies)
            
                        # Display original heatmap if selected
            if show_original:
                heatmap_fig = create_indicators_heatmap(lab_info)
                if heatmap_fig:
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                else:
                    st.info("Original heatmap data not available for the selected living lab.")
            
            # Display policy impact table if selected
            if show_table:
                create_and_display_indicator_table(lab_info, selected_policies)
            
            # Display improved heatmap if selected and policies are available
            if show_improved and selected_policies:
                improved_heatmap_fig = create_improved_indicators_heatmap(lab_info, selected_policies)
                if improved_heatmap_fig:
                    st.plotly_chart(improved_heatmap_fig, use_container_width=True)
                else:
                    st.info("Unable to generate improved heatmap.")
        else:
            st.info("WEFE scores not available for the selected living lab.")