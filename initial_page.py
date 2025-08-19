import base64
import streamlit as st
import folium
from folium import plugins
from utils import load_living_labs, get_regions_from_labs

def create_living_labs_map(selected_lab=None):
    """Create an interactive map showing all living lab areas as squares"""
    livinglabs = load_living_labs()
    
    # Map settings
    center_lat = 18.0
    center_lon = 10.0
    zoom_level = 4.5   
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles='OpenStreetMap'
    )
    
    # Add each living lab area as a rectangle
    for lab in livinglabs:
        upper_left = lab['geolocation_area']['upper_left']
        lower_right = lab['geolocation_area']['lower_right']
        
        rectangle_coords = [
            [upper_left['lat'], upper_left['lon']],
            [upper_left['lat'], lower_right['lon']],
            [lower_right['lat'], lower_right['lon']],
            [lower_right['lat'], upper_left['lon']],
            [upper_left['lat'], upper_left['lon']]
        ]
        if selected_lab and lab['name'] == selected_lab:
            color = 'blue'  # Selected lab
            weight = 3
        else:
            color = 'red'   # Unselected labs
            weight = 2
        
        folium.Polygon(
            locations=rectangle_coords,
            color=color,
            weight=weight,
            fill=True,
            fillColor=color,
            fillOpacity=0.3,
            popup=f"<b>{lab['name']}</b><br>Country: {lab['country']}<br>Climate: {lab['climate_type']}"
        ).add_to(m)
        
    return m

def get_selected_lab_info(selected_lab_name):
    """Get detailed information about the selected living lab"""
    if not selected_lab_name:
        return None
    
    livinglabs = load_living_labs()
    for lab in livinglabs:
        if lab['name'] == selected_lab_name:
            return lab
    return None

def render_sidebar_welcome_page():
    """Render the initial setup page with sidebar configuration"""
    st.sidebar.header("1. Select Living Lab and Impact Weights")

    livinglabs = load_living_labs()
    regions = get_regions_from_labs(livinglabs)
    
    selected_lab = st.sidebar.selectbox("Select a Living Lab", regions, key="select_lab")
    st.session_state.current_selected_lab = selected_lab
    st.sidebar.markdown("---")
    
    # WEFE weights settings
    with st.sidebar.expander("WEFE weights settings", expanded=False):
        water_w = st.slider("Water Availability", 0, 5, 3, key="water_weight")
        energy_w = st.slider("Energy Demand", 0, 5, 3, key="energy_weight")
        food_w = st.slider("Agricultural Production", 0, 5, 3, key="food_weight")
        eco_w = st.slider("Ecosystem Health", 0, 5, 3, key="eco_weight")

    # Session parameters settings 
    with st.sidebar.expander("Session parameters settings", expanded=False):
        budget = st.number_input("Budget (Million USD)", 0, 1000, 10, 1, key="budget")
        time_range = st.number_input("Simulation Year", 2030, 2100, 2030, 5, key="sim_year")
        time_interval = st.number_input("Interval (years)", 1, 20, 5, 1, key="interval")

    # Scenario definition settings
    with st.sidebar.expander("Scenario definition", expanded=False):
        st.markdown("Here it's possible to pick a specific scenario if needed for the analysis")
        scenario_options = ["Baseline", "Climate Change", "Population Growth", "Technology Adoption"]
        selected_scenario = st.selectbox("Select Scenario", scenario_options, key="scenario_select")

    if st.sidebar.button("Start Session", key="start_session"):
        st.session_state.session_started = True
        st.session_state.selected_lab = selected_lab
        st.session_state.policy_weights = {
            "Water": water_w, "Energy": energy_w, "Food": food_w, "Ecosystem": eco_w
        }
        st.rerun()

def render_wefe_pillars_view(lab_info):
    """Render a card-style view for all 4 WEFE pillars of the selected living lab."""
    if not lab_info or 'wefe_pillars' not in lab_info:
        st.info("No WEFE data available for this living lab.")
        return

    pillars = [
        {
            "key": "water",
            "label": "Water",
            "icon": "💧",
            "color": "#3498db"
        },
        {
            "key": "energy",
            "label": "Energy",
            "icon": "⚡",
            "color": "#f39c12"
        },
        {
            "key": "food",
            "label": "Food",
            "icon": "🌾",
            "color": "#27ae60"
        },
        {
            "key": "ecosystems",
            "label": "Ecosystems",
            "icon": "🌳",
            "color": "#16a085"
        }
    ]

    cols = st.columns(4)
    for i, pillar in enumerate(pillars):
        data = lab_info['wefe_pillars'].get(pillar["key"], {})
        
        with cols[i]:
            with st.container(border=True):
                internal_col1, internal_col2 = st.columns([1, 2])
                with internal_col1:
                    st.markdown(f"<div style='display:flex;align-items:center;'><span style='font-size:2rem;'>{pillar['icon']}</span> <span style='font-size:2rem;font-weight:700;margin-left:0.5em;color:{pillar['color']}'>{pillar['label']}</span></div>", unsafe_allow_html=True)
                with internal_col2:
                    st.markdown(
                        f"""
                        <div style='display: flex; justify-content: flex-end; align-items: center;'>
                            <div>
                                <span style='font-size: 0.9rem; color: #888;'>Score</span><br>
                                <span style='font-size: 1.5rem; font-weight: bold;'>{data.get("score", "-")}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                indicators = data.get("indicators", {})
                for subpillar, subdata in indicators.items():
                    st.divider()
                    st.markdown(f"**{subpillar.capitalize()}**")
                    for ind_name, ind_value in subdata.items():
                        st.write(f"{ind_name.replace('_', ' ').capitalize()}: {ind_value}")

def render_welcome_page():
    """Render the welcome page when session hasn't started"""
    
    selected_lab = st.session_state.get('current_selected_lab', None)
    
    col1, col2 = st.columns([3, 1])    
    
    with col1:
        map_obj = create_living_labs_map(selected_lab)
        st.components.v1.html(map_obj._repr_html_(), height=800, width=None)
    with col2:
        if selected_lab:
            lab_info = get_selected_lab_info(selected_lab)
            if lab_info:
                st.subheader(f"**{lab_info['name']}**")
                st.markdown(f"**Country:** {lab_info['country']}")
                st.markdown(f"**Climate Type:** {lab_info['climate_type']}")
                st.markdown(f"**Description:** {lab_info['description']}")
                
                if 'challenges' in lab_info and lab_info['challenges']:
                    with st.expander("⚠️ Main Challenges", expanded=False):
                        st.markdown("**Main challenges of the living lab:**")
                        for i, challenge in enumerate(lab_info['challenges'], 1):
                            st.markdown(f"- {challenge}")
                
                with st.expander("📞 Contact Information", expanded=False):
                    for contact in lab_info['contacts']:
                        st.markdown(f"- **{contact['name']}**")
                        st.markdown(f"  {contact['institution']}")
                        st.markdown(f"  📧 {contact['email']}")
                        st.markdown(f"  📞 {contact['phone']}")
                        st.markdown("")                
            else:
                lab_info = None
        else:
            st.subheader("Living Lab Information")
            st.info("Select a living lab from the sidebar to view its details.")
            lab_info = None
            
    render_wefe_pillars_view(lab_info) 
    
    
    
