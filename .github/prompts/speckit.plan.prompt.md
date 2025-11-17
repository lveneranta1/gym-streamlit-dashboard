---
agent: speckit.plan
---

# Workout Data Upload to BigQuery - Implementation Plan

## Project Overview
Build a Streamlit application that allows users to upload workout CSV data, parse it using a configurable schema, enrich it with muscle group mappings, and upload to Google BigQuery.

---

## Phase 1: Project Setup & Configuration System

### 1.1 Initialize Project Structure
**Tasks:**
- [ ] Create project directory structure
- [ ] Initialize git repository
- [ ] Create `requirements.txt` with dependencies
- [ ] Set up `.gitignore` for Python/Streamlit projects
- [ ] Create `.env.example` for environment variables

**Files to create:**
```
gym-streamlit-dashboard/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── config/
│   ├── csv_schema.yaml
│   ├── exercise_mapping.yaml
│   └── bigquery_config.yaml
├── modules/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── csv_parser.py
│   ├── data_enrichment.py
│   └── bigquery_uploader.py
└── tests/
    └── sample_workout_data.csv
```

**Dependencies (requirements.txt):**
```
streamlit>=1.28.0
pandas>=2.0.0
pyyaml>=6.0
google-cloud-bigquery>=3.11.0
google-auth>=2.22.0
python-dotenv>=1.0.0
```

**Estimated time:** 30 minutes

---

### 1.2 Create Configuration Files

#### Task: Create `config/csv_schema.yaml`
Define the modular CSV schema structure.

**File content:**
```yaml
# CSV Schema Configuration
version: "1.0"

required_columns:
  datetime:
    type: datetime
    formats:
      - "%Y-%m-%d %H:%M:%S"
      - "%Y-%m-%d"
      - "%m/%d/%Y"
    aliases: ["datetime", "date", "timestamp", "workout_date"]
    
  workout_name:
    type: string
    aliases: ["workout_name", "workout", "session_name", "workout_type"]
    
  exercise_name:
    type: string
    aliases: ["exercise_name", "exercise", "movement", "name"]
    
  weight:
    type: float
    aliases: ["weight", "weight_kg", "weight_lbs", "load"]
    validation:
      min: 0
      max: 1000
    
  reps:
    type: integer
    aliases: ["reps", "repetitions", "rep_count"]
    validation:
      min: 1
      max: 100

optional_columns:
  sets:
    type: integer
    default: 1
    aliases: ["sets", "set_count"]
    
  notes:
    type: string
    default: ""
    aliases: ["notes", "comments", "description"]
    
  duration_minutes:
    type: integer
    default: null
    aliases: ["duration", "duration_minutes", "time_minutes"]

# Column mapping flexibility
allow_extra_columns: true
strict_mode: false  # If true, reject uploads with missing required columns
```

**Estimated time:** 20 minutes

---

#### Task: Create `config/exercise_mapping.yaml`
Define exercise to muscle group mappings.

