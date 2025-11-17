---
agent: speckit.constitution
---

# Gym Workout Tracking - Streamlit App Development Principles

## Core Development Principles

### 1. Python & Streamlit Best Practices
- Use Streamlit's native components and caching mechanisms (`@st.cache_data`, `@st.cache_resource`)
- Follow PEP 8 style guidelines for Python code
- Use type hints for function parameters and return values
- Keep the main app file clean; modularize code into separate modules for data, UI, and business logic
- Use `st.session_state` for maintaining state across reruns

### 2. Data Management
- Store workout data in a structured format (CSV, SQLite, or JSON)
- Implement data validation before saving (check for required fields, valid date formats, positive numbers)
- Use pandas for data manipulation and analysis
- Create backup mechanisms for user data
- Handle missing or corrupted data gracefully with clear error messages

### 3. User Interface Design
- Keep the interface simple and intuitive for quick workout logging
- Use sidebar for navigation and filters
- Implement clear visual hierarchy (metrics at top, detailed data below)
- Use Streamlit's columns for compact layouts
- Provide immediate feedback for user actions (success messages, warnings)
- Use appropriate input widgets (number_input for weights/reps, date_input for dates, selectbox for exercises)

### 4. Workout Tracking Features
- Support multiple exercise types (strength training, cardio, flexibility)
- Track key metrics: exercise name, sets, reps, weight, duration, date
- Allow easy logging of current workout and viewing of history
- Implement exercise templates for quick entry of common routines
- Support personal records (PRs) tracking and highlighting

### 5. Data Visualization
- Use plotly or altair for interactive charts (compatible with Streamlit)
- Show progress over time with line charts
- Display workout volume trends
- Visualize muscle group distribution
- Keep charts simple and focused on actionable insights

### 6. Performance & Efficiency
- Cache expensive data operations
- Load only necessary data for current view
- Optimize dataframe operations (use vectorized operations)
- Minimize unnecessary reruns with proper state management
- Consider pagination for large workout histories

### 7. Error Handling & Validation
- Validate all user inputs before processing
- Provide helpful error messages that guide users to fix issues
- Use try-except blocks for file operations and data processing
- Implement graceful degradation when features fail
- Log errors for debugging without exposing technical details to users

### 8. Code Organization
```
Structure suggestion:
├── app.py                 # Main Streamlit app
├── data/
│   ├── workouts.csv      # Data storage
│   └── exercises.json    # Exercise library
├── modules/
│   ├── data_manager.py   # Data CRUD operations
│   ├── analytics.py      # Calculations and analysis
│   ├── visualizations.py # Chart generation
│   └── utils.py          # Helper functions
└── requirements.txt      # Dependencies
```

### 9. User Experience
- Default to today's date for quick logging
- Remember user preferences in session state
- Provide keyboard shortcuts where possible (Enter to submit forms)
- Show most recent workouts first
- Allow quick repeat of previous workouts
- Implement search/filter functionality for exercise history

### 10. Deployment Ready
- Include requirements.txt with pinned versions
- Use environment variables for configuration
- Keep sensitive data out of version control
- Test on Streamlit Cloud constraints (memory, processing)
- Provide clear README with setup instructions

## Specific Implementation Guidelines

### For Workout Logging
- Use forms (`st.form`) to prevent reruns on each input change
- Provide autocomplete for exercise names
- Calculate and display total volume per workout
- Allow multiple sets to be added at once

### For Analytics
- Show weekly/monthly summaries
- Calculate and display personal records
- Track consistency (workouts per week)
- Identify trends in performance

### For Data Integrity
- Implement data export functionality
- Validate dates are not in future
- Ensure numeric fields are positive
- Prevent duplicate entries (same exercise, same time)

## Testing & Quality
- Test with empty data state (first-time user experience)
- Test with large datasets (performance with 1000+ workouts)
- Verify all calculations are mathematically correct
- Test edge cases (zero values, very large numbers)
- Ensure responsive behavior on different screen sizes
