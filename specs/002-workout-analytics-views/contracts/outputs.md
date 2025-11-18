# Output Contracts: Workout Analytics Views & BigQuery Enhancements

**Feature**: 002-workout-analytics-views  
**Date**: 2025-11-18

## Overview

This document defines the output contracts for the workout analytics feature - what the system produces and returns to users and downstream components.

---

## 1. BigQuery Tables (Created/Updated)

### 1.1 `exercise_muscle_mapping` Table

**Output After**: Data upload completion  
**Update Frequency**: Every data upload  
**Write Mode**: WRITE_TRUNCATE (full table replacement)

**Schema**:
```sql
exercise_name: STRING
muscle_group_level1: STRING  -- 'upper'/'lower'/'core'/'full_body'
muscle_group_level2: STRING  -- 'chest'/'back'/'quads'/etc.
is_compound: BOOLEAN
mapping_source: STRING       -- 'config'/'fuzzy'/'default'
last_updated: TIMESTAMP
```

**Sample Output**:
| exercise_name | muscle_group_level1 | muscle_group_level2 | is_compound | mapping_source | last_updated |
|--------------|-------------------|-------------------|------------|---------------|-------------|
| Bench Press | upper | chest | true | config | 2025-11-18T10:00:00Z |
| Squat | lower | quads | true | config | 2025-11-18T10:00:00Z |

**Row Count**: 50-200 (matches number of configured exercise mappings)

---

### 1.2 BigQuery Views (Created/Updated)

**Output After**: View refresh (post-upload)  
**Update Frequency**: Every data upload  
**Access Pattern**: Queryable via SELECT statements

Views created:
- `workout_frequency_by_muscle_group`
- `workout_frequency_by_exercise`
- `exercise_performance_metrics`

*Schema detailed in data-model.md*

---

## 2. Analytics Page Output (UI)

### 2.1 Summary Tab - Rest Days Table

**Component**: Streamlit dataframe display  
**Update Trigger**: Time period or category type change

**Output Format** (DataFrame):
```python
pd.DataFrame({
    'Category': [str, ...],              # Muscle group or exercise name
    'Avg Rest Days': [float, ...],       # Formatted to 1 decimal
    'Min Rest Days': [int, ...],
    'Max Rest Days': [int, ...],
    'Total Workouts': [int, ...],
    'Last Workout': [date, ...]          # Formatted as 'YYYY-MM-DD'
})
```

**Sample Display**:
| Category | Avg Rest Days | Min Rest Days | Max Rest Days | Total Workouts | Last Workout |
|----------|--------------|--------------|--------------|---------------|-------------|
| Chest | 3.2 | 1 | 7 | 24 | 2025-11-15 |
| Back | 2.8 | 1 | 5 | 28 | 2025-11-17 |
| Legs | 4.1 | 2 | 10 | 18 | 2025-11-16 |

**Sorting**: By 'Avg Rest Days' ascending (most frequent training first)

**Empty State**: 
```
ℹ️ No data available for the selected time period and category.
Try selecting a different time range or upload more workout data.
```

---

### 2.2 Summary Tab - Overall Metrics Cards

**Component**: Streamlit metrics  
**Update Trigger**: Time period change

**Output Format** (3 columns):

**Column 1 - Overall Average Rest Days**:
```python
st.metric(
    label="Overall Avg Rest Days",
    value=f"{avg_rest_days:.1f} days",
    delta=f"{delta_vs_all_time:+.1f} vs all-time"  # If time period != 'all'
)
```

**Column 2 - Most Trained Category**:
```python
st.metric(
    label="Most Trained",
    value="Chest",
    delta=f"{count} workouts"
)
```

**Column 3 - Least Trained Category**:
```python
st.metric(
    label="Needs Attention",
    value="Legs",
    delta=f"{count} workouts",
    delta_color="inverse"  # Red color to indicate low frequency
)
```

---

### 2.3 Visualization Tab - Exercise Performance Chart