**File content:**
```yaml
# Exercise to Muscle Group Mapping
version: "1.0"

muscle_groups:
  level1:
    - upper
    - lower
    - core
    - full_body
    
  level2:
    upper: [chest, back, shoulders, triceps, biceps, forearms]
    lower: [quads, hamstrings, glutes, calves]
    core: [abs, obliques, lower_back]
    full_body: [compound]

# Exercise mappings (case-insensitive matching)
exercises:
  # Chest exercises
  - names: 
      - "bench press"
      - "barbell bench press"
      - "dumbbell bench press"
      - "flat bench press"
    level1: upper
    level2: chest
    
  - names:
      - "incline bench press"
      - "incline press"
      - "incline dumbbell press"
    level1: upper
    level2: chest
    
  - names:
      - "chest fly"
      - "dumbbell fly"
      - "cable fly"
      - "pec fly"
    level1: upper
    level2: chest
    
  - names:
      - "push up"
      - "pushup"
    level1: upper
    level2: chest

  # Back exercises
  - names:
      - "deadlift"
      - "conventional deadlift"
      - "barbell deadlift"
    level1: full_body
    level2: compound
    
  - names:
      - "romanian deadlift"
      - "rdl"
      - "stiff leg deadlift"
    level1: lower
    level2: hamstrings
    
  - names:
      - "pull up"
      - "pullup"
      - "chin up"
      - "chinup"
    level1: upper
    level2: back
    
  - names:
      - "barbell row"
      - "bent over row"
      - "bent-over row"
      - "pendlay row"
    level1: upper
    level2: back
    
  - names:
      - "dumbbell row"
      - "one arm row"
      - "single arm row"
    level1: upper
    level2: back
    
  - names:
      - "lat pulldown"
      - "cable pulldown"
      - "wide grip pulldown"
    level1: upper
    level2: back

  # Leg exercises
  - names:
      - "squat"
      - "back squat"
      - "barbell squat"
      - "high bar squat"
      - "low bar squat"
    level1: lower
    level2: quads
    
  - names:
      - "front squat"
    level1: lower
    level2: quads
    
  - names:
      - "leg press"
    level1: lower
    level2: quads
    
  - names:
      - "leg extension"
      - "quad extension"
    level1: lower
    level2: quads
    
  - names:
      - "leg curl"
      - "hamstring curl"
      - "lying leg curl"
      - "seated leg curl"
    level1: lower
    level2: hamstrings
    
  - names:
      - "lunge"
      - "walking lunge"
      - "reverse lunge"
      - "forward lunge"
    level1: lower
    level2: quads
    
  - names:
      - "calf raise"
      - "standing calf raise"
      - "seated calf raise"
    level1: lower
    level2: calves

  # Shoulder exercises
  - names:
      - "overhead press"
      - "military press"
      - "shoulder press"
      - "barbell overhead press"
    level1: upper
    level2: shoulders
    
  - names:
      - "dumbbell shoulder press"
      - "dumbbell press"
      - "seated dumbbell press"
    level1: upper
    level2: shoulders
    
  - names:
      - "lateral raise"
      - "side raise"
      - "dumbbell lateral raise"
    level1: upper
    level2: shoulders
    
  - names:
      - "front raise"
      - "front delt raise"
    level1: upper
    level2: shoulders

  # Arm exercises
  - names:
      - "bicep curl"
      - "barbell curl"
      - "ez bar curl"
      - "dumbbell curl"
    level1: upper
    level2: biceps
    
  - names:
      - "hammer curl"
      - "dumbbell hammer curl"
    level1: upper
    level2: biceps
    
  - names:
      - "tricep extension"
      - "overhead extension"
      - "overhead tricep extension"
      - "skull crusher"
      - "lying tricep extension"
    level1: upper
    level2: triceps
    
  - names:
      - "tricep dip"
      - "dips"
      - "chest dip"
    level1: upper
    level2: triceps
    
  - names:
      - "tricep pushdown"
      - "cable pushdown"
      - "rope pushdown"
    level1: upper
    level2: triceps

  # Core exercises
  - names:
      - "plank"
      - "front plank"
    level1: core
    level2: abs
    
  - names:
      - "crunch"
      - "sit up"
      - "situp"
    level1: core
    level2: abs

# Fuzzy matching rules for unmapped exercises
fuzzy_rules:
  - keyword: "press"
    exclude: ["leg press"]
    level1: upper
    level2: chest
    
  - keyword: "curl"
    level1: upper
    level2: biceps
    
  - keyword: "squat"
    level1: lower
    level2: quads
    
  - keyword: "deadlift"
    level1: lower
    level2: hamstrings
    
  - keyword: "row"
    level1: upper
    level2: back
    
  - keyword: "raise"
    level1: upper
    level2: shoulders

# Default for completely unknown exercises
default_mapping:
  level1: upper
  level2: unknown
```

**Estimated time:** 45 minutes

---

#### Task: Create `config/bigquery_config.yaml`
Configure BigQuery connection and schema.

