# Quickstart Guide: Workout Analytics Views & BigQuery Enhancements

**Feature**: 002-workout-analytics-views  
**Date**: 2025-11-18  
**For**: Developers implementing this feature

## Overview

This guide walks you through implementing the workout analytics feature in the correct order, from database setup to UI deployment.

---

## Prerequisites

✅ **Before starting, ensure you have**:
- Existing Streamlit workout uploader application (app.py, modules/)
- Google Cloud BigQuery project with workouts table
- Python 3.11+ environment
- Access to modify BigQuery datasets

---

## Implementation Phases

### Phase 1: BigQuery Schema Extensions (1-2 hours)

#### 1.1 Create Exercise Mapping Table

**File**: `modules/bigquery_uploader.py` (extend existing class)

**Add method**:
```python
def upload_exercise_mapping(self, mapping_config: Dict) -> bool:
    """Upload exercise-to-muscle mapping to BigQuery."""
    # Parse YAML config into DataFrame
    mapping_data = self._parse_exercise_mapping(mapping_config)
    
    # Define table schema
    schema = [
        bigquery.SchemaField("exercise_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("muscle_group_level1", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("muscle_group_level2", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("is_compound", "BOOLEAN"),
        bigquery.SchemaField("mapping_source", "STRING"),
        bigquery.SchemaField("last_updated", "TIMESTAMP")
    ]
    
    # Upload with WRITE_TRUNCATE
    table_id = f"{self.project_id}.{self.dataset_id}.exercise_muscle_mapping"
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition="WRITE_TRUNCATE"
    )
    
    job = self.client.load_table_from_dataframe(
        mapping_data, table_id, job_config=job_config
    )
    job.result()  # Wait for completion
    return True
```

**Test**:
```bash
pytest tests/test_bigquery_uploader.py::test_upload_exercise_mapping
```

---

#### 1.2 Create SQL View Definitions

**Directory**: Create `sql/views/`

**Files to create**:
1. `sql/views/workout_frequency_by_muscle_group.sql`
2. `sql/views/workout_frequency_by_exercise.sql`
3. `sql/views/exercise_performance_metrics.sql`

**Example** (`workout_frequency_by_muscle_group.sql`):
```sql
CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.workout_frequency_by_muscle_group` AS
WITH workout_dates AS (
  SELECT DISTINCT
    DATE(datetime) as workout_date,
    muscle_group_level1,
    muscle_group_level2
  FROM `{project_id}.{dataset_id}.workouts`
),
date_gaps AS (
  SELECT
    muscle_group_level1,
    muscle_group_level2,
    workout_date,
    DATE_DIFF(
      workout_date,
      LAG(workout_date) OVER (
        PARTITION BY muscle_group_level1, muscle_group_level2 
        ORDER BY workout_date
      ),
      DAY
    ) as days_since_last_workout
  FROM workout_dates
)
SELECT
  muscle_group_level1,
  muscle_group_level2,
  COUNT(DISTINCT workout_date) as total_workouts,
  MIN(workout_date) as first_workout_date,
  MAX(workout_date) as last_workout_date,
  AVG(days_since_last_workout) as avg_rest_days,
  MIN(days_since_last_workout) as min_rest_days,
  MAX(days_since_last_workout) as max_rest_days
FROM date_gaps
WHERE days_since_last_workout IS NOT NULL AND days_since_last_workout > 0
GROUP BY muscle_group_level1, muscle_group_level2;
```

*Copy full SQL from data-model.md for other views*

---

### Phase 2: View Management Module (2 hours)

**File**: Create `modules/bigquery_views.py`

**Core functionality**:
```python
"""BigQuery view management for workout analytics."""
from google.cloud import bigquery
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class BigQueryViewManager:
    """Manage BigQuery analytical views."""
    
    def __init__(self, client: bigquery.Client, project_id: str, dataset_id: str):
        self.client = client
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.sql_dir = Path("sql/views")
    
    def load_view_sql(self, view_name: str) -> str:
        """Load SQL definition from file."""
        sql_file = self.sql_dir / f"{view_name}.sql"
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        # Replace template variables
        sql = sql.replace('{project_id}', self.project_id)
        sql = sql.replace('{dataset_id}', self.dataset_id)
        return sql
    
    def create_or_update_view(self, view_name: str) -> bool:
        """Create or replace a BigQuery view."""
        try:
            sql = self.load_view_sql(view_name)
            self.client.query(sql).result()
            logger.info(f"View '{view_name}' created/updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create view '{view_name}': {e}")
            return False
    
    def refresh_all_views(self, view_names: List[str]) -> Dict[str, bool]:
        """Refresh all analytical views."""
        results = {}
        for view_name in view_names:
            results[view_name] = self.create_or_update_view(view_name)
        return results
