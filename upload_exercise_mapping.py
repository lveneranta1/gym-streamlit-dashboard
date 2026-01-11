#!/usr/bin/env python3
"""Upload exercise mapping data to BigQuery."""

import os
import sys
from modules.config_loader import ConfigLoader
from modules.bigquery_uploader import BigQueryUploader
from google.oauth2 import service_account

def main():
    """Upload exercise mapping to BigQuery."""
    print("🏋️  Uploading Exercise Mapping to BigQuery...")
    print("-" * 50)
    
    try:
        # Load configuration
        config_loader = ConfigLoader()
        
        # Load BigQuery config
        bq_config = config_loader.get_bigquery_config()
        table_schema = bq_config.get('table_schema', [])
        upload_settings = bq_config.get('upload', {})
        location = bq_config.get('connection', {}).get('location', 'europe-north1')
        
        # Get credentials from environment
        project_id = os.getenv('GCP_PROJECT_ID')
        dataset_id = os.getenv('BQ_DATASET_ID', 'workout_data')
        table_id = 'exercise_muscle_mapping'  # Different from workouts table
        
        # Try to use the terraform-generated service account key first
        creds_file = os.path.join(os.path.dirname(__file__), 'terraform', 'keys', 'service-account-key.json')
        if not os.path.exists(creds_file):
            # Fallback to environment variable
            creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not all([project_id, creds_file]):
            print("❌ Missing required environment variables:")
            print("  - GCP_PROJECT_ID")
            print("  - Service account key not found at terraform/keys/service-account-key.json")
            print("  - GOOGLE_APPLICATION_CREDENTIALS not set")
            sys.exit(1)
        
        print(f"📊 Project: {project_id}")
        print(f"📊 Dataset: {dataset_id}")
        print(f"📊 Table: {table_id}")
        print()
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(creds_file)
        
        # Initialize BigQuery uploader
        uploader = BigQueryUploader(
            table_schema=table_schema,
            upload_settings=upload_settings,
            location=location
        )
        
        uploader.initialize_client(
            project_id=project_id,
            dataset_id=dataset_id,
            table_id=table_id,
            credentials=credentials
        )
        
        # Load exercise mapping
        print("📖 Loading exercise mapping configuration...")
        mapping_config = config_loader.get_exercise_mapping()
        
        exercise_count = len(mapping_config.get('exercises', []))
        print(f"✅ Loaded {exercise_count} exercise groups")
        print()
        
        # Upload to BigQuery
        print("☁️  Uploading to BigQuery...")
        result = uploader.upload_exercise_mapping(mapping_config)
        
        if result.get('success'):
            print("✅ Upload successful!")
            print(f"📊 Rows uploaded: {result.get('rows_uploaded', 0)}")
            if 'job_id' in result:
                print(f"🔖 Job ID: {result['job_id']}")
        else:
            print("❌ Upload failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"❌ Configuration file not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("🎉 Done!")

if __name__ == "__main__":
    main()