**File content:**
```yaml
# BigQuery Configuration
version: "1.0"

# Connection settings (use environment variables for sensitive data)
connection:
  project_id: "${GCP_PROJECT_ID}"
  dataset_id: "workout_data"
  table_id: "workouts"
  credentials_path: "${GOOGLE_APPLICATION_CREDENTIALS}"

# BigQuery table schema
table_schema:
  - name: datetime
    type: TIMESTAMP
    mode: REQUIRED
    
  - name: workout_name
    type: STRING
    mode: REQUIRED
    
  - name: exercise_name
    type: STRING
    mode: REQUIRED
    
  - name: weight
    type: FLOAT
    mode: REQUIRED
    
  - name: reps
    type: INTEGER
    mode: REQUIRED
    
  - name: sets
    type: INTEGER
    mode: NULLABLE
    
  - name: notes
    type: STRING
    mode: NULLABLE
    
  - name: duration_minutes
    type: INTEGER
    mode: NULLABLE
    
  - name: muscle_group_level1
    type: STRING
    mode: REQUIRED
    
  - name: muscle_group_level2
    type: STRING
    mode: REQUIRED
    
  - name: upload_timestamp
    type: TIMESTAMP
    mode: REQUIRED
    
  - name: data_source
    type: STRING
    mode: NULLABLE

# Upload settings
upload:
  write_disposition: "WRITE_APPEND"  # WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY
  create_disposition: "CREATE_IF_NEEDED"  # CREATE_IF_NEEDED, CREATE_NEVER
  batch_size: 1000
  timeout_seconds: 300
```

**Estimated time:** 15 minutes

---

### 1.3 Create Configuration Loader Module

#### Task: Implement `modules/config_loader.py`

**File content:**
```python
"""Configuration loader for YAML config files."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ConfigLoader:
    """Load and manage configuration files."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._configs = {}
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file."""
        if filename in self._configs:
            return self._configs[filename]
        
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        
        # Replace environment variables
        config = self._replace_env_vars(config)
        
        self._configs[filename] = config
        return config
    
    def _replace_env_vars(self, config: Any) -> Any:
        """Recursively replace ${VAR} with environment variables."""
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            var_name = config[2:-1]
            return os.getenv(var_name, config)
        return config
    
    def get_csv_schema(self) -> Dict[str, Any]:
        """Load CSV schema configuration."""
        return self.load_yaml("csv_schema.yaml")
    
    def get_exercise_mapping(self) -> Dict[str, Any]:
        """Load exercise mapping configuration."""
        return self.load_yaml("exercise_mapping.yaml")
    
    def get_bigquery_config(self) -> Dict[str, Any]:
        """Load BigQuery configuration."""
        return self.load_yaml("bigquery_config.yaml")
```

**Estimated time:** 30 minutes

---

## Phase 2: CSV Parsing Module

### 2.1 Implement CSV Parser

#### Task: Create `modules/csv_parser.py`

**Features:**
- Parse CSV files based on schema configuration
- Handle flexible column name matching (aliases)
- Validate data types and constraints
- Provide detailed error messages

**Key functions:**
```python
class CSVParser:
    def __init__(self, schema_config: Dict[str, Any])
    def parse_csv(self, file) -> pd.DataFrame
    def _map_columns(self, df: pd.DataFrame) -> pd.DataFrame
    def _validate_required_columns(self, df: pd.DataFrame)
    def _validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame
    def _validate_constraints(self, df: pd.DataFrame)
    def get_validation_errors(self) -> List[str]
```

**Validation rules:**
- Check required columns present (using aliases)
- Convert data types (datetime, float, int)
- Validate constraints (min/max values)
- Handle missing optional columns with defaults

**Estimated time:** 2 hours

---

## Phase 3: Data Enrichment Module

### 3.1 Implement Muscle Group Mapping

#### Task: Create `modules/data_enrichment.py`

**Features:**
- Map exercises to muscle groups using configuration
- Support exact matching and fuzzy matching
- Handle unmapped exercises gracefully
- Add enrichment metadata columns