```

**Test**:
```bash
pytest tests/test_bigquery_views.py::test_create_view
pytest tests/test_bigquery_views.py::test_refresh_all_views
```

---

### Phase 3: Analytics Module (3 hours)

**File**: Create `modules/analytics.py`

**Key functions**:
```python
"""Analytics calculations and data queries."""
import pandas as pd
from google.cloud import bigquery
from typing import Literal, Optional

TimePeriod = Literal['all', 'last_7', 'last_14', 'last_30', 'last_90']


def get_time_filter(period: TimePeriod) -> str:
    """Get SQL date filter for time period."""
    filters = {
        'all': '',
        'last_7': 'AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)',
        'last_14': 'AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)',
        'last_30': 'AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)',
        'last_90': 'AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)'
    }
    return filters.get(period, '')


def get_rest_days_by_muscle_group(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    time_period: TimePeriod = 'all'
) -> pd.DataFrame:
    """Query rest days analysis by muscle group."""
    time_filter = get_time_filter(time_period)
    
    query = f"""
    SELECT 
        muscle_group_level1,
        muscle_group_level2,
        avg_rest_days,
        min_rest_days,
        max_rest_days,
        total_workouts,
        last_workout_date
    FROM `{project_id}.{dataset_id}.workout_frequency_by_muscle_group`
    WHERE 1=1 {time_filter}
    ORDER BY avg_rest_days ASC
    """
    
    return client.query(query).to_dataframe()


def get_exercise_performance(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    exercise_name: str,
    time_period: TimePeriod = 'all'
) -> pd.DataFrame:
    """Get performance metrics for a specific exercise."""
    time_filter = get_time_filter(time_period)
    
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.exercise_performance_metrics`
    WHERE exercise_name = @exercise_name
    {time_filter}
    ORDER BY workout_date
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("exercise_name", "STRING", exercise_name)
        ]
    )
    
    return client.query(query, job_config=job_config).to_dataframe()
```

**Test**:
```bash
pytest tests/test_analytics.py
```

---

### Phase 4: Visualization Module (2 hours)

**File**: Create `modules/visualizations.py`

**Core function**:
```python
"""Plotly visualization generators for workout analytics."""
import plotly.graph_objects as go
import pandas as pd
from typing import Literal

KPI = Literal['1rm', 'total_volume', 'max_weight']
XAxis = Literal['index', 'week', 'month', 'year']


def create_exercise_performance_chart(
    df: pd.DataFrame,
    exercise_name: str,
    kpi: KPI,
    x_axis: XAxis,
    show_trend: bool = False
) -> go.Figure:
    """Create interactive performance chart."""
    
    # Map KPI to column and label
    kpi_mapping = {
        '1rm': ('estimated_1rm', '1RM (Estimated)', 'pct_change_1rm'),
        'total_volume': ('total_volume', 'Total Volume (kg)', 'pct_change_volume'),
        'max_weight': ('max_weight', 'Max Weight (kg)', None)
    }
    
    kpi_col, kpi_label, pct_col = kpi_mapping[kpi]
    
    # Map x-axis to column
    x_mapping = {
        'index': ('session_index', 'Session #'),
        'week': ('week_number', 'Week'),
        'month': ('month_number', 'Month'),
        'year': ('year', 'Year')
    }
    
    x_col, x_label = x_mapping[x_axis]
    
    # Create figure
    fig = go.Figure()
    
    # Add bar chart
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[kpi_col],
        name=kpi_label,
        marker_color='lightblue',
        hovertemplate=f'<b>{x_label}: %{{x}}</b><br>{kpi_label}: %{{y:.1f}} kg<extra></extra>'
    ))
    
    # Add trend line if requested
    if show_trend and pct_col and pct_col in df.columns:
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[pct_col],
            name='% Change',
            mode='lines+markers',
            yaxis='y2',
            line=dict(color='green', width=2),
            hovertemplate=f'<b>Change: %{{y:+.1f}}%</b><extra></extra>'
        ))
    
    # Layout
    fig.update_layout(
        title=f'{exercise_name} - {kpi_label} Over Time',
        xaxis_title=x_label,
        yaxis_title=kpi_label,
        yaxis2=dict(
            title='% Change',
            overlaying='y',
            side='right',
            showgrid=False
        ) if show_trend else None,
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    return fig
```

