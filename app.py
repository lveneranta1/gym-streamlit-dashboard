"""Gym Workout Data Uploader to BigQuery - Streamlit Application."""
import streamlit as st
import pandas as pd
from modules.app_common import (
    init_page_config,
    get_config_loader,
    get_bigquery_uploader,
    render_sidebar,
    check_environment_vars,
    show_env_var_warning
)
from modules.csv_parser import CSVParser
from modules.data_enrichment import DataEnrichment
import traceback

# Initialize page configuration
init_page_config(page_title="Workout Data Uploader", page_icon="🏋️")

# Initialize configuration loader
config_loader = get_config_loader()

# Render sidebar
render_sidebar(config_loader)

# Main title
st.title("🏋️ Workout Data Uploader to BigQuery")
st.markdown("Upload your workout CSV files with automatic muscle group mapping and BigQuery integration.")
st.markdown("---")

# Tabs for different sections
tabs = st.tabs(["📤 Upload Data", "⚙️ CSV Schema", "💪 Exercise Mapping", "☁️ BigQuery Config"])

# TAB 1: Upload Data
with tabs[0]:
    st.header("Upload Workout Data")
    
    if not config_loader:
        st.error("Configuration loader not initialized. Please check your config files.")
        st.stop()
    
    # Check environment variables
    all_valid, missing = check_environment_vars(config_loader)
    if not all_valid:
        show_env_var_warning(missing)
    
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
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                upload_button = st.button("📤 Upload to BigQuery", type="primary", use_container_width=True)
            
            if upload_button:
                if not all_valid:
                    st.error("Cannot upload: Environment variables not configured")
                    st.stop()
                
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

# TAB 2: CSV Schema Configuration
with tabs[1]:
    st.header("⚙️ CSV Schema Configuration")
    
    if config_loader:
        try:
            csv_schema = config_loader.get_csv_schema()
            
            st.subheader("Required Columns")
            req_df = []
            for col_name, config in csv_schema['required_columns'].items():
                req_df.append({
                    'Column': col_name,
                    'Type': config['type'],
                    'Aliases': ', '.join(config.get('aliases', []))
                })
            st.dataframe(pd.DataFrame(req_df), use_container_width=True)
            
            st.subheader("Optional Columns")
            opt_df = []
            for col_name, config in csv_schema.get('optional_columns', {}).items():
                opt_df.append({
                    'Column': col_name,
                    'Type': config['type'],
                    'Default': config.get('default', 'None'),
                    'Aliases': ', '.join(config.get('aliases', []))
                })
            st.dataframe(pd.DataFrame(opt_df), use_container_width=True)
            
            st.subheader("Configuration Settings")
            st.write(f"- **Allow Extra Columns**: {csv_schema.get('allow_extra_columns', True)}")
            st.write(f"- **Strict Mode**: {csv_schema.get('strict_mode', False)}")
            st.write(f"- **Case Sensitive**: {csv_schema.get('case_sensitive', False)}")
            
            with st.expander("View Full Configuration"):
                st.json(csv_schema)
                
        except Exception as e:
            st.error(f"Error loading CSV schema: {e}")

