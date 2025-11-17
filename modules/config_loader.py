"""Configuration loader for YAML config files with environment variable support."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigLoader:
    """Load and manage YAML configuration files with environment variable substitution."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the configuration loader.
        
        Args:
            config_dir: Directory containing configuration YAML files
        """
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, Dict[str, Any]] = {}
        
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {self.config_dir}")
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file with caching.
        
        Args:
            filename: Name of the YAML file (e.g., 'csv_schema.yaml')
            
        Returns:
            Dictionary containing the configuration
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            yaml.YAMLError: If the YAML file is invalid
        """
        # Return cached config if available
        if filename in self._configs:
            return self._configs[filename]
        
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filepath}: {e}")
        
        # Replace environment variables in the config
        config = self._replace_env_vars(config)
        
        # Cache the config
        self._configs[filename] = config
        return config
    
    def _replace_env_vars(self, config: Any) -> Any:
        """Recursively replace ${VAR} placeholders with environment variables.
        
        Args:
            config: Configuration value (can be dict, list, string, etc.)
            
        Returns:
            Configuration with environment variables substituted
        """
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            var_name = config[2:-1]
            env_value = os.getenv(var_name)
            if env_value is None:
                # Keep the placeholder if environment variable is not set
                return config
            return env_value
        return config
    
    def get_csv_schema(self) -> Dict[str, Any]:
        """Load CSV schema configuration.
        
        Returns:
            CSV schema configuration dictionary
        """
        return self.load_yaml("csv_schema.yaml")
    
    def get_exercise_mapping(self) -> Dict[str, Any]:
        """Load exercise mapping configuration.
        
        Returns:
            Exercise mapping configuration dictionary
        """
        return self.load_yaml("exercise_mapping.yaml")
    
    def get_bigquery_config(self) -> Dict[str, Any]:
        """Load BigQuery configuration.
        
        Returns:
            BigQuery configuration dictionary
        """
        return self.load_yaml("bigquery_config.yaml")
    
    def reload_configs(self):
        """Clear cached configurations to force reload on next access."""
        self._configs.clear()
    
    def validate_env_vars(self) -> tuple[bool, list[str]]:
        """Validate that required environment variables are set.
        
        Returns:
            Tuple of (all_valid, missing_vars) where:
            - all_valid: True if all required env vars are set
            - missing_vars: List of missing environment variable names
        """
        required_vars = [
            "GCP_PROJECT_ID",
            "GOOGLE_APPLICATION_CREDENTIALS",
            "BQ_DATASET_ID",
            "BQ_TABLE_ID"
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        return len(missing) == 0, missing
