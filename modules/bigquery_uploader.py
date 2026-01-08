"""BigQuery uploader module for uploading workout data to Google BigQuery."""
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import Dict, Any, Optional
from datetime import datetime
import os


class BigQueryUploader:
    """Upload workout data to Google BigQuery."""
    
    def __init__(self, bq_config: Dict[str, Any]):
        """Initialize BigQuery uploader with configuration.
        
        Args:
            bq_config: Dictionary containing BigQuery configuration
        """
        self.config = bq_config
        self.client: Optional[bigquery.Client] = None
        self.upload_stats: Dict[str, Any] = {}
        
    def initialize_client(self, credentials=None) -> bool:
        """Initialize BigQuery client with credentials.
        
        Args:
            credentials: Optional Google Auth credentials object.
            
        Returns:
            True if initialization successful, False otherwise
            
        Raises:
            Exception: If credentials or configuration are invalid
        """
        connection_config = self.config.get('connection', {})
        project_id = connection_config.get('project_id')
        location = connection_config.get('location', 'US')

        # Project ID can be overridden by credentials
        if credentials and hasattr(credentials, 'project_id'):
            project_id = credentials.project_id

        if not project_id:
            raise ValueError("Missing GCP_PROJECT_ID in configuration or credentials.")
        
        try:
            # The BigQuery client will use 'credentials' if provided.
            # If 'credentials' is None, it falls back to Application Default Credentials.
            self.client = bigquery.Client(
                project=project_id,
                credentials=credentials,
                location=location
            )
            
            # Test connection with a simple query
            self.client.query("SELECT 1").result()
            return True
            
        except Exception as e:
            raise Exception(f"Failed to initialize BigQuery client: {e}")
    
    def create_table_if_not_exists(self) -> bool:
        """Create BigQuery table if it doesn't exist.
        
        Returns:
            True if table exists or was created successfully
            
        Raises:
            Exception: If table creation fails
        """
        if not self.client:
            raise Exception("BigQuery client not initialized. Call initialize_client() first.")
        
        connection_config = self.config.get('connection', {})
        project_id = connection_config.get('project_id')
        dataset_id = connection_config.get('dataset_id')
        table_id = connection_config.get('table_id')
        
        if not all([project_id, dataset_id, table_id]):
            raise ValueError("Missing BigQuery table configuration")
        
        # Full table reference
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        
        try:
            # Check if table exists
            self.client.get_table(table_ref)
            return True
        except Exception:
            # Table doesn't exist, create it
            pass
        
        # Build schema from configuration
        schema_config = self.config.get('table_schema', [])
        schema = []
        
        for field in schema_config:
            field_type = field['type']
            field_mode = field.get('mode', 'NULLABLE')
            field_name = field['name']
            field_desc = field.get('description', '')
            
            schema.append(
                bigquery.SchemaField(
                    field_name,
                    field_type,
                    mode=field_mode,
                    description=field_desc
                )
            )
        
        # Create table
        table = bigquery.Table(table_ref, schema=schema)
        
        try:
            table = self.client.create_table(table)
            return True
        except Exception as e:
            raise Exception(f"Failed to create BigQuery table: {e}")
    
    def _add_metadata_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add metadata columns to dataframe before upload.
        
        Args:
            df: DataFrame to add metadata to
            
        Returns:
            DataFrame with metadata columns
        """
        df = df.copy()
        
        # Add upload timestamp
        df['upload_timestamp'] = pd.Timestamp.now()
        
        # Add data source
        df['data_source'] = 'csv_upload'
        
        return df
    
    def _validate_schema(self, df: pd.DataFrame) -> bool:
        """Validate that DataFrame matches BigQuery schema.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if schema matches
            
        Raises:
            ValueError: If schema doesn't match
        """
        schema_config = self.config.get('table_schema', [])
        required_fields = [field['name'] for field in schema_config if field.get('mode') == 'REQUIRED']
        
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            raise ValueError(f"DataFrame missing required fields: {', '.join(missing_fields)}")
        
        return True
    
    def upload_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Upload dataframe to BigQuery.
        
        Args:
            df: DataFrame to upload
            
        Returns:
            Dictionary with upload statistics
            
        Raises:
            Exception: If upload fails
        """
        if not self.client:
            raise Exception("BigQuery client not initialized. Call initialize_client() first.")
        
        if df.empty:
            return {
                'success': False,
                'error': 'DataFrame is empty',
                'rows_uploaded': 0
            }
        
        start_time = datetime.now()
        
        # Add metadata columns
        df = self._add_metadata_columns(df)
        
        # Validate schema
        try:
            self._validate_schema(df)
        except ValueError as e:
            return {
                'success': False,
                'error': str(e),
                'rows_uploaded': 0
            }
        
        # Get table reference
        connection_config = self.config.get('connection', {})
        project_id = connection_config.get('project_id')
        dataset_id = connection_config.get('dataset_id')
        table_id = connection_config.get('table_id')
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        
        # Configure job
        upload_config = self.config.get('upload', {})
        job_config = bigquery.LoadJobConfig(
            write_disposition=upload_config.get('write_disposition', 'WRITE_APPEND'),
            create_disposition=upload_config.get('create_disposition', 'CREATE_IF_NEEDED')
        )
        
        try:
            # Upload dataframe
            job = self.client.load_table_from_dataframe(
                df,
                table_ref,
                job_config=job_config
            )
            
            # Wait for job to complete
            timeout = upload_config.get('timeout_seconds', 300)
            job.result(timeout=timeout)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.upload_stats = {
                'success': True,
                'rows_uploaded': len(df),
                'duration_seconds': duration,
                'table': table_ref,
                'timestamp': end_time.isoformat()
            }
            
            return self.upload_stats
            
        except Exception as e:
            self.upload_stats = {
                'success': False,
                'error': str(e),
                'rows_uploaded': 0
            }
            return self.upload_stats
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """Get statistics from last upload.
        
        Returns:
            Dictionary with upload statistics
        """
        return self.upload_stats
    
    def test_connection(self) -> Dict[str, Any]:
        """Test BigQuery connection and configuration.
        
        Returns:
            Dictionary with connection test results
        """
        results = {
            'client_initialized': self.client is not None,
            'can_query': False,
            'table_exists': False,
            'table_accessible': False
        }
        
        if not self.client:
            results['error'] = 'Client not initialized'
            return results
        
        # Test query capability
        try:
            self.client.query("SELECT 1").result()
            results['can_query'] = True
        except Exception as e:
            results['query_error'] = str(e)
        
        # Test table access
        connection_config = self.config.get('connection', {})
        project_id = connection_config.get('project_id')
        dataset_id = connection_config.get('dataset_id')
        table_id = connection_config.get('table_id')
        
        if all([project_id, dataset_id, table_id]):
            table_ref = f"{project_id}.{dataset_id}.{table_id}"
            
            try:
                table = self.client.get_table(table_ref)
                results['table_exists'] = True
                results['table_accessible'] = True
                results['table_rows'] = table.num_rows
            except Exception as e:
                results['table_error'] = str(e)
        
        return results
    
    def _parse_exercise_mapping(self, mapping_config: Dict[str, Any]) -> pd.DataFrame:
        """Parse exercise mapping YAML config into DataFrame.
        
        Args:
            mapping_config: Exercise mapping configuration from YAML
            
        Returns:
            DataFrame with exercise mapping data
        """
        exercises = mapping_config.get('exercises', [])
        
        rows = []
        for exercise_group in exercises:
            names = exercise_group.get('names', [])
            level1 = exercise_group.get('level1', 'unknown')
            level2 = exercise_group.get('level2', 'unknown')
            is_compound = exercise_group.get('compound', False)
            
            # Create a row for each exercise name variant
            for name in names:
                rows.append({
                    'exercise_name': name.strip(),
                    'muscle_group_level1': level1,
                    'muscle_group_level2': level2,
                    'is_compound': is_compound,
                    'mapping_source': 'config',
                    'last_updated': pd.Timestamp.now()
                })
        
        return pd.DataFrame(rows)
    
    def upload_exercise_mapping(self, mapping_config: Dict[str, Any]) -> Dict[str, Any]:
        """Upload exercise-to-muscle mapping to BigQuery.
        
        Args:
            mapping_config: Exercise mapping configuration from YAML
            
        Returns:
            Dictionary with upload statistics
        """
        if not self.client:
            raise Exception("BigQuery client not initialized. Call initialize_client() first.")
        
        try:
            # Parse mapping config into DataFrame
            mapping_df = self._parse_exercise_mapping(mapping_config)
            
            if mapping_df.empty:
                return {
                    'success': False,
                    'error': 'No exercise mappings found in configuration',
                    'rows_uploaded': 0
                }
            
            # Get connection config
            connection_config = self.config.get('connection', {})
            project_id = connection_config.get('project_id')
            dataset_id = connection_config.get('dataset_id')
            
            # Define table schema
            schema = [
                bigquery.SchemaField("exercise_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("muscle_group_level1", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("muscle_group_level2", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("is_compound", "BOOLEAN"),
                bigquery.SchemaField("mapping_source", "STRING"),
                bigquery.SchemaField("last_updated", "TIMESTAMP")
            ]
            
            # Upload with WRITE_TRUNCATE (replace entire table)
            table_id = f"{project_id}.{dataset_id}.exercise_muscle_mapping"
            job_config = bigquery.LoadJobConfig(
                schema=schema,
                write_disposition="WRITE_TRUNCATE"
            )
            
            job = self.client.load_table_from_dataframe(
                mapping_df, table_id, job_config=job_config
            )
            job.result()  # Wait for completion
            
            return {
                'success': True,
                'rows_uploaded': len(mapping_df),
                'table': table_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'rows_uploaded': 0
            }

