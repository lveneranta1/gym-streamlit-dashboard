"""BigQuery uploader module for uploading workout data to Google BigQuery."""
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import Dict, Any, Optional
from datetime import datetime
import os


class BigQueryUploader:
    """Upload workout data to Google BigQuery."""
    
    def __init__(self, table_schema: Dict[str, Any], upload_settings: Dict[str, Any], location: str):
        """Initialize BigQuery uploader with configuration.
        
        Args:
            table_schema: The schema for the BigQuery table.
            upload_settings: Settings for the upload job.
            location: The GCP location for the BigQuery client.
        """
        self.table_schema_config = table_schema
        self.upload_settings = upload_settings
        self.location = location

        self.client: Optional[bigquery.Client] = None
        self.project_id: Optional[str] = None
        self.dataset_id: Optional[str] = None
        self.table_id: Optional[str] = None
        self.upload_stats: Dict[str, Any] = {}
        
    def initialize_client(self, project_id: str, dataset_id: str, table_id: str, credentials=None) -> bool:
        """Initialize BigQuery client with credentials and connection info.
        
        Args:
            project_id: The GCP Project ID.
            dataset_id: The BigQuery Dataset ID.
            table_id: The BigQuery Table ID.
            credentials: Optional Google Auth credentials object.
            
        Returns:
            True if initialization successful, False otherwise
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        
        try:
            self.client = bigquery.Client(
                project=self.project_id,
                credentials=credentials,
                location=self.location
            )
            self.client.query("SELECT 1").result()
            return True
        except Exception as e:
            raise Exception(f"Failed to initialize BigQuery client: {e}")
    
    def create_table_if_not_exists(self) -> bool:
        """Create BigQuery table if it doesn't exist."""
        if not all([self.client, self.project_id, self.dataset_id, self.table_id]):
            raise Exception("BigQuery client and connection info not initialized.")
        
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        
        try:
            self.client.get_table(table_ref)
            return True
        except Exception:
            pass # Table doesn't exist, create it below
        
        schema = [
            bigquery.SchemaField(field['name'], field['type'], mode=field.get('mode', 'NULLABLE'), description=field.get('description', ''))
            for field in self.table_schema_config
        ]
        
        table = bigquery.Table(table_ref, schema=schema)
        
        try:
            self.client.create_table(table)
            return True
        except Exception as e:
            raise Exception(f"Failed to create BigQuery table: {e}")
    
    def _add_metadata_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add metadata columns to dataframe before upload."""
        df = df.copy()
        df['upload_timestamp'] = pd.Timestamp.now()
        df['data_source'] = 'csv_upload'
        return df
    
    def _validate_schema(self, df: pd.DataFrame) -> bool:
        """Validate that DataFrame matches BigQuery schema."""
        required_fields = [field['name'] for field in self.table_schema_config if field.get('mode') == 'REQUIRED']
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            raise ValueError(f"DataFrame missing required fields: {', '.join(missing_fields)}")
        
        return True
    
    def upload_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Upload dataframe to BigQuery."""
        if not self.client:
            raise Exception("BigQuery client not initialized.")
        
        if df.empty:
            return {'success': False, 'error': 'DataFrame is empty', 'rows_uploaded': 0}
        
        start_time = datetime.now()
        df = self._add_metadata_columns(df)
        
        try:
            self._validate_schema(df)
        except ValueError as e:
            return {'success': False, 'error': str(e), 'rows_uploaded': 0}
        
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=self.upload_settings.get('write_disposition', 'WRITE_APPEND'),
            create_disposition=self.upload_settings.get('create_disposition', 'CREATE_IF_NEEDED')
        )
        
        try:
            job = self.client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            timeout = self.upload_settings.get('timeout_seconds', 300)
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
            self.upload_stats = {'success': False, 'error': str(e), 'rows_uploaded': 0}
            return self.upload_stats
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """Get statistics from last upload."""
        return self.upload_stats
    
    def test_connection(self) -> Dict[str, Any]:
        """Test BigQuery connection and configuration."""
        results = {'client_initialized': self.client is not None, 'can_query': False, 'table_exists': False}
        
        if not self.client:
            results['error'] = 'Client not initialized'
            return results
        
        try:
            self.client.query("SELECT 1").result()
            results['can_query'] = True
        except Exception as e:
            results['query_error'] = str(e)
        
        if all([self.project_id, self.dataset_id, self.table_id]):
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            try:
                table = self.client.get_table(table_ref)
                results['table_exists'] = True
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
            
            # Use connection info from initialized client
            project_id = self.project_id
            dataset_id = self.dataset_id

            if not all([project_id, dataset_id]):
                raise Exception("BigQuery client is not fully initialized with project and dataset IDs.")
            
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

