import streamlit as st
import pandas as pd
import numpy as np
import random
import json
import os
from src.intervention.models import INTERVENTIONS

def load_living_labs():
    """Load living labs data from JSON file"""
    data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'livinglab.json')
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_regions_from_labs(livinglabs):
    """Extract region names from living labs data"""
    return [lab["name"] for lab in livinglabs]

def initialize_session_state():
    """Initialize all session state variables"""
    if "session_started" not in st.session_state:
        st.session_state.session_started = False
    if "current_selected_lab" not in st.session_state:
        st.session_state.current_selected_lab = None
    if "selected_lab" not in st.session_state:
        st.session_state.selected_lab = "Tunis"  # Default lab
    if "selected_policies" not in st.session_state:
        st.session_state.selected_policies = []
    if "policy_inputs" not in st.session_state:
        st.session_state.policy_inputs = {}
    if "policy_suggestions" not in st.session_state:
        st.session_state.policy_suggestions = {}
    if "active_interventions" not in st.session_state:
        st.session_state.active_interventions = []

def run_policy_simulation():
    """Run the policy simulation and update session state"""
    st.session_state.sim_run = True
    st.session_state.policy_scores = {
        "Water": np.random.randint(0, 100),
        "Energy": np.random.randint(0, 100),
        "Food": np.random.randint(0, 100),
        "Ecosystem": np.random.randint(0, 100)
    }


def get_map_data():
    """Get default map data for Tunisia"""
    return pd.DataFrame({"lat": [34.8], "lon": [10.1]})

# Policy functions moved to src/policy/utils.py
from src.policy.utils import POLICY_DETAILS

def load_pillars():
    """Load WEFE pillars configuration from JSON file"""
    try:
        json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'pillars.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            pillars_data = json.load(f)
        
        # Convert to list format for compatibility
        pillars_list = []
        for pillar_key, pillar_data in pillars_data['wefe_pillars'].items():
            pillars_list.append({
                "key": pillar_data["key"],
                "label": pillar_data["label"],
                "icon": pillar_data["icon"],
                "color": pillar_data["color"]
            })
        return pillars_list
    except FileNotFoundError:
        print(f"Error: Could not find pillars.json at {json_path}")
        # Check if file exists in current directory
        current_dir_path = os.path.join('..', '..', 'data', 'pillars.json')
        if os.path.exists(current_dir_path):
            print(f"Found pillars.json in current directory: {current_dir_path}")
            with open(current_dir_path, 'r', encoding='utf-8') as f:
                pillars_data = json.load(f)
            
            # Convert to list format for compatibility
            pillars_list = []
            for pillar_key, pillar_data in pillars_data['wefe_pillars'].items():
                pillars_list.append({
                    "key": pillar_data["key"],
                    "label": pillar_data["label"],
                    "icon": pillar_data["icon"],
                    "color": pillar_data["color"]
                })
            return pillars_list
        else:
            print(f"Also checked current directory path: {current_dir_path} - not found")
            # Fallback to default configuration
            return [
                {"key": "water", "label": "Water", "icon": "💧", "color": "#3498db"},
                {"key": "energy", "label": "Energy", "icon": "⚡", "color": "#f39c12"},
                {"key": "food", "label": "Food", "icon": "🌾", "color": "#27ae60"},
                {"key": "ecosystems", "label": "Ecosystems", "icon": "🌳", "color": "#16a085"}
            ]
    except Exception as e:
        print(f"Error loading pillars: {e}")
        # Fallback to default configuration
        return [
            {"key": "water", "label": "Water", "icon": "💧", "color": "#3498db"},
            {"key": "energy", "label": "Energy", "icon": "⚡", "color": "#f39c12"},
            {"key": "food", "label": "Food", "icon": "🌾", "color": "#27ae60"},
            {"key": "ecosystems", "label": "Ecosystems", "icon": "🌳", "color": "#16a085"}
        ]

PILLARS = load_pillars()

# load_pillars_definitions() moved to policy_data.py

