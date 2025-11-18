# Input Contracts: Workout Analytics Views & BigQuery Enhancements

**Feature**: 002-workout-analytics-views  
**Date**: 2025-11-18

## Overview

This document defines the input data contracts for the workout analytics feature - what data the system requires and expects from external sources and user interactions.

---

## 1. Exercise Mapping Configuration (YAML)

**Source**: `config/exercise_mapping.yaml` (existing file)  
**Consumer**: `modules/bigquery_uploader.py` → BigQuery `exercise_muscle_mapping` table

**Contract**:
```yaml
exercises:
  - names: [string, ...]           # List of exercise name variations
    level1: string                 # Primary muscle category
    level2: string                 # Specific muscle
    compound: boolean              # Optional, default false
```

**Required Fields**:
- `exercises` (array): At least one exercise mapping
- `names` (array of strings): At least one name per exercise
- `level1` (string): Must be one of: upper, lower, core, full_body
- `level2` (string): Must be valid muscle name (chest, back, quads, etc.)

**Validation Rules**:
- Exercise names are case-insensitive
- Duplicate names across different mappings = error
- Empty names array = error
- Invalid level1/level2 values = error

**Example**:
```yaml
exercises:
  - names: ["bench press", "barbell bench press"]
    level1: upper
    level2: chest
    compound: true
```

---

## 2. BigQuery Configuration

**Source**: `config/bigquery_config.yaml` (existing file, to be extended)  
**Consumer**: `modules/bigquery_views.py`

**New Configuration Section**:
```yaml
views:
  enabled: true
  dataset_id: "workout_data"      # Dataset for views
  view_definitions:
    - name: "workout_frequency_by_muscle_group"
      sql_file: "sql/views/workout_frequency_by_muscle_group.sql"
    - name: "workout_frequency_by_exercise"
      sql_file: "sql/views/workout_frequency_by_exercise.sql"
    - name: "exercise_performance_metrics"
      sql_file: "sql/views/exercise_performance_metrics.sql"
  refresh_on_upload: true          # Auto-refresh after data upload
```

**Required Fields**:
- `views.enabled` (boolean): Enable/disable view management
- `views.dataset_id` (string): BigQuery dataset for views
- `views.view_definitions` (array): List of view specs
  - `name` (string): View name in BigQuery
  - `sql_file` (string): Path to SQL definition file

**Validation Rules**:
- All sql_file paths must exist
- View names must be valid BigQuery identifiers
- dataset_id must match existing dataset

---

## 3. User Input: Analytics Page Filters

### 3.1 Time Period Selection

**UI Component**: Streamlit selectbox  
**Consumer**: `modules/analytics.py` query functions

**Contract**:
```python
time_period: Literal['all', 'last_7', 'last_14', 'last_30', 'last_90']
```

**Validation**:
- Must be one of the allowed literal values
- Invalid value → default to 'all'

**Mapping to SQL**:
```python
{
    'all': '',  # No date filter
    'last_7': 'AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)',
    'last_14': 'AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)',
    'last_30': 'AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)',
    'last_90': 'AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)'
}
```

---

### 3.2 Category Type Selection (Summary View)

**UI Component**: Streamlit radio buttons  
**Consumer**: `modules/analytics.py` rest days analysis

**Contract**:
```python
category_type: Literal['muscle_group', 'exercise']
```

**Behavior**:
- `'muscle_group'`: Query `workout_frequency_by_muscle_group` view
- `'exercise'`: Query `workout_frequency_by_exercise` view

---

### 3.3 Exercise Selection (Visualization View)

**UI Component**: Streamlit selectbox  
**Consumer**: `modules/visualizations.py` chart generators

**Contract**:
```python
exercise_name: str  # Must be an exercise that exists in workout data
```

**Validation**:
- Must match existing exercise_name in BigQuery workouts table
- Invalid/non-existent exercise → display error message
- Dynamically populated from: `SELECT DISTINCT exercise_name FROM workouts`

---

### 3.4 KPI Selection (Visualization View)

**UI Component**: Streamlit selectbox  
**Consumer**: `modules/visualizations.py`

**Contract**:
```python
kpi: Literal['1rm', 'total_volume', 'max_weight']
```

**Field Mapping**:
- `'1rm'` → `estimated_1rm` column from view
- `'total_volume'` → `total_volume` column
- `'max_weight'` → `max_weight` column

**Display Labels**:
```python
{
    '1rm': '1RM (Estimated)',
    'total_volume': 'Total Volume (kg)',
    'max_weight': 'Max Weight (kg)'
}
```

---

### 3.5 X-Axis Selection (Visualization View)

