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
        
        # Step 2: Preview parsed data
        st.subheader("📊 Parsed Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Step 3: Data enrichment
        st.subheader("💪 Muscle Group Mapping")
        
        with st.spinner("Mapping exercises to muscle groups..."):
            exercise_mapping = config_loader.get_exercise_mapping()
            enrichment = DataEnrichment(exercise_mapping)
            df_enriched = enrichment.enrich_dataframe(df)
        
        # Show mapping summary
        mapping_summary = enrichment.get_mapping_summary(df_enriched)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Unique Exercises", mapping_summary['unique_exercises'])
        with col2:
            st.metric("Unmapped Exercises", mapping_summary['unmapped_count'])
        
        # Show unmapped exercises
        unmapped = enrichment.get_unmapped_exercises()
        if unmapped:
            st.warning(f"⚠️ {len(unmapped)} exercises could not be mapped exactly")
            with st.expander("Show unmapped exercises"):
                for ex in unmapped:
                    suggestions = enrichment.suggest_mapping(ex)
                    st.write(f"**{ex}**")
                    if suggestions:
                        st.write(f"  → Applied: {suggestions[0][0]} / {suggestions[0][1]}")
        
        # Show enriched data preview
        st.subheader("📈 Enriched Data Preview")
        preview_cols = ['exercise_name', 'weight_kg', 'reps', 'muscle_group_level1', 'muscle_group_level2']
        available_cols = [col for col in preview_cols if col in df_enriched.columns]
        st.dataframe(df_enriched[available_cols].head(10), use_container_width=True)
        
        # Show muscle group distribution
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Level 1 Distribution**")
            st.bar_chart(pd.Series(mapping_summary['level1_distribution']))
        with col2:
            st.write("**Level 2 Distribution**")
            st.bar_chart(pd.Series(mapping_summary['level2_distribution']).head(10))
        
        # Step 4: Upload to BigQuery
        st.subheader("☁️ Upload to BigQuery")
        
        st.info(f"Ready to upload {len(df_enriched)} rows to BigQuery")
        
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
                    result = uploader.upload_dataframe(df_enriched)
                
                if result['success']:
                    st.success(f"🎉 Successfully uploaded {result['rows_uploaded']} rows!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows Uploaded", result['rows_uploaded'])
                    with col2:
                        st.metric("Duration", f"{result['duration_seconds']:.2f}s")
                    with col3:
                        st.metric("Table", result['table'].split('.')[-1])
                    
                    # Upload exercise mapping table
                    with st.spinner("Uploading exercise mapping table..."):
                        mapping_result = uploader.upload_exercise_mapping(exercise_mapping)
                    
                    if mapping_result['success']:
                        st.success(f"✅ Exercise mapping table updated ({mapping_result['rows_uploaded']} mappings)")
                    else:
                        st.warning(f"⚠️ Exercise mapping upload failed (non-critical): {mapping_result.get('error', 'Unknown error')}")
                    
                    # Refresh BigQuery views
                    with st.spinner("Refreshing analytical views..."):
                        from modules.bigquery_views import BigQueryViewManager
                        
                        bq_config = config_loader.get_bigquery_config()
                        connection_config = bq_config.get('connection', {})
                        project_id = connection_config.get('project_id')
                        dataset_id = connection_config.get('dataset_id')
                        
                        view_manager = BigQueryViewManager(uploader.client, project_id, dataset_id)
                        
                        views_config = bq_config.get('views', {})
                        if views_config.get('enabled', False) and views_config.get('refresh_on_upload', True):
                            view_definitions = views_config.get('view_definitions', [])
                            view_results = view_manager.refresh_all_views(view_definitions)
                            
                            successful_views = sum(1 for status in view_results.values() if status)
                            total_views = len(view_results)
                            
                            if successful_views == total_views:
                                st.success(f"✅ All {total_views} analytical views refreshed")
                            else:
                                st.warning(f"⚠️ Views refreshed: {successful_views}/{total_views} successful")
                    
                    st.balloons()
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
