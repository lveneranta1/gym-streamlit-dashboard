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
    
    It prioritizes credentials from st.secrets['gcp_service_account'] and falls
    back to Application Default Credentials if they are not found.

    Args:
        _config_loader: ConfigLoader instance (underscore prefix prevents hashing)
        
    Returns:
        BigQueryUploader instance or None if initialization fails
    """
    if not _config_loader:
        return None
        
    try:
        bq_config = _config_loader.get_bigquery_config()
        
        # PRIORITY 1: Load credentials from Streamlit secrets
        credentials = None
        if "gcp_service_account" in st.secrets:
            creds_info = st.secrets["gcp_service_account"]
            credentials = service_account.Credentials.from_service_account_info(creds_info)

        # PRIORITY 2: If no secrets, ADC will be used by default inside initialize_client
        
        uploader = BigQueryUploader(bq_config)
        uploader.initialize_client(credentials=credentials) # Pass creds
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