**UI Component**: Streamlit selectbox  
**Consumer**: `modules/visualizations.py`

**Contract**:
```python
x_axis: Literal['index', 'week', 'month', 'year']
```

**Field Mapping**:
```python
{
    'index': 'session_index',      # Sequential workout number
    'week': 'week_number',          # Week number (1-52)
    'month': 'month_number',        # Month (1-12)
    'year': 'year'                  # Year (e.g., 2025)
}
```

**Aggregation Behavior**:
- `'index'`: No aggregation (one bar per session)
- `'week'/'month'/'year'`: Aggregate by grouping (e.g., max 1RM per month)

---

### 3.6 Trend Line Toggle (Visualization View)

**UI Component**: Streamlit checkbox  
**Consumer**: `modules/visualizations.py`

**Contract**:
```python
show_trend: bool
```

**Behavior**:
- `True`: Add percentage change line chart overlay on secondary y-axis
- `False`: Show only bar chart

**Data Source**:
- Percentage change values come from `pct_change_1rm` or `pct_change_volume` columns (depending on selected KPI)

---

## 4. BigQuery View Query Results

**Source**: BigQuery views  
**Consumer**: `modules/analytics.py` and Streamlit pages

### 4.1 `workout_frequency_by_muscle_group` View Output

**Schema**:
```python
{
    'muscle_group_level1': str,
    'muscle_group_level2': str,
    'total_workouts': int,
    'first_workout_date': date,
    'last_workout_date': date,
    'avg_rest_days': float,
    'min_rest_days': int,
    'max_rest_days': int
}
```

**Constraints**:
- `avg_rest_days`: Can be NULL if only one workout exists
- `min_rest_days` / `max_rest_days`: NULL if insufficient data
- All dates in DATE format (not TIMESTAMP)

---

### 4.2 `workout_frequency_by_exercise` View Output

**Schema**:
```python
{
    'exercise_name': str,
    'total_workouts': int,
    'first_workout_date': date,
    'last_workout_date': date,
    'avg_rest_days': float,
    'min_rest_days': int,
    'max_rest_days': int
}
```

**Same constraints as muscle group view**

---

### 4.3 `exercise_performance_metrics` View Output

**Schema**:
```python
{
    'exercise_name': str,
    'workout_date': date,
    'week_number': int,
    'month_number': int,
    'year': int,
    'session_index': int,
    'max_weight': float,
    'total_volume': float,
    'estimated_1rm': float,
    'pct_change_1rm': Optional[float],      # NULL for first session
    'pct_change_volume': Optional[float]    # NULL for first session
}
```

**Constraints**:
- `estimated_1rm`: NULL if reps >= 36 or invalid
- `pct_change_*`: NULL for first session of each exercise
- `session_index`: Starts at 1 for each exercise

---

## 5. Environment Variables

**Required for BigQuery Operations**:

```bash
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

**Validation**:
- Must be set before running analytics queries
- Missing variables → graceful error message
- Invalid credentials → BigQuery authentication error

---

## 6. SQL View Definition Files

**Location**: `sql/views/*.sql`  
**Consumer**: `modules/bigquery_views.py`

**File Contract**:
- Must be valid BigQuery SQL
- Must use standard SQL syntax (not legacy)
- Must reference existing tables/views
- View name should match filename

**Example File**: `sql/views/workout_frequency_by_muscle_group.sql`
```sql
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.workout_frequency_by_muscle_group` AS
-- SQL query here
SELECT ...
```

**Template Variables** (injected at runtime):
- `{project_id}`: From config
- `{dataset_id}`: From config

---

## Input Validation Summary

| Input | Validator | Error Handling |
|-------|-----------|---------------|
| Exercise mapping YAML | ConfigLoader | Raise exception with details |
| Time period selection | Type checking | Default to 'all' |
| Exercise name | BigQuery query | Show "Exercise not found" |
| KPI selection | Type checking | Default to '1rm' |
| X-axis selection | Type checking | Default to 'index' |
| BigQuery credentials | google.auth | Show setup instructions |
| SQL view files | File existence | Raise FileNotFoundError |

---

## Error Messages

**Invalid Exercise Selection**:
```
Error: Exercise "X" not found in workout data.
Please select a different exercise or upload more data.
```

**Missing Configuration**:
```
Error: BigQuery views not configured.
Please check config/bigquery_config.yaml and ensure 'views' section is present.
```

**Insufficient Data**:
```
Warning: Not enough data to calculate rest days for "X".
At least 2 workout sessions are required.
```

**BigQuery Connection Failed**:
```
Error: Unable to connect to BigQuery.
Please verify GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS in your .env file.
```