**Test**:
```bash
pytest tests/test_visualizations.py
```

---

### Phase 5: Analytics Page (3-4 hours)

**File**: Create `pages/Analytics.py`

**Structure**:
```python
"""Analytics dashboard page for workout data."""
import streamlit as st
import pandas as pd
from modules.config_loader import ConfigLoader
from modules.bigquery_uploader import BigQueryUploader
from modules.analytics import (
    get_rest_days_by_muscle_group,
    get_rest_days_by_exercise,
    get_exercise_performance
)
from modules.visualizations import create_exercise_performance_chart

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

# Initialize clients
@st.cache_resource
def init_bigquery():
    config_loader = ConfigLoader()
    bq_config = config_loader.get_bigquery_config()
    uploader = BigQueryUploader(bq_config)
    uploader.initialize_client()
    return uploader.client, bq_config

try:
    client, config = init_bigquery()
except Exception as e:
    st.error(f"Failed to connect to BigQuery: {e}")
    st.stop()

# Page header
st.title("📊 Workout Analytics")
st.markdown("Track your training frequency and exercise performance over time")
st.markdown("---")

# Time period selector (global)
time_period = st.selectbox(
    "Time Period",
    options=['all', 'last_7', 'last_14', 'last_30', 'last_90'],
    format_func=lambda x: {
        'all': 'All Time',
        'last_7': 'Last 7 Days',
        'last_14': 'Last 14 Days',
        'last_30': 'Last 30 Days',
        'last_90': 'Last 90 Days'
    }[x],
    index=0
)

# Tabs
tab1, tab2 = st.tabs(["📋 Summary", "📈 Exercise Performance"])

with tab1:
    st.header("Rest Days Analysis")
    
    # Category type selector
    category_type = st.radio(
        "View by",
        options=['muscle_group', 'exercise'],
        format_func=lambda x: 'Muscle Groups' if x == 'muscle_group' else 'Exercises',
        horizontal=True
    )
    
    # Query data
    @st.cache_data(ttl=300)
    def load_rest_days(cat_type, period):
        if cat_type == 'muscle_group':
            return get_rest_days_by_muscle_group(
                client, config['connection']['project_id'],
                config['connection']['dataset_id'], period
            )
        else:
            return get_rest_days_by_exercise(
                client, config['connection']['project_id'],
                config['connection']['dataset_id'], period
            )
    
    df = load_rest_days(category_type, time_period)
    
    if df.empty:
        st.info("No data available for the selected period.")
    else:
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Avg Rest Days", f"{df['avg_rest_days'].mean():.1f}")
        with col2:
            most_freq = df.iloc[0]['muscle_group_level2' if category_type == 'muscle_group' else 'exercise_name']
            st.metric("Most Trained", most_freq)
        with col3:
            least_freq = df.iloc[-1]['muscle_group_level2' if category_type == 'muscle_group' else 'exercise_name']
            st.metric("Needs Attention", least_freq, delta_color="inverse")
        
        # Display table
        st.dataframe(df, use_container_width=True)

with tab2:
    st.header("Exercise Performance Tracking")
    
    # Get available exercises
    @st.cache_data(ttl=300)
    def get_exercises():
        query = f"""
        SELECT DISTINCT exercise_name 
        FROM `{config['connection']['project_id']}.{config['connection']['dataset_id']}.workouts`
        ORDER BY exercise_name
        """
        return client.query(query).to_dataframe()['exercise_name'].tolist()
    
    exercises = get_exercises()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        exercise = st.selectbox("Exercise", exercises)
    with col2:
        kpi = st.selectbox("KPI", ['1rm', 'total_volume', 'max_weight'],
                          format_func=lambda x: {
                              '1rm': '1RM (Estimated)',
                              'total_volume': 'Total Volume',
                              'max_weight': 'Max Weight'
                          }[x])
    with col3:
        x_axis = st.selectbox("X-Axis", ['index', 'week', 'month', 'year'],
                             format_func=lambda x: x.capitalize())
    with col4:
        show_trend = st.checkbox("Show % Change", value=False)
    
    # Load and display chart
    @st.cache_data(ttl=300)
    def load_performance(ex, period):
        return get_exercise_performance(
            client, config['connection']['project_id'],
            config['connection']['dataset_id'], ex, period
        )
    
    perf_df = load_performance(exercise, time_period)
    
    if perf_df.empty:
        st.info(f"No data available for {exercise}")
    else:
        fig = create_exercise_performance_chart(
            perf_df, exercise, kpi, x_axis, show_trend
        )
        st.plotly_chart(fig, use_container_width=True)
```

