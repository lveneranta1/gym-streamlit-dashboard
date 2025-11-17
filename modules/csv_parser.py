"""CSV parser with flexible column mapping and validation."""
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import io


class CSVParser:
    """Parse and validate CSV files based on schema configuration."""
    
    def __init__(self, schema_config: Dict[str, Any]):
        """Initialize the CSV parser with schema configuration.
        
        Args:
            schema_config: Dictionary containing CSV schema configuration
        """
        self.schema = schema_config
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.column_mappings: Dict[str, str] = {}
    
    def parse_csv(self, file: Union[str, io.BytesIO]) -> pd.DataFrame:
        """Parse and validate a CSV file.
        
        Args:
            file: File path or file-like object
            
        Returns:
            Cleaned and validated pandas DataFrame
            
        Raises:
            ValueError: If validation fails critically
        """
        self.errors = []
        self.warnings = []
        self.column_mappings = {}
        
        # Read CSV file
        try:
            if isinstance(file, str):
                df = pd.read_csv(file)
            else:
                df = pd.read_csv(file)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {e}")
        
        if df.empty:
            raise ValueError("CSV file is empty")
        
        # Map columns to standard names
        df = self._map_columns(df)
        
        # Validate required columns
        self._validate_required_columns(df)
        
        # Add optional columns with defaults
        df = self._add_optional_columns(df)
        
        # Validate and convert data types
        df = self._validate_data_types(df)
        
        # Validate constraints
        self._validate_constraints(df)
        
        # If strict mode and there are errors, raise exception
        if self.schema.get('strict_mode', False) and self.errors:
            raise ValueError(f"Validation failed: {'; '.join(self.errors)}")
        
        return df
    
    def _map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map CSV columns to standard names using aliases.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with mapped column names
        """
        case_sensitive = self.schema.get('case_sensitive', False)
        df_columns = df.columns.tolist()
        
        # Create a mapping from actual columns to standard names
        mapped_columns = {}
        
        # Check all required columns
        for std_name, config in self.schema['required_columns'].items():
            aliases = config.get('aliases', [std_name])
            matched = False
            
            for col in df_columns:
                col_compare = col if case_sensitive else col.lower()
                
                for alias in aliases:
                    alias_compare = alias if case_sensitive else alias.lower()
                    if col_compare == alias_compare:
                        mapped_columns[col] = std_name
                        self.column_mappings[std_name] = col
                        matched = True
                        break
                
                if matched:
                    break
        
        # Check optional columns
        for std_name, config in self.schema.get('optional_columns', {}).items():
            aliases = config.get('aliases', [std_name])
            matched = False
            
            for col in df_columns:
                col_compare = col if case_sensitive else col.lower()
                
                for alias in aliases:
                    alias_compare = alias if case_sensitive else alias.lower()
                    if col_compare == alias_compare:
                        mapped_columns[col] = std_name
                        self.column_mappings[std_name] = col
                        matched = True
                        break
                
                if matched:
                    break
        
        # Rename columns
        df = df.rename(columns=mapped_columns)
        
        return df
    
    def _validate_required_columns(self, df: pd.DataFrame):
        """Validate that all required columns are present.
        
        Args:
            df: DataFrame to validate
        """
        required_cols = list(self.schema['required_columns'].keys())
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            self.errors.append(f"Missing required columns: {', '.join(missing_cols)}")
    
    def _add_optional_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add optional columns with default values if not present.
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with optional columns added
        """
        optional_cols = self.schema.get('optional_columns', {})
        
        for col_name, config in optional_cols.items():
            if col_name not in df.columns:
                default_value = config.get('default')
                df[col_name] = default_value
                if default_value is not None:
                    self.warnings.append(f"Added column '{col_name}' with default value: {default_value}")
        
        return df
    
    def _validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and convert data types.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            DataFrame with converted data types
        """
        all_columns = {**self.schema['required_columns'], **self.schema.get('optional_columns', {})}
        
        for col_name, config in all_columns.items():
            if col_name not in df.columns:
                continue
            
            dtype = config.get('type')
            
            try:
                if dtype == 'datetime':
                    df[col_name] = self._parse_datetime(df[col_name], config)
                elif dtype == 'integer':
                    df[col_name] = pd.to_numeric(df[col_name], errors='coerce').astype('Int64')
                    # Check for NaN values after conversion
                    null_count = df[col_name].isna().sum()
                    if null_count > 0:
                        self.errors.append(f"Column '{col_name}': {null_count} values could not be converted to integer")
                elif dtype == 'float':
                    df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                    null_count = df[col_name].isna().sum()
                    if null_count > 0:
                        self.errors.append(f"Column '{col_name}': {null_count} values could not be converted to float")
                elif dtype == 'string':
                    df[col_name] = df[col_name].astype(str)
                    # Replace 'nan' string with empty string
                    df[col_name] = df[col_name].replace('nan', '')
            except Exception as e:
                self.errors.append(f"Error converting column '{col_name}' to {dtype}: {e}")
        
        return df
    
    def _parse_datetime(self, series: pd.Series, config: Dict[str, Any]) -> pd.Series:
        """Parse datetime column with multiple format support.
        
        Args:
            series: Pandas Series containing datetime values
            config: Column configuration with datetime formats
            
        Returns:
            Series with parsed datetime values
        """
        formats = config.get('formats', ['%Y-%m-%d %H:%M:%S'])
        parsed_series = None
        
        for fmt in formats:
            try:
                parsed_series = pd.to_datetime(series, format=fmt, errors='coerce')
                # If we got some successful parses, use this format
                if parsed_series.notna().sum() > 0:
                    break
            except:
                continue
        
        # Try pandas automatic date parsing as fallback
        if parsed_series is None or parsed_series.notna().sum() == 0:
            parsed_series = pd.to_datetime(series, errors='coerce')
        
        return parsed_series
    
    def _validate_constraints(self, df: pd.DataFrame):
        """Validate data constraints (min/max values, etc.).
        
        Args:
            df: DataFrame to validate
        """
        all_columns = {**self.schema['required_columns'], **self.schema.get('optional_columns', {})}
        
        for col_name, config in all_columns.items():
            if col_name not in df.columns:
                continue
            
            validation = config.get('validation', {})
            
            # Check min value
            if 'min' in validation:
                min_val = validation['min']
                below_min = df[df[col_name] < min_val]
                if not below_min.empty:
                    self.errors.append(
                        f"Column '{col_name}': {len(below_min)} values below minimum {min_val}"
                    )
            
            # Check max value
            if 'max' in validation:
                max_val = validation['max']
                above_max = df[df[col_name] > max_val]
                if not above_max.empty:
                    self.errors.append(
                        f"Column '{col_name}': {len(above_max)} values above maximum {max_val}"
                    )
            
            # Check for null values in required columns
            if col_name in self.schema['required_columns']:
                null_count = df[col_name].isna().sum()
                if null_count > 0:
                    self.errors.append(
                        f"Column '{col_name}': {null_count} null values found (required field)"
                    )
        
        # Validate datetime is not in the future
        if 'datetime' in df.columns:
            future_dates = df[df['datetime'] > pd.Timestamp.now()]
            if not future_dates.empty:
                self.warnings.append(
                    f"Found {len(future_dates)} entries with future dates"
                )
    
    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors.
        
        Returns:
            List of error messages
        """
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Get list of validation warnings.
        
        Returns:
            List of warning messages
        """
        return self.warnings
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary.
        
        Returns:
            Dictionary with validation summary
        """
        return {
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'column_mappings': self.column_mappings,
            'has_errors': len(self.errors) > 0
        }