**Key functions:**
```python
class DataEnrichment:
    def __init__(self, mapping_config: Dict[str, Any])
    def enrich_dataframe(self, df: pd.DataFrame) -> pd.DataFrame
    def _map_exercise_to_muscles(self, exercise_name: str) -> Dict[str, str]
    def _exact_match(self, exercise_name: str) -> Optional[Dict]
    def _fuzzy_match(self, exercise_name: str) -> Optional[Dict]
    def _apply_default_mapping(self) -> Dict[str, str]
    def get_unmapped_exercises(self) -> List[str]
```

**Logic:**
1. Normalize exercise name (lowercase, strip whitespace)
2. Try exact match against configured exercises
3. If no match, try fuzzy rules (keyword matching)
4. If still no match, apply default mapping
5. Add `muscle_group_level1` and `muscle_group_level2` columns
6. Track unmapped exercises for user review

**Estimated time:** 1.5 hours

---

## Phase 4: BigQuery Upload Module

### 4.1 Implement BigQuery Uploader

#### Task: Create `modules/bigquery_uploader.py`

**Features:**
- Initialize BigQuery client with credentials
- Create table if not exists (based on schema config)
- Upload dataframe to BigQuery
- Handle upload errors and retries
- Add metadata columns (upload_timestamp, data_source)

**Key functions:**
```python
class BigQueryUploader:
    def __init__(self, bq_config: Dict[str, Any])
    def initialize_client(self)
    def create_table_if_not_exists(self)
    def upload_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]
    def _add_metadata_columns(self, df: pd.DataFrame) -> pd.DataFrame
    def _validate_schema(self, df: pd.DataFrame)
    def get_upload_stats(self) -> Dict[str, int]
```

**Upload process:**
1. Add metadata columns (upload_timestamp = now, data_source = "csv_upload")
2. Validate dataframe matches BigQuery schema
3. Upload using `load_table_from_dataframe()`
4. Return upload statistics (rows uploaded, errors, duration)

**Error handling:**
- Catch authentication errors
- Handle schema mismatches
- Retry failed uploads
- Log detailed error messages

**Estimated time:** 2 hours

---

## Phase 5: Streamlit UI

### 5.1 Create Main App Interface

#### Task: Implement `app.py`

**Page structure:**

```python
import streamlit as st
from modules.config_loader import ConfigLoader
from modules.csv_parser import CSVParser
from modules.data_enrichment import DataEnrichment
from modules.bigquery_uploader import BigQueryUploader

st.set_page_config(page_title="Workout Data Uploader", layout="wide")

def main():
    st.title("🏋️ Workout Data Uploader to BigQuery")
    
    # Sidebar
    st.sidebar.header("Configuration")
    # Add config file editors/viewers
    
    # Main content
    tabs = st.tabs(["📤 Upload", "⚙️ Schema Config", "💪 Exercise Mapping", "📊 BigQuery Config"])
    
    with tabs[0]:
        upload_page()
    
    with tabs[1]:
        schema_config_page()
    
    with tabs[2]:
        exercise_mapping_page()
    
    with tabs[3]:
        bigquery_config_page()
```

**Upload page workflow:**
1. File uploader widget
2. Parse CSV and show preview
3. Display column mappings
4. Show data validation results
5. Preview enriched data with muscle groups
6. Upload button
7. Progress bar during upload
8. Success/error messages with stats

**Estimated time:** 3 hours

---

### 5.2 Implement Upload Workflow

**Step-by-step UI:**

