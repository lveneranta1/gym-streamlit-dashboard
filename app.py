"""Gym Workout Data Uploader to BigQuery - Streamlit Application."""
import streamlit as st
import pandas as pd
from modules.app_common import (
    init_page_config,
    get_config_loader,
    get_bigquery_uploader,
    render_sidebar
)
from modules.csv_parser import CSVParser
from modules.data_enrichment import DataEnrichment
import traceback

# Initialize page configuration
init_page_config(page_title="Workout Data Uploader", page_icon="🏋️")

# Initialize configuration loader
config_loader = get_config_loader()

# Render the sidebar (which now includes the connection test button)
render_sidebar(config_loader)

# Main title
st.title("🏋️ Workout Data Uploader to BigQuery")
st.markdown("Upload your workout CSV files with automatic muscle group mapping and BigQuery integration.")
st.markdown("---")

# Uploader Section
st.header("Upload Workout Data")

if not config_loader:
    st.error("Configuration loader not initialized. Please check your config files.")
    st.stop()

# File uploader
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="Upload your workout data CSV file. Required columns: date, workout_name, exercise_name, weight_kg, reps"
)

if uploaded_file is not None:
    try:
        # Show file info
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Step 1: Parse CSV
        with st.spinner("Parsing CSV file..."):
            csv_schema = config_loader.get_csv_schema()
            parser = CSVParser(csv_schema)
            df = parser.parse_csv(uploaded_file)
        
        # Show validation results
        errors = parser.get_validation_errors()
        warnings = parser.get_warnings()
        summary = parser.get_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Validation Errors", len(errors))
        with col3:
            st.metric("Warnings", len(warnings))
        
        # Display errors
        if errors:
            st.error("❌ Validation Errors Found")
            with st.expander("Show errors", expanded=True):
                for error in errors:
                    st.write(f"- {error}")
            st.stop()
        
        # Display warnings
        if warnings:
            st.warning("⚠️ Validation Warnings")
            with st.expander("Show warnings"):
                for warning in warnings:
                    st.write(f"- {warning}")
        
        # Show column mappings
        if summary['column_mappings']:
            with st.expander("Column Mappings"):
                st.write("CSV columns mapped to standard names:")
                for std_name, orig_name in summary['column_mappings'].items():
                    st.write(f"- `{orig_name}` → `{std_name}`")
        
        # Step 2: Upload to BigQuery
        st.subheader("☁️ Upload to BigQuery")
        
        st.info(f"Ready to upload {len(df)} rows to BigQuery")
        
        if st.button("📤 Upload to BigQuery", type="primary", use_container_width=True):
            
            try:
                # Get or create BigQuery uploader
                uploader = get_bigquery_uploader(config_loader)
                
                if not uploader:
                    st.error("Failed to initialize BigQuery uploader. Check your configuration.")
                    st.stop()
                
                st.success("✅ BigQuery client initialized")
                
                with st.spinner("Creating table if needed..."):
                    uploader.create_table_if_not_exists()
                
                st.success("✅ Table ready")
                
                with st.spinner("Uploading data to BigQuery..."):
                    result = uploader.upload_dataframe(df)
                
                if result['success']:
                    st.success(f"🎉 Successfully uploaded {result['rows_uploaded']} rows!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows Uploaded", result['rows_uploaded'])
                    with col2:
                        st.metric("Duration", f"{result['duration_seconds']:.2f}s")
                    with col3:
                        st.metric("Table", result['table'].split('.')[-1])
                    
                else:
                    st.error(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Error during upload: {e}")
                with st.expander("Show error details"):
                    st.code(traceback.format_exc())
    
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
        with st.expander("Show error details"):
            st.code(traceback.format_exc())
