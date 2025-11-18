"""BigQuery view management for workout analytics."""
from google.cloud import bigquery
from pathlib import Path
from typing import Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class BigQueryViewManager:
    """Manage BigQuery analytical views."""
    
    def __init__(self, client: bigquery.Client, project_id: str, dataset_id: str):
        """Initialize view manager.
        
        Args:
            client: BigQuery client instance
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        self.client = client
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.sql_dir = Path("sql/views")
    
    def load_view_sql(self, view_name: str, table_id: str = "workouts") -> str:
        """Load SQL definition from file and substitute placeholders.
        
        Args:
            view_name: Name of the view (matches SQL filename without extension)
            table_id: Table ID to substitute in SQL
            
        Returns:
            SQL query string with placeholders replaced
            
        Raises:
            FileNotFoundError: If SQL file doesn't exist
        """
        sql_file = self.sql_dir / f"{view_name}.sql"
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        
        with open(sql_file, 'r') as f:
            sql_template = f.read()
        
        # Substitute placeholders
        sql_query = sql_template.format(
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            table_id=table_id
        )
        
        return sql_query
    
    def create_or_update_view(self, view_name: str, table_id: str = "workouts") -> bool:
        """Create or replace a BigQuery view.
        
        Args:
            view_name: Name of the view to create/update
            table_id: Table ID referenced in the view
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load SQL from file
            view_sql = self.load_view_sql(view_name, table_id)
            
            # Construct full view ID
            view_id = f"{self.project_id}.{self.dataset_id}.{view_name}"
            
            # Execute CREATE OR REPLACE VIEW
            ddl_query = f"CREATE OR REPLACE VIEW `{view_id}` AS\n{view_sql}"
            
            logger.info(f"Creating/updating view: {view_id}")
            query_job = self.client.query(ddl_query)
            query_job.result()  # Wait for completion
            
            logger.info(f"Successfully created/updated view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create/update view {view_name}: {str(e)}")
            return False
    
    def refresh_all_views(self, view_configs: List[Dict[str, str]], table_id: str = "workouts") -> Dict[str, bool]:
        """Refresh all configured views.
        
        Args:
            view_configs: List of view config dicts with 'name' keys
            table_id: Table ID referenced in views
            
        Returns:
            Dictionary mapping view names to success status
        """
        results = {}
        
        for view_config in view_configs:
            view_name = view_config['name']
            success = self.create_or_update_view(view_name, table_id)
            results[view_name] = success
        
        successful = sum(1 for status in results.values() if status)
        total = len(results)
        
        logger.info(f"View refresh complete: {successful}/{total} successful")
        
        return results
