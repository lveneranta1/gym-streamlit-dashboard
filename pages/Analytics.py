"""Workout Analytics Dashboard - Streamlit Page."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.app_common import (
    init_page_config,
    get_config_loader,
    get_bigquery_uploader,
    render_sidebar,
    check_environment_vars,
    show_env_var_warning
)
from modules.analytics import WorkoutAnalytics

# Initialize page configuration
init_page_config(page_title="Workout Analytics", page_icon="📊")

# Initialize configuration loader
config_loader = get_config_loader()

# Render sidebar
render_sidebar(config_loader)

# Main title
st.title("📊 Workout Analytics Dashboard")
st.markdown("Analyze your workout data with interactive visualizations and insights.")
st.markdown("---")

if not config_loader:
    st.error("Configuration loader not initialized. Please check your config files.")
    st.stop()

# Check environment variables
all_valid, missing = check_environment_vars(config_loader)
if not all_valid:
    show_env_var_warning(missing)
    st.stop()

# Initialize BigQuery uploader
uploader = get_bigquery_uploader(config_loader)

if not uploader:
    st.error("⚠️ BigQuery connection not available. Please check your configuration.")
    st.stop()

# Initialize analytics module
bq_config = config_loader.get_bigquery_config()
connection_config = bq_config.get('connection', {})
project_id = connection_config.get('project_id')
dataset_id = connection_config.get('dataset_id')

try:
    analytics = WorkoutAnalytics(uploader.client, project_id, dataset_id)
    
    # Check if table has data
    if not analytics.check_table_exists():
        st.warning("⚠️ No workout data found in BigQuery.")
        st.info("👉 Upload some workout data first using the main Upload Data page.")
        st.stop()
    
    st.success("✅ Analytics module initialized")
except Exception as e:
    st.error(f"Failed to initialize analytics: {e}")
    st.stop()

# Create tabs for different analytics views
tabs = st.tabs([
    "📈 Overview", 
    "💪 Muscle Groups", 
    "🏋️ Exercises", 
    "📊 Performance"
])

# TAB 1: Overview
with tabs[0]:
    st.header("Workout Overview")
    
    try:
        # Get overview metrics
        with st.spinner("Loading overview metrics..."):
            overview = analytics.get_workout_overview()
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Workouts", overview.get('total_workouts', 0))
        with col2:
            st.metric("Total Exercises", overview.get('total_exercises', 0))
        with col3:
            st.metric("Total Volume (kg)", f"{overview.get('total_volume_kg', 0):,.0f}")
        with col4:
            st.metric("Unique Exercises", overview.get('unique_exercises', 0))
        
        # Workout frequency over time
        st.subheader("Workout Frequency Over Time")
        frequency_data = analytics.get_workout_frequency_by_date()
        
        if not frequency_data.empty:
            fig = px.line(
                frequency_data,
                x='date',
                y='workout_count',
                title='Daily Workout Count',
                labels={'date': 'Date', 'workout_count': 'Number of Workouts'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No workout frequency data available yet.")
    
    except Exception as e:
        st.error(f"Error loading overview: {e}")
        with st.expander("Show error details"):
            import traceback
            st.code(traceback.format_exc())

# TAB 2: Muscle Groups
with tabs[1]:
    st.header("Muscle Group Analysis")
    
    try:
        # Muscle group distribution
        st.subheader("Workout Distribution by Muscle Group")
        
        with st.spinner("Loading muscle group data..."):
            muscle_data = analytics.get_muscle_group_distribution()
        
        if not muscle_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Level 1 (Primary Groups)**")
                level1_data = muscle_data[muscle_data['level'] == 'level1']
                if not level1_data.empty:
                    fig = px.pie(
                        level1_data,
                        values='exercise_count',
                        names='muscle_group',
                        title='Primary Muscle Groups'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No level 1 muscle group data available.")
            
            with col2:
                st.write("**Level 2 (Specific Muscles)**")
                level2_data = muscle_data[muscle_data['level'] == 'level2'].head(10)
                if not level2_data.empty:
                    fig = px.bar(
                        level2_data,
                        x='exercise_count',
                        y='muscle_group',
                        orientation='h',
                        title='Top 10 Specific Muscle Groups'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No level 2 muscle group data available.")
        else:
            st.info("No muscle group data available yet.")
    
    except Exception as e:
        st.error(f"Error loading muscle group analysis: {e}")
        with st.expander("Show error details"):
            import traceback
            st.code(traceback.format_exc())

# TAB 3: Exercises
with tabs[2]:
    st.header("Exercise Analysis")
    
    try:
        # Most performed exercises
        st.subheader("Most Performed Exercises")
        
        with st.spinner("Loading exercise data..."):
            exercise_data = analytics.get_top_exercises(limit=20)
        
        if not exercise_data.empty:
            fig = px.bar(
                exercise_data,
                x='total_sets',
                y='exercise_name',
                orientation='h',
                title='Top 20 Exercises by Total Sets',
                labels={'total_sets': 'Total Sets', 'exercise_name': 'Exercise'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data table
            with st.expander("View detailed data"):
                st.dataframe(exercise_data, use_container_width=True)
        else:
            st.info("No exercise data available yet.")
    
    except Exception as e:
        st.error(f"Error loading exercise analysis: {e}")
        with st.expander("Show error details"):
            import traceback
            st.code(traceback.format_exc())

# TAB 4: Performance
with tabs[3]:
    st.header("Performance Metrics")
    
    try:
        # Exercise selector
        exercises = analytics.get_all_exercises()
        
        if not exercises.empty and len(exercises) > 0:
            selected_exercise = st.selectbox(
                "Select an exercise to analyze:",
                exercises['exercise_name'].unique()
            )
            
            if selected_exercise:
                st.subheader(f"Performance Tracking: {selected_exercise}")
                
                with st.spinner("Loading performance data..."):
                    performance_data = analytics.get_exercise_performance(selected_exercise)
                
                if not performance_data.empty:
                    # Weight progression
                    fig = px.line(
                        performance_data,
                        x='date',
                        y='max_weight',
                        title=f'{selected_exercise} - Weight Progression',
                        labels={'date': 'Date', 'max_weight': 'Max Weight (kg)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Volume over time
                    fig = px.line(
                        performance_data,
                        x='date',
                        y='total_volume',
                        title=f'{selected_exercise} - Volume Over Time',
                        labels={'date': 'Date', 'total_volume': 'Total Volume (kg)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show data table
                    with st.expander("View detailed data"):
                        st.dataframe(performance_data, use_container_width=True)
                else:
                    st.info(f"No performance data available for {selected_exercise}")
        else:
            st.info("No exercises found in database. Upload some workout data first!")
    
    except Exception as e:
        st.error(f"Error loading performance metrics: {e}")
        with st.expander("Show error details"):
            import traceback
            st.code(traceback.format_exc())