```python
def upload_page():
    st.header("Upload Workout Data")
    
    # Step 1: File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Upload your workout data CSV file"
    )
    
    if uploaded_file:
        # Step 2: Parse and validate
        with st.spinner("Parsing CSV..."):
            parser = CSVParser(config_loader.get_csv_schema())
            df = parser.parse_csv(uploaded_file)
        
        # Show validation results
        errors = parser.get_validation_errors()
        if errors:
            st.error("Validation errors found:")
            for error in errors:
                st.write(f"- {error}")
            return
        
        st.success(f"✅ Parsed {len(df)} rows successfully")
        
        # Step 3: Preview data
        st.subheader("Data Preview")
        st.dataframe(df.head(10))
        
        # Step 4: Enrich data
        with st.spinner("Enriching data with muscle groups..."):
            enrichment = DataEnrichment(config_loader.get_exercise_mapping())
            df_enriched = enrichment.enrich_dataframe(df)
        
        # Show unmapped exercises
        unmapped = enrichment.get_unmapped_exercises()
        if unmapped:
            st.warning(f"⚠️ {len(unmapped)} exercises not mapped:")
            st.write(unmapped)
        
        # Step 5: Preview enriched data
        st.subheader("Enriched Data Preview")
        st.dataframe(df_enriched[['exercise_name', 'muscle_group_level1', 'muscle_group_level2']].head(10))
        
        # Step 6: Upload to BigQuery
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📤 Upload to BigQuery", type="primary"):
                upload_to_bigquery(df_enriched)
        with col2:
            st.info(f"Ready to upload {len(df_enriched)} rows")
```

**Estimated time:** 2 hours

---

### 5.3 Configuration Editor Pages

#### Task: Create interactive config editors

**Features:**
- View current configuration
- Edit YAML files through UI
- Add custom exercise mappings
- Test configuration changes
- Save updated configs

**Schema config page:**
- Display current schema
- Add/remove optional columns
- Modify validation rules
- Test with sample data

**Exercise mapping page:**
- List all mapped exercises
- Add new exercise mappings
- Edit existing mappings
- Preview muscle group distribution

**BigQuery config page:**
- Display connection settings
- Test BigQuery connection
- View table schema
- Modify upload settings

**Estimated time:** 2.5 hours

---

## Phase 6: Testing & Validation

### 6.1 Create Test Data

#### Task: Generate `tests/sample_workout_data.csv`

**Sample data:**
```csv
datetime,workout_name,exercise_name,weight,reps,sets,notes
2024-01-15 09:00:00,Push Day,Bench Press,100,8,3,Felt strong
2024-01-15 09:15:00,Push Day,Incline Bench Press,80,10,3,
2024-01-15 09:30:00,Push Day,Dumbbell Fly,25,12,3,
2024-01-17 10:00:00,Pull Day,Deadlift,150,5,3,New PR!
2024-01-17 10:20:00,Pull Day,Pull Up,0,10,3,Bodyweight
2024-01-17 10:35:00,Pull Day,Barbell Row,90,8,3,
2024-01-19 08:00:00,Leg Day,Squat,120,10,3,
2024-01-19 08:20:00,Leg Day,Leg Press,200,12,3,
2024-01-19 08:35:00,Leg Day,Leg Curl,60,12,3,
```

**Estimated time:** 15 minutes

---

### 6.2 Unit Tests

#### Task: Create unit tests for each module

**Test files:**
- `tests/test_config_loader.py`
- `tests/test_csv_parser.py`
- `tests/test_data_enrichment.py`
- `tests/test_bigquery_uploader.py`

**Test coverage:**
- Config loading with env vars
- CSV parsing with various formats
- Column alias matching
- Data type validation
- Exercise mapping (exact, fuzzy, default)
- BigQuery schema validation
- Upload error handling

**Estimated time:** 3 hours

---

### 6.3 Integration Testing

#### Task: End-to-end testing

**Test scenarios:**
1. Upload valid CSV → Verify data in BigQuery
2. Upload CSV with wrong columns → Show proper errors
3. Upload CSV with invalid dates → Show validation errors
4. Upload CSV with unmapped exercises → Apply fuzzy/default mapping
5. Upload large CSV (10k+ rows) → Test performance
6. Modify config → Verify changes take effect

**Estimated time:** 2 hours

---

## Phase 7: Documentation & Deployment

### 7.1 Create Documentation

#### Task: Write comprehensive README.md