**Component**: Plotly chart via st.plotly_chart()  
**Update Trigger**: Exercise, KPI, X-axis, or trend toggle change

**Output Format** (Plotly Figure):

**Chart Type**: Bar chart with optional line overlay

**Primary Y-Axis** (Left):
- **Data**: Selected KPI values (1RM / Total Volume / Max Weight)
- **Bar Color**: Blue gradient based on value
- **Hover Template**:
  ```
  Date: {workout_date}
  {kpi_label}: {value:.1f} kg
  Session: #{session_index}
  ```

**Secondary Y-Axis** (Right) - If `show_trend=True`:
- **Data**: Percentage change from previous session
- **Line Color**: Green (positive) / Red (negative)
- **Hover Template**:
  ```
  Change: {pct_change:+.1f}%
  ```

**Chart Layout**:
```python
{
    'title': f'{exercise_name} - {kpi_label} Over Time',
    'xaxis': {'title': x_axis_label},
    'yaxis': {'title': kpi_label},
    'yaxis2': {'title': '% Change', 'overlaying': 'y', 'side': 'right'},
    'hovermode': 'x unified',
    'height': 500
}
```

**Sample Output**:
```
[Bar Chart]
Title: Bench Press - 1RM (Estimated) Over Time
X-Axis: Week Number (1, 2, 3, ...)
Y-Axis (Left): 1RM (kg) - 80, 85, 87, 90...
Y-Axis (Right): % Change - +6.3%, +2.4%, +3.4%...
[Line overlay showing trend]
```

**Empty State**:
```
ℹ️ No performance data available for {exercise_name}.
This exercise may not have enough recorded sessions.
```

---

### 2.4 Visualization Tab - Exercise Selector

**Component**: Streamlit selectbox  
**Output**: Dropdown menu with all available exercises

**Data Source**: 
```sql
SELECT DISTINCT exercise_name 
FROM workouts 
ORDER BY exercise_name
```

**Format**:
```python
exercises = ['Bench Press', 'Squat', 'Deadlift', ...]  # Sorted alphabetically
selected_exercise = st.selectbox('Select Exercise', exercises)
```

---

## 3. Module Function Outputs

### 3.1 `modules/analytics.py`

#### `get_rest_days_by_muscle_group(client, table_id, time_period) -> pd.DataFrame`

**Returns**:
```python
pd.DataFrame({
    'muscle_group_level1': str,
    'muscle_group_level2': str,
    'avg_rest_days': float,
    'min_rest_days': int,
    'max_rest_days': int,
    'total_workouts': int,
    'last_workout_date': date
})
```

**Row Count**: 10-30 (one per muscle group with data)

---

#### `get_rest_days_by_exercise(client, table_id, time_period) -> pd.DataFrame`

**Returns**:
```python
pd.DataFrame({
    'exercise_name': str,
    'avg_rest_days': float,
    'min_rest_days': int,
    'max_rest_days': int,
    'total_workouts': int,
    'last_workout_date': date
})
```

**Row Count**: 50-200 (one per exercise with data)

---

#### `get_exercise_performance(client, exercise_name, x_axis, time_period) -> pd.DataFrame`

**Returns**:
```python
pd.DataFrame({
    'workout_date': date,
    'session_index': int,
    'week_number': int,
    'month_number': int,
    'year': int,
    'max_weight': float,
    'total_volume': float,
    'estimated_1rm': float,
    'pct_change_1rm': Optional[float],
    'pct_change_volume': Optional[float]
})
```

**Row Count**: Varies by exercise (10-500 sessions)

---

### 3.2 `modules/bigquery_views.py`

#### `refresh_all_views(client, config) -> Dict[str, bool]`

**Returns**:
```python
{
    'workout_frequency_by_muscle_group': True,  # Success
    'workout_frequency_by_exercise': True,
    'exercise_performance_metrics': True
}
```

**Success**: All values `True`  
**Partial Failure**: Some values `False` (with logged errors)  
**Complete Failure**: Raises exception

