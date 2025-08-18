# WEFE Nexus DSS: Policy & Intervention Simulator

A modular Streamlit application for simulating water-energy-food-ecosystem (WEFE) nexus policies and interventions.

## Project Structure

The application has been refactored into a modular structure for better maintainability:

```
├── app.py                 # Main entry point
├── utils.py              # Shared utilities and functions
├── initial_page.py       # Initial setup and configuration
├── policy_tab.py         # Policy view functionality
├── intervention_tab.py   # Intervention view functionality
├── policies.py           # Policy data (existing)
├── interventions.py      # Intervention data (existing)
├── policies.json         # Policy details (existing)
└── livinglab.json       # Living lab data (existing)
```

## File Descriptions

### `app.py`
- **Main entry point** for the Streamlit application
- Handles page configuration and session state initialization
- Coordinates between different components
- Manages the tab structure

### `utils.py`
- **Shared utilities** and helper functions
- Data loading functions (`load_living_labs`, `get_regions_from_labs`)
- Session state management (`initialize_session_state`)
- Simulation functions (`run_policy_simulation`)
- Data processing functions (`calculate_overall_score`, `get_detailed_scores`)

### `initial_page.py`
- **Initial setup interface** before the main session starts
- Sidebar configuration for living lab selection
- Indicator weight settings
- Budget and time range configuration
- Welcome page when session hasn't started
- **Interactive map** showing all living lab areas as colored squares
  - Red squares for unselected labs
  - Blue square for the selected lab
  - Popup information for each lab area

### `policy_tab.py`
- **Policy management functionality**
- Policy selection and addition interface
- Detailed policy configuration and display
- Simulation execution
- Results visualization with detailed scores

### `intervention_tab.py`
- **Intervention management functionality**
- Intervention suggestion display
- Add/remove/replace intervention controls
- Progress tracking
- Map visualization

## Benefits of This Structure

1. **Modularity**: Each component has a single responsibility
2. **Maintainability**: Easier to modify individual features
3. **Reusability**: Functions can be reused across components
4. **Testability**: Individual components can be tested separately
5. **Clarity**: Clear separation of concerns

## Dependencies

The application requires the following Python packages:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install streamlit pandas numpy folium
```

## Running the Application

To run the application, use:

```bash
streamlit run app.py
```

## Migration from Original Structure

The original `prototype.py` file has been split into:
- Main app logic → `app.py`
- Initial setup → `initial_page.py`
- Policy functionality → `policy_tab.py`
- Intervention functionality → `intervention_tab.py`
- Shared functions → `utils.py`

All functionality remains the same, but the code is now more organized and maintainable. 