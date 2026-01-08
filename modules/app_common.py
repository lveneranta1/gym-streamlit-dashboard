"""Common initialization and configuration for all Streamlit pages."""
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import service_account
from modules.config_loader import ConfigLoader
from modules.bigquery_uploader import BigQueryUploader

# Load environment variables from .env file at repository root
load_dotenv()


def init_page_config(page_title: str = "Workout Data", page_icon: str = "🏋️"):
    """Initialize Streamlit page configuration.
    
    Args:
        page_title: Title for the page
        page_icon: Icon emoji for the page
    """
    try:
        st.set_page_config(
            page_title=page_title,
            page_icon=page_icon,
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except st.errors.StreamlitAPIException:
        # Page config already set, ignore
        pass


@st.cache_resource
def get_config_loader():
    """Get cached configuration loader.
    
    Returns:
        ConfigLoader instance or None if initialization fails
    """
    try:
        return ConfigLoader()
    except Exception as e:
        st.error(f"Failed to load configurations: {e}")
        return None


@st.cache_resource
def get_bigquery_uploader(_config_loader: ConfigLoader):
    """Get cached BigQuery uploader instance.
    
    It prioritizes credentials from st.secrets and passes them to the uploader.

    Args:
        _config_loader: ConfigLoader instance (underscore prefix prevents hashing)
        
    Returns:
        BigQueryUploader instance or None if initialization fails
    """
    if not _config_loader:
        return None
        
    try:
        # Load non-sensitive BQ settings from YAML
        bq_config = _config_loader.get_bigquery_config()
        table_schema = bq_config.get('table_schema', [])
        upload_settings = bq_config.get('upload', {})
        location = bq_config.get('connection', {}).get('location', 'US')

        # Load sensitive connection details from Streamlit secrets
        gcp_creds_info = st.secrets.get("gcp_service_account")
        dataset_id = st.secrets.get("bq_dataset_id")
        table_id = st.secrets.get("bq_table_id")

        if not all([gcp_creds_info, dataset_id, table_id]):
            st.error("Missing required BigQuery connection info in .streamlit/secrets.toml")
            return None
        
        project_id = gcp_creds_info.get("project_id")
        credentials = service_account.Credentials.from_service_account_info(gcp_creds_info)
        
        # Instantiate uploader with non-sensitive config
        uploader = BigQueryUploader(
            table_schema=table_schema,
            upload_settings=upload_settings,
            location=location
        )
        
        # Initialize client with sensitive connection details
        uploader.initialize_client(
            project_id=project_id,
            dataset_id=dataset_id,
            table_id=table_id,
            credentials=credentials
        )
        return uploader
        
    except Exception as e:
        st.error(f"Failed to initialize BigQuery client: {e}")
        return None


def render_sidebar(config_loader: ConfigLoader = None):
    """Render sidebar with app information and status.
    
    Args:
        config_loader: ConfigLoader instance for checking environment variables
    """
    st.sidebar.title("🏋️ Workout Uploader")
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("Connection")
    if st.sidebar.button("🔌 Test BigQuery Connection"):
        if not config_loader:
            st.sidebar.error("Config loader not initialized.")
            return

        if "gcp_service_account" not in st.secrets:
            st.sidebar.warning("`gcp_service_account` not in secrets.")
            return

        try:
            with st.spinner("Testing connection..."):
                uploader = get_bigquery_uploader(config_loader)
                
                if not uploader or not uploader.client:
                    st.sidebar.error("Connection failed.")
                    return

                test_results = uploader.test_connection()
            
            if test_results.get('can_query'):
                st.sidebar.success("Connection successful!")
                st.sidebar.metric("Project ID", uploader.client.project)
                if test_results.get('table_exists'):
                    st.sidebar.metric("Workout Table Rows", f"{test_results.get('table_rows', 0):,}")
                else:
                    st.sidebar.warning("Workout table not found.")
            else:
                st.sidebar.error("Connection failed.")
        
        except Exception as e:
            st.sidebar.error(f"Connection test failed: {e}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("About")
    st.sidebar.info(
        "Upload workout CSV files to Google BigQuery with automatic "
        "exercise-to-muscle group mapping and analytics."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Version 1.0.0")


def check_environment_vars(config_loader: ConfigLoader) -> tuple[bool, list[str]]:
    """Check if required environment variables are set.
    
    Args:
        config_loader: ConfigLoader instance
        
    Returns:
        Tuple of (all_valid, missing_vars)
    """
    if not config_loader:
        return False, ["ConfigLoader not initialized"]
    
    return config_loader.validate_env_vars()


def show_env_var_warning(missing_vars: list[str]):
    """Display warning about missing environment variables.
    
    Args:
        missing_vars: List of missing environment variable names
    """
    st.warning("⚠️ Some environment variables are not configured. BigQuery operations may fail.")
    with st.expander("Show missing variables"):
        for var in missing_vars:
            st.write(f"- `{var}`")
        st.info("Please set these in your `.env` file. See `.env.example` for reference.")
