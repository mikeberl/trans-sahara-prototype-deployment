import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List
from src.core.wefe_calculations import PILLARS, calculate_all_pillar_scores, normalize_indicator, get_indicators_to_invert
from src.policy.data import load_policies, load_pillars_definitions, infer_policy_pillar, parse_change_value


def create_wefe_radar_plot(lab_info, selected_lab_name):
    """Create a radar plot showing WEFE pillar scores with policy scenario overlay"""
    if not lab_info or 'wefe_pillars' not in lab_info:
        return None
    
    categories = [pillar["label"] for pillar in PILLARS]
    pillar_keys = [pillar["key"] for pillar in PILLARS]
    
    calculated_scores = calculate_all_pillar_scores(lab_info)
    values = [calculated_scores.get(k, 0) for k in pillar_keys]

    # to track impact of policies on indicators
    scenario_values = values.copy()

    selected_titles_for_boost = st.session_state.get('selected_policies', [])
    if selected_titles_for_boost:
        policies_map_local = {p['title']: p for p in load_policies()}

        boosts = {key: 0 for key in pillar_keys}
        for t in selected_titles_for_boost:
            p = policies_map_local.get(t)
            if not p:
                continue
            pillar = infer_policy_pillar(p)
            if pillar in boosts:
                boosts[pillar] += 10

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
    return fig


def create_indicators_heatmap(lab_info):
    """Create a heatmap showing indicators (rows) vs pillars (columns) with normalized values organized in parallel"""
    if not lab_info or 'wefe_pillars' not in lab_info:
        return None
    
    pillars_def = load_pillars_definitions()
    if not pillars_def:
        return None
    
    wefe_pillars_def = pillars_def.get('wefe_pillars', {})
    indicators_to_invert = get_indicators_to_invert()
    
    pillar_columns = ['Water', 'Energy', 'Food', 'Ecosystems']
    pillar_keys = ['water', 'energy', 'food', 'ecosystems']
    
    pillar_indicators = {}
    for pillar_key in pillar_keys:
        pillar_def = wefe_pillars_def.get(pillar_key, {})
        indicators_list = []
        
        for category_name, category_def in pillar_def.get('categories', {}).items():
            for indicator_name, indicator_def in category_def.get('indicators', {}).items():
                indicators_list.append({
                    'key': indicator_name,
                    'name': indicator_def.get('name', indicator_name.replace('_', ' ').title()),
                    'min_value': indicator_def.get('min_value'),
                    'max_value': indicator_def.get('max_value'),
                    'category': category_name
                })
        
        pillar_indicators[pillar_key] = indicators_list
    
    max_indicators = max(len(indicators) for indicators in pillar_indicators.values())
    
    heatmap_matrix = []
    indicator_rows = []
    
    for i in range(max_indicators):
        row_values = []
        indicator_rows.append(f"Indicator {i+1}")
        
        for pillar_key in pillar_keys:
            indicators_list = pillar_indicators[pillar_key]
            
            if i < len(indicators_list):
                indicator_info = indicators_list[i]
                indicator_name = indicator_info['key']
                
                pillar_data = lab_info['wefe_pillars'].get(pillar_key, {})
                indicator_value = None
                
                for category_name, category_data in pillar_data.get('indicators', {}).items():
                    if isinstance(category_data, dict) and indicator_name in category_data:
                        indicator_value = category_data[indicator_name]
                        break
                
                # Normalize the value if found
                if indicator_value is not None:
                    min_val = indicator_info['min_value']
                    max_val = indicator_info['max_value']
                    should_invert = indicator_name in indicators_to_invert
                    
                    normalized_value = normalize_indicator(indicator_value, min_val, max_val, invert=should_invert)
                    if normalized_value is not None:
                        row_values.append(normalized_value)
                    else:
                        row_values.append(np.nan)
                else:
                    row_values.append(np.nan)
            else:
                row_values.append(np.nan)
        
        heatmap_matrix.append(row_values)
    
    heatmap_array = np.array(heatmap_matrix)
    
    hover_text = []
    for i in range(max_indicators):
        hover_row = []
        for pillar_key in pillar_keys:
            indicators_list = pillar_indicators[pillar_key]
            if i < len(indicators_list):
                indicator_name = indicators_list[i]['name']
                hover_row.append(indicator_name)
            else:
                hover_row.append("No indicator")
        hover_text.append(hover_row)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_array,
        x=pillar_columns,
        y=indicator_rows,
        text=hover_text,
        colorscale=[
            [0.0, '#d32f2f'],    # Red for low values
            [0.5, '#ffc107'],    # Yellow for medium values  
            [1.0, '#4caf50']     # Green for high values
        ],
        colorbar=dict(
            title="Normalized Score<br>(0-100)"
        ),
        hoverongaps=False,
        hovertemplate='<b>%{text}</b><br>' +
                      '<b>%{x} Pillar</b><br>' +
                      'Score: %{z:.1f}<br>' +
                      '<extra></extra>',
        zmin=0,
        zmax=100
    ))
    
    fig.update_layout(
        title="WEFE Indicators Evaluation Heatmap",
        xaxis_title="WEFE Pillars",
        yaxis_title="Indicator Position",
        height=max(400, max_indicators * 30), 
        margin=dict(l=100, r=100, t=60, b=50)
    )
    
    return fig