# TAB 3: Exercise Mapping Configuration
with tabs[2]:
    st.header("💪 Exercise Mapping Configuration")
    
    if config_loader:
        try:
            exercise_mapping = config_loader.get_exercise_mapping()
            
            # Muscle group hierarchy
            st.subheader("Muscle Group Hierarchy")
            muscle_groups = exercise_mapping.get('muscle_groups', {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Level 1 Groups**")
                for group in muscle_groups.get('level1', []):
                    st.write(f"- {group}")
            
            with col2:
                st.write("**Level 2 Breakdown**")
                level2 = muscle_groups.get('level2', {})
                for l1, l2_groups in level2.items():
                    st.write(f"**{l1}**: {', '.join(l2_groups)}")
            
            # Exercise count
            exercises = exercise_mapping.get('exercises', [])
            total_exercises = sum(len(ex.get('names', [])) for ex in exercises)
            
            st.metric("Total Mapped Exercises", total_exercises)
            
            # Group exercises by muscle group
            st.subheader("Mapped Exercises")
            
            exercise_dict = {}
            for ex_def in exercises:
                level2 = ex_def['level2']
                if level2 not in exercise_dict:
                    exercise_dict[level2] = []
                exercise_dict[level2].extend(ex_def.get('names', []))
            
            # Display by muscle group
            for muscle, ex_list in sorted(exercise_dict.items()):
                with st.expander(f"{muscle.title()} ({len(ex_list)} exercises)"):
                    for ex in sorted(ex_list):
                        st.write(f"- {ex}")
            
            # Fuzzy rules
            st.subheader("Fuzzy Matching Rules")
            fuzzy_rules = exercise_mapping.get('fuzzy_rules', [])
            rules_df = []
            for rule in fuzzy_rules:
                rules_df.append({
                    'Keyword': rule['keyword'],
                    'Level 1': rule['level1'],
                    'Level 2': rule['level2'],
                    'Excludes': ', '.join(rule.get('exclude', []))
                })
            st.dataframe(pd.DataFrame(rules_df), use_container_width=True)
            
            # Default mapping
            st.subheader("Default Mapping")
            default = exercise_mapping.get('default_mapping', {})
            st.write(f"Unknown exercises are mapped to: **{default.get('level1')} / {default.get('level2')}**")
            
        except Exception as e:
            st.error(f"Error loading exercise mapping: {e}")

# TAB 4: BigQuery Configuration
with tabs[3]:
    st.header("☁️ BigQuery Configuration")
    
    if config_loader:
        try:
            bq_config = config_loader.get_bigquery_config()
            
            # Connection settings
            st.subheader("Connection Settings")
            connection = bq_config.get('connection', {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Project ID**: {connection.get('project_id', 'Not set')}")
                st.write(f"**Dataset ID**: {connection.get('dataset_id', 'Not set')}")
            with col2:
                st.write(f"**Table ID**: {connection.get('table_id', 'Not set')}")
                st.write(f"**Location**: {connection.get('location', 'US')}")
            
            # Test connection button
            if st.button("🔌 Test BigQuery Connection"):
                all_valid, missing = config_loader.validate_env_vars()
                if not all_valid:
                    st.error("Cannot test connection: Environment variables not configured")
                else:
                    try:
                        with st.spinner("Testing connection..."):
                            uploader = BigQueryUploader(bq_config)
                            uploader.initialize_client()
                            test_results = uploader.test_connection()
                        
                        if test_results['can_query']:
                            st.success("✅ Connection successful!")
                            
                            if test_results['table_exists']:
                                st.info(f"Table exists with {test_results.get('table_rows', 0)} rows")
                            else:
                                st.warning("Table does not exist yet (will be created on first upload)")
                        else:
                            st.error("❌ Connection failed")
                            if 'query_error' in test_results:
                                st.error(test_results['query_error'])
                    
                    except Exception as e:
                        st.error(f"❌ Connection test failed: {e}")
            
            # Table schema
            st.subheader("Table Schema")
            schema = bq_config.get('table_schema', [])
            schema_df = []
            for field in schema:
                schema_df.append({
                    'Column': field['name'],
                    'Type': field['type'],
                    'Mode': field.get('mode', 'NULLABLE'),
                    'Description': field.get('description', '')
                })
            st.dataframe(pd.DataFrame(schema_df), use_container_width=True)
            
            # Upload settings
            st.subheader("Upload Settings")
            upload_settings = bq_config.get('upload', {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Write Disposition**: {upload_settings.get('write_disposition', 'WRITE_APPEND')}")
                st.write(f"**Create Disposition**: {upload_settings.get('create_disposition', 'CREATE_IF_NEEDED')}")
            with col2:
                st.write(f"**Batch Size**: {upload_settings.get('batch_size', 1000)}")
                st.write(f"**Timeout**: {upload_settings.get('timeout_seconds', 300)}s")
            
        except Exception as e:
            st.error(f"Error loading BigQuery config: {e}")

# Render sidebar
render_sidebar()