---

### Phase 6: Integration & Configuration (1 hour)

#### 6.1 Update requirements

**File**: `requirements.yaml`

**Add**:
```yaml
plotly>=5.0.0
```

**Install**:
```bash
pip install plotly
```

---

#### 6.2 Update BigQuery config

**File**: `config/bigquery_config.yaml`

**Add section**:
```yaml
views:
  enabled: true
  dataset_id: "workout_data"
  view_definitions:
    - name: "workout_frequency_by_muscle_group"
      sql_file: "sql/views/workout_frequency_by_muscle_group.sql"
    - name: "workout_frequency_by_exercise"
      sql_file: "sql/views/workout_frequency_by_exercise.sql"
    - name: "exercise_performance_metrics"
      sql_file: "sql/views/exercise_performance_metrics.sql"
  refresh_on_upload: true
```

---

#### 6.3 Update upload workflow

**File**: `app.py` (upload tab)

**Modify upload success handler**:
```python
# After successful data upload
if upload_successful:
    # Upload exercise mapping
    mapping_config = config_loader.get_exercise_mapping()
    uploader.upload_exercise_mapping(mapping_config)
    
    # Refresh views
    from modules.bigquery_views import BigQueryViewManager
    view_manager = BigQueryViewManager(
        uploader.client,
        config['connection']['project_id'],
        config['connection']['dataset_id']
    )
    
    view_names = [v['name'] for v in config['views']['view_definitions']]
    results = view_manager.refresh_all_views(view_names)
    
    # Show success message
    st.success(f"""
    ✅ Upload successful!
    - Uploaded {len(df)} workout records
    - Updated exercise mapping table
    - Refreshed {sum(results.values())}/{len(results)} analytical views
    """)
```

---

## Testing Checklist

**Unit Tests**:
- [ ] `test_bigquery_uploader.py::test_upload_exercise_mapping`
- [ ] `test_bigquery_views.py::test_create_view`
- [ ] `test_bigquery_views.py::test_refresh_all_views`
- [ ] `test_analytics.py::test_get_rest_days`
- [ ] `test_analytics.py::test_get_exercise_performance`
- [ ] `test_visualizations.py::test_create_chart`

**Integration Tests**:
- [ ] Upload CSV → Verify mapping table created
- [ ] Upload CSV → Verify views refreshed
- [ ] Navigate to Analytics page → Data loads
- [ ] Change time period → Metrics update
- [ ] Select exercise → Chart displays
- [ ] Toggle trend line → Chart updates

**Manual Testing**:
- [ ] Test with empty database (no data state)
- [ ] Test with single workout (insufficient data)
- [ ] Test with various time periods
- [ ] Test all KPI options
- [ ] Test all x-axis options
- [ ] Verify chart interactivity (hover, zoom)

---

## Deployment

**1. Commit all files**:
```bash
git add .
git commit -m "feat: Add workout analytics views and BigQuery enhancements"
```

**2. Run full test suite**:
```bash
pytest tests/ -v
```

**3. Deploy to Streamlit Cloud**:
- Push to main branch
- Streamlit Cloud auto-deploys
- Verify Analytics page appears in navigation

**4. Verify BigQuery setup**:
- Check `exercise_muscle_mapping` table exists
- Check views are created
- Run sample queries to verify data

---

## Troubleshooting

**Views not refreshing**:
- Check `config/bigquery_config.yaml` has `views` section
- Verify SQL files exist in `sql/views/`
- Check BigQuery permissions (bigquery.tables.create)

**Analytics page shows no data**:
- Verify workout data exists in BigQuery
- Check time period filter (try 'all')
- Check browser console for errors

**Chart not displaying**:
- Verify Plotly installed (`pip install plotly`)
- Check DataFrame has required columns
- Verify exercise name exists in data

---

## Time Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | BigQuery schema | 1-2 hours |
| Phase 2 | View management | 2 hours |
| Phase 3 | Analytics module | 3 hours |
| Phase 4 | Visualizations | 2 hours |
| Phase 5 | Analytics page | 3-4 hours |
| Phase 6 | Integration | 1 hour |
| **Total** | | **12-14 hours** |

---

## Next Steps

After implementation:
1. Monitor BigQuery query costs
2. Gather user feedback on analytics
3. Consider adding more KPIs (training intensity, volume trends)
4. Optimize view queries if performance issues arise