def normalize_indicator(value, min_val, max_val, invert=False):
    """
    Normalize an indicator value to 0-100 scale
    
    Args:
        value: The actual indicator value
        min_val: Minimum possible value for this indicator
        max_val: Maximum possible value for this indicator
        invert: Whether to invert the score (lower values are better)
    
    Returns:
        Normalized score between 0 and 100
    """
    if value is None or min_val is None or max_val is None:
        return None
    
    if max_val == min_val:
        return 50  # Default middle score if no range
    
    # Normalize to 0-100 scale
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    
    # Clamp to 0-100 range
    normalized = max(0, min(100, normalized))
    
    # Invert if needed (for indicators where lower is better)
    if invert:
        normalized = 100 - normalized
    
    return round(normalized, 1)

def get_indicators_to_invert():
    """
    Define which indicators should be inverted (lower values = better scores)
    """
    return {
        'undernourishment_prevalence',
        'children_wasting_percent', 
        'children_stunted_percent',
        'adult_obesity_prevalence',
        'co2_emissions_per_capita',
        'freshwater_withdrawals_percent',
        'energy_imports_net_percent',
        'endangered_species_count',
        'soil_erosion_rate'
    }

def calculate_pillar_score(pillar_key, lab_data, pillars_definitions):
    """
    Calculate the overall score for a specific pillar using the defined formula
    
    Args:
        pillar_key: The pillar key (water, energy, food, ecosystems)
        lab_data: The living lab data containing indicator values
        pillars_definitions: Complete pillars definitions from pillars.json
    
    Returns:
        Calculated pillar score (0-100)
    """
    if not lab_data or 'wefe_pillars' not in lab_data:
        return None
    
    pillar_data = lab_data['wefe_pillars'].get(pillar_key)
    if not pillar_data or 'indicators' not in pillar_data:
        return None
    
    pillars_def = pillars_definitions.get('wefe_pillars', {})
    pillar_def = pillars_def.get(pillar_key, {})
    
    if not pillar_def:
        return None
    
    # Get all indicator values from the lab data
    all_indicators = {}
    for category_name, category_data in pillar_data['indicators'].items():
        if isinstance(category_data, dict):
            all_indicators.update(category_data)
    
    # Get indicator definitions and calculate normalized scores
    normalized_scores = []
    indicators_to_invert = get_indicators_to_invert()
    
    # Get indicator definitions from pillars.json
    for category_name, category_def in pillar_def.get('categories', {}).items():
        for indicator_name, indicator_def in category_def.get('indicators', {}).items():
            if indicator_name in all_indicators:
                raw_value = all_indicators[indicator_name]
                min_val = indicator_def.get('min_value')
                max_val = indicator_def.get('max_value')
                
                should_invert = indicator_name in indicators_to_invert
                normalized_score = normalize_indicator(raw_value, min_val, max_val, invert=should_invert)
                
                if normalized_score is not None:
                    normalized_scores.append(normalized_score)
    
    # Calculate mean score
    if normalized_scores:
        return round(sum(normalized_scores) / len(normalized_scores), 1)
    else:
        return None

def calculate_all_pillar_scores(lab_data):
    """
    Calculate scores for all pillars for a given living lab
    
    Args:
        lab_data: Complete living lab data
    
    Returns:
        Dictionary with calculated scores for each pillar
    """
    from src.policy.data import load_pillars_definitions
    pillars_definitions = load_pillars_definitions()
    
    scores = {}
    for pillar in PILLARS:
        pillar_key = pillar['key']
        calculated_score = calculate_pillar_score(pillar_key, lab_data, pillars_definitions)
        scores[pillar_key] = calculated_score
    
    return scores