**Sections:**
- Project overview
- Features
- Installation instructions
- Configuration guide
- Usage examples
- Troubleshooting
- Development setup

**Estimated time:** 1.5 hours

---

### 7.2 Environment Setup Guide

#### Task: Create `.env.example`

```bash
# Google Cloud Platform
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# BigQuery
BQ_DATASET_ID=workout_data
BQ_TABLE_ID=workouts
```

**Estimated time:** 15 minutes

---

### 7.3 Deployment Preparation

#### Task: Prepare for deployment

**Checklist:**
- [ ] Add error logging (Sentry, Cloud Logging)
- [ ] Add usage analytics
- [ ] Create deployment script
- [ ] Set up CI/CD (GitHub Actions)
- [ ] Security review (credentials, permissions)
- [ ] Performance optimization
- [ ] Add rate limiting for uploads

**Estimated time:** 2 hours

---

## Timeline Summary

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Setup & Config | Project structure, config files, loader | 2.5 hours |
| Phase 2: CSV Parser | Parsing, validation, error handling | 2 hours |
| Phase 3: Data Enrichment | Exercise mapping, fuzzy matching | 1.5 hours |
| Phase 4: BigQuery Upload | Client setup, upload logic, error handling | 2 hours |
| Phase 5: Streamlit UI | Main app, upload workflow, config editors | 7.5 hours |
| Phase 6: Testing | Test data, unit tests, integration tests | 5.25 hours |
| Phase 7: Documentation | README, env setup, deployment | 3.75 hours |
| **Total** | | **~24.5 hours** |

---

## Implementation Order

### Week 1: Core Functionality
1. ✅ Project setup and configuration system (Phase 1)
2. ✅ CSV parser module (Phase 2)
3. ✅ Data enrichment module (Phase 3)
4. ✅ Basic Streamlit UI for upload (Phase 5.1, 5.2)

### Week 2: BigQuery & Polish
5. ✅ BigQuery uploader module (Phase 4)
6. ✅ Configuration editor pages (Phase 5.3)
7. ✅ Testing suite (Phase 6)
8. ✅ Documentation and deployment (Phase 7)

---

## Success Criteria

### MVP Requirements
- ✅ Upload CSV files through Streamlit interface
- ✅ Parse CSV based on configurable schema
- ✅ Map exercises to muscle groups (level 1 & 2)
- ✅ Upload enriched data to BigQuery
- ✅ Display validation errors clearly
- ✅ Show upload success/failure with stats

### Nice-to-Have Features
- ⭐ Interactive config editing in UI
- ⭐ Preview data before upload with filtering
- ⭐ Batch upload multiple files
- ⭐ Download enriched CSV before BigQuery upload
- ⭐ View upload history and statistics
- ⭐ Rollback functionality for uploads

---

## Risk Mitigation

### Technical Risks
1. **BigQuery authentication issues**
   - Mitigation: Clear setup guide, test connection button, detailed error messages

2. **CSV format variations**
   - Mitigation: Flexible column aliases, preview before upload, clear validation errors

3. **Exercise mapping accuracy**
   - Mitigation: Comprehensive default mappings, fuzzy matching, user review of unmapped

4. **Large file uploads**
   - Mitigation: Batch processing, progress indicators, timeout handling

### Configuration Risks
1. **Invalid YAML syntax**
   - Mitigation: YAML validation, schema validation, example configs

2. **Missing environment variables**
   - Mitigation: Clear error messages, .env.example file, validation at startup

---

## Next Steps After Implementation

1. **User feedback collection**
   - Add feedback form in app
   - Monitor upload errors and patterns

2. **Feature enhancements**
   - Add data visualization dashboard
   - Exercise recommendation engine
   - Workout program templates

3. **Scalability improvements**
   - Add caching for configurations
   - Optimize BigQuery batch uploads
   - Add background job queue for large uploads

4. **Integration opportunities**
   - Export data from fitness apps (Strava, MyFitnessPal)
   - Connect to Google Sheets for data entry
   - API for programmatic uploads