---

#### `create_or_update_view(client, view_name, sql_definition) -> bool`

**Returns**: `True` if successful, `False` otherwise

**Side Effect**: View created/updated in BigQuery

---

### 3.3 `modules/visualizations.py`

#### `create_exercise_performance_chart(df, kpi, x_axis, show_trend) -> go.Figure`

**Returns**: Plotly Figure object ready for `st.plotly_chart()`

**Figure Structure**:
```python
go.Figure(
    data=[
        go.Bar(...),              # Primary KPI bars
        go.Scatter(...)           # Trend line (if show_trend=True)
    ],
    layout=go.Layout(...)
)
```

---

## 4. Upload Pipeline Output

### 4.1 Enhanced Upload Success Message

**Output After**: Successful data upload + view refresh

**Format** (Streamlit success message):
```python
st.success(f"""
✅ Upload successful!
- Uploaded {num_rows} workout records
- Updated exercise mapping table ({num_exercises} exercises)
- Refreshed {num_views} analytical views
- Data available in Analytics page
""")
```

**Failure Scenarios**:

**Upload succeeded, view refresh failed**:
```python
st.warning(f"""
⚠️ Upload completed with warnings
- Uploaded {num_rows} workout records
- Updated exercise mapping table
- View refresh failed: {error_message}
- Analytics may show stale data until views are refreshed
""")
```

---

## 5. Logging Output

### 5.1 View Refresh Logs

**Output To**: Console / log file  
**Format**: Structured logging

**Success Log**:
```
INFO [bigquery_views] View 'workout_frequency_by_muscle_group' created/updated successfully
INFO [bigquery_views] View 'workout_frequency_by_exercise' created/updated successfully
INFO [bigquery_views] View 'exercise_performance_metrics' created/updated successfully
INFO [bigquery_views] All views refreshed successfully in 2.3s
```

**Failure Log**:
```
ERROR [bigquery_views] Failed to create view 'workout_frequency_by_muscle_group': 
      Syntax error at line 15: Expected ")" but got "FROM"
WARNING [bigquery_views] View refresh completed with 1 error
```

---

### 5.2 Exercise Mapping Upload Logs

**Success Log**:
```
INFO [bigquery_uploader] Loaded 127 exercise mappings from config
INFO [bigquery_uploader] Uploaded exercise_muscle_mapping table (127 rows)
```

**Failure Log**:
```
ERROR [bigquery_uploader] Failed to upload exercise_muscle_mapping: 
      Permission denied: bigquery.tables.create
```

---

## 6. Error Outputs

### 6.1 BigQuery Query Errors

**Output**: Streamlit error message

**Format**:
```python
st.error(f"""
❌ Failed to load analytics data

Error: {error_type}
Details: {error_message}

Please check:
- BigQuery connection is configured
- Views exist in dataset
- You have query permissions
""")
```

---

### 6.2 No Data Available

**Output**: Streamlit info message

**Format**:
```python
st.info("""
ℹ️ No workout data available

Get started by:
1. Go to the Upload Data tab
2. Upload a CSV file with your workout history
3. Return here to view analytics
""")
```

---

## 7. Performance Metrics

**Logged for Monitoring**:

```python
{
    'query_execution_time': float,      # seconds
    'rows_returned': int,
    'cache_hit': bool,
    'bigquery_bytes_processed': int,
    'chart_render_time': float          # seconds
}
```

**Target Performance**:
- Query execution: <1s
- Chart rendering: <0.5s
- Page load (total): <2s
- View refresh: <30s

---

## Output Validation

All outputs validated for:
1. **Type Safety**: Correct dtypes (float, int, date, str)
2. **Null Handling**: NULL values displayed as "-" or "N/A"
3. **Format Consistency**: Dates as YYYY-MM-DD, floats to 1-2 decimals
4. **Sort Order**: Consistent sorting (most frequent first, alphabetical)
5. **Empty States**: Graceful messages when no data available