def calculate_overall_wefe_score(lab_data, weights=None):
    """
    Calculate overall WEFE Nexus score using weighted mean of pillar scores
    
    Args:
        lab_data: Complete living lab data
        weights: Dictionary with pillar weights (e.g., {"Water": 3, "Energy": 3, "Food": 3, "Ecosystem": 3})
                If None, uses equal weights of 1 for all pillars
    
    Returns:
        Overall WEFE score (0-100) and breakdown information
    """
    # Get calculated pillar scores
    pillar_scores = calculate_all_pillar_scores(lab_data)
    
    if not pillar_scores:
        return None, {}
    
    # Default weights if not provided
    if weights is None:
        weights = {"Water": 1, "Energy": 1, "Food": 1, "Ecosystem": 1}
    
    # Map weight keys to pillar keys
    weight_mapping = {
        "Water": "water",
        "Energy": "energy", 
        "Food": "food",
        "Ecosystem": "ecosystems"
    }
    
    weighted_sum = 0
    total_weights = 0
    included_pillars = []
    excluded_pillars = []
    
    # Calculate weighted sum
    for weight_key, pillar_key in weight_mapping.items():
        weight = weights.get(weight_key, 0)
        pillar_score = pillar_scores.get(pillar_key)
        
        if weight > 0 and pillar_score is not None:
            weighted_sum += pillar_score * weight
            total_weights += weight
            included_pillars.append({
                "pillar": weight_key,
                "score": pillar_score,
                "weight": weight,
                "weighted_contribution": pillar_score * weight
            })
        else:
            excluded_pillars.append({
                "pillar": weight_key,
                "score": pillar_score,
                "weight": weight,
                "reason": "Weight is 0" if weight == 0 else "Score unavailable"
            })
    
    # Calculate overall score
    if total_weights > 0:
        overall_score = round(weighted_sum / total_weights, 1)
    else:
        overall_score = None
    
    # Breakdown information
    breakdown = {
        "overall_score": overall_score,
        "included_pillars": included_pillars,
        "excluded_pillars": excluded_pillars,
        "total_weights": total_weights,
        "weighted_sum": weighted_sum,
        "number_of_included_pillars": len(included_pillars)
    }
    
    return overall_score, breakdown

def get_indicator_units():
    """
    Extract units for all indicators from pillars.json
    
    Returns:
        Dictionary mapping indicator names to their units
    """
    from src.policy.data import load_pillars_definitions
    pillars_definitions = load_pillars_definitions()
    units_dict = {}
    
    if not pillars_definitions or 'wefe_pillars' not in pillars_definitions:
        return units_dict
    
    # Extract units from all pillars and categories
    for pillar_key, pillar_data in pillars_definitions['wefe_pillars'].items():
        categories = pillar_data.get('categories', {})
        for category_key, category_data in categories.items():
            indicators = category_data.get('indicators', {})
            for indicator_key, indicator_data in indicators.items():
                unit = indicator_data.get('unit', '')
                units_dict[indicator_key] = unit
    
    return units_dict

def format_indicator_with_unit(indicator_name, value, units_dict=None):
    """
    Format an indicator value with its appropriate unit
    
    Args:
        indicator_name: The indicator key name
        value: The indicator value
        units_dict: Dictionary of indicator units (if None, will load from pillars.json)
    
    Returns:
        Formatted string with value and unit
    """
    if value is None:
        return "-"
    
    if units_dict is None:
        units_dict = get_indicator_units()
    
    unit = units_dict.get(indicator_name, "")
    
    # Format based on unit type
    if unit == "percentage":
        return f"{value}%"
    elif unit == "cubic meters per capita per year":
        return f"{value} m³/capita/year"
    elif unit == "millimeters per year":
        return f"{value} mm/year"
    elif unit == "kilowatt hours per capita per year":
        return f"{value} kWh/capita/year"
    elif unit == "metric tons CO2 per capita per year":
        return f"{value} tCO₂/capita/year"
    elif unit == "grams per capita per day":
        return f"{value} g/capita/day"
    elif unit == "kilograms per hectare":
        return f"{value} kg/ha"
    elif unit == "USD per capita per year":
        return f"${value}/capita/year"
    elif unit == "metric tons CO2 equivalent per hectare per year":
        return f"{value} tCO₂eq/ha/year"
    elif unit == "metric tons per hectare per year":
        return f"{value} t/ha/year"
    elif unit == "index (0-1)":
        return f"{value}"
    elif unit == "score (0-100)":
        return f"{value}"
    elif unit == "count":
        return f"{value}"
    elif unit and unit != "":
        # Generic case - just append the unit
        return f"{value} {unit}"
    else:
        # No unit information available
        return f"{value}" 
    