def create_improved_indicators_heatmap(lab_info, selected_policy_titles):
    """Create a heatmap showing indicators (rows) vs pillars (columns) with values after policy improvements"""
    if not lab_info or 'wefe_pillars' not in lab_info:
        return None
    
    if not selected_policy_titles:
        return None
    
    pillars_def = load_pillars_definitions()
    if not pillars_def:
        return None
    
    wefe_pillars_def = pillars_def.get('wefe_pillars', {})
    indicators_to_invert = get_indicators_to_invert()
    
    pillar_columns = ['Water', 'Energy', 'Food', 'Ecosystems']
    pillar_keys = ['water', 'energy', 'food', 'ecosystems']
    
    pillar_indicators = {}
    for pillar_key in pillar_keys:
        pillar_def = wefe_pillars_def.get(pillar_key, {})
        indicators_list = []
        
        for category_name, category_def in pillar_def.get('categories', {}).items():
            for indicator_name, indicator_def in category_def.get('indicators', {}).items():
                indicators_list.append({
                    'key': indicator_name,
                    'name': indicator_def.get('name', indicator_name.replace('_', ' ').title()),
                    'min_value': indicator_def.get('min_value'),
                    'max_value': indicator_def.get('max_value'),
                    'category': category_name
                })
        
        pillar_indicators[pillar_key] = indicators_list
    
    policies_by_title = {p['title']: p for p in load_policies()}
    indicator_improvements = {}
    
    for policy_title in selected_policy_titles:
        policy_obj = policies_by_title.get(policy_title)
        if not policy_obj:
            continue
        for coll_key in ('synergies', 'trade_offs'):
            for item in policy_obj.get(coll_key, []) or []:
                for ind in (item.get('affected_indicators') or []):
                    indicator_key = ind.get('indicator')
                    change_value = parse_change_value(ind.get('expected_change'))
                    if indicator_key:
                        if indicator_key not in indicator_improvements:
                            indicator_improvements[indicator_key] = 0
                        indicator_improvements[indicator_key] += change_value
    
    max_indicators = max(len(indicators) for indicators in pillar_indicators.values())

    heatmap_matrix = []
    indicator_rows = []
    
    for i in range(max_indicators):
        row_values = []
        indicator_rows.append(f"Indicator {i+1}")
        
        for pillar_key in pillar_keys:
            indicators_list = pillar_indicators[pillar_key]
            
            if i < len(indicators_list):
                indicator_info = indicators_list[i]
                indicator_name = indicator_info['key']
                
                pillar_data = lab_info['wefe_pillars'].get(pillar_key, {})
                indicator_value = None
                
                for category_name, category_data in pillar_data.get('indicators', {}).items():
                    if isinstance(category_data, dict) and indicator_name in category_data:
                        indicator_value = category_data[indicator_name]
                        break
                
                # Apply improvements and normalize the value if found
                if indicator_value is not None:
                    improvement_percent = indicator_improvements.get(indicator_name, 0)
                    improved_value = indicator_value + (indicator_value * improvement_percent / 100)
                    
                    min_val = indicator_info['min_value']
                    max_val = indicator_info['max_value']
                    should_invert = indicator_name in indicators_to_invert
                    
                    normalized_value = normalize_indicator(improved_value, min_val, max_val, invert=should_invert)
                    if normalized_value is not None:
                        # Clamp to 0-100 range
                        normalized_value = max(0, min(100, normalized_value))
                        row_values.append(normalized_value)
                    else:
                        row_values.append(np.nan)
                else:
                    row_values.append(np.nan)
            else:
                row_values.append(np.nan)
        
        heatmap_matrix.append(row_values)
    
    heatmap_array = np.array(heatmap_matrix)
    
    # Create custom hover text that shows the actual indicator names
    hover_text = []
    for i in range(max_indicators):
        hover_row = []
        for pillar_key in pillar_keys:
            indicators_list = pillar_indicators[pillar_key]
            if i < len(indicators_list):
                indicator_name = indicators_list[i]['name']
                hover_row.append(indicator_name)
            else:
                hover_row.append("No indicator")
        hover_text.append(hover_row)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_array,
        x=pillar_columns,
        y=indicator_rows,
        text=hover_text,
        colorscale=[
            [0.0, '#d32f2f'],    # Red for low values
            [0.5, '#ffc107'],    # Yellow for medium values  
            [1.0, '#4caf50']     # Green for high values
        ],
        colorbar=dict(
            title="Normalized Score<br>(0-100)<br>After Improvements"
        ),
        hoverongaps=False,
        hovertemplate='<b>%{text}</b><br>' +
                      '<b>%{x} Pillar</b><br>' +
                      'Improved Score: %{z:.1f}<br>' +
                      '<extra></extra>',
        zmin=0,
        zmax=100
    ))
    
    fig.update_layout(
        title="WEFE Indicators Evaluation Heatmap - After Policy Improvements",
        xaxis_title="WEFE Pillars",
        yaxis_title="Indicator Position",
        height=max(400, max_indicators * 30), 
        margin=dict(l=100, r=100, t=60, b=50)
    )
    
    return fig
