# Research: Workout Analytics Views & BigQuery Enhancements

**Feature**: 002-workout-analytics-views  
**Date**: 2025-11-18  
**Phase**: Phase 0 - Research & Technology Decisions

## Research Areas

### 1. BigQuery View Management Strategy

**Question**: How should BigQuery views be created, updated, and maintained programmatically?

**Decision**: Use BigQuery DDL (CREATE OR REPLACE VIEW) statements executed via the google-cloud-bigquery Python client

**Rationale**:
- BigQuery supports CREATE OR REPLACE VIEW which is idempotent - safe to run multiple times
- Views are lightweight and don't incur storage costs (unlike materialized views)
- View definitions can be version-controlled as SQL files
- Python client provides `client.query()` method to execute DDL statements
- No need for complex migration frameworks for simple view management

**Alternatives Considered**:
- **Materialized Views**: Rejected because they incur storage costs and add complexity. Regular views are sufficient for this scale (personal tracking, <50k records)
- **dbt (data build tool)**: Rejected as overkill for this project. Adds significant dependency overhead for managing just 4-5 views
- **Manual Console Updates**: Rejected because it breaks automation and version control

**Implementation Pattern**:
```python
# modules/bigquery_views.py
def create_or_update_view(client, view_sql, view_id):
    query = f"CREATE OR REPLACE VIEW `{view_id}` AS {view_sql}"
    client.query(query).result()
```

---

### 2. Streamlit Multi-Page Navigation

**Question**: What's the best pattern for adding a new Analytics page to the existing Streamlit application?

**Decision**: Use Streamlit's native multi-page apps feature with `pages/` directory structure

**Rationale**:
- Streamlit 1.10+ supports automatic multi-page routing via `pages/` directory
- Files in `pages/` appear automatically in sidebar navigation
- Maintains separation of concerns (upload logic vs analytics logic)
- No need for custom routing or session state management
- Existing `app.py` can remain as the main upload page

**Alternatives Considered**:
- **Tab-based single page**: Rejected because analytics page is complex enough to warrant separate page, and tabs are used within the analytics page for sub-views
- **Custom routing with st.session_state**: Rejected because Streamlit's native multi-page feature is simpler and more maintainable

**Implementation Pattern**:
```
app.py              # Existing upload page (becomes Home page)
pages/
  Analytics.py      # New analytics page (appears as "Analytics" in sidebar)
```

---

### 3. Visualization Library Choice

**Question**: Which library should be used for interactive workout analytics visualizations?

**Decision**: Use Plotly for all visualizations

**Rationale**:
- Streamlit has native `st.plotly_chart()` support with full interactivity
- Plotly provides:
  - Interactive hover tooltips (ideal for showing workout details)
  - Zoom and pan capabilities for time-series data
  - Easy bar charts, line charts, and combination charts
  - Responsive design works well in Streamlit's layout
- Already widely used in data analytics applications
- Good documentation and community support

**Alternatives Considered**:
- **Altair**: Rejected because Plotly has better interactivity and more chart customization options
- **Matplotlib/Seaborn**: Rejected because they produce static images; lack the interactivity needed for exploring workout data
- **Streamlit native charts**: Rejected because they're too basic for the KPI selection and multi-axis requirements

**Implementation Pattern**:
```python
import plotly.graph_objects as go
import plotly.express as px

# modules/visualizations.py
def create_exercise_performance_chart(df, kpi='1rm', show_trend=False):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['date'], y=df[kpi], name=kpi))
    if show_trend:
        fig.add_trace(go.Scatter(x=df['date'], y=df['pct_change'], 
                                  name='% Change', yaxis='y2'))
    return fig
```

---

### 4. Rest Days Calculation Approach

**Question**: How should "average days between workouts" be calculated for muscle groups and exercises?

**Decision**: Calculate as average of consecutive workout gaps (pairwise differences)

**Rationale**:
- More intuitive than total span / count approach
- Better reflects actual rest patterns
- Handles irregular training schedules correctly
- Example: Workouts on days [1, 3, 10, 12] → gaps [2, 7, 2] → avg = 3.67 days

**Calculation Logic**:
```python
# For a muscle group or exercise:
# 1. Get all workout dates (sorted)
# 2. Calculate differences between consecutive dates
# 3. Exclude zero-day gaps (same-day workouts)
# 4. Return mean of gaps

gaps = df['date'].sort_values().diff().dt.days.dropna()
gaps = gaps[gaps > 0]  # Exclude same-day
avg_rest_days = gaps.mean()
```

**Edge Cases Handled**:
- Single workout: Return "N/A" (can't calculate rest days)
- Same-day workouts: Treated as single data point for gap calculation
- Missing data periods: Included in calculation (reflects actual training gaps)

---

### 5. Time Period Filtering Strategy

**Question**: How should time period filters (last 7/14/30/90 days, all-time) be implemented efficiently?

**Decision**: Pre-filter data in BigQuery queries using WHERE clauses with date parameters

**Rationale**:
- BigQuery is optimized for date filtering (partition pruning)
- Reduces data transfer from BigQuery to Streamlit
- Faster than filtering in Python after loading all data
- Consistent with BigQuery best practices

**Implementation Pattern**:
```python
# modules/analytics.py
def get_rest_days_analysis(client, table_id, period='all'):
    date_filter = {
        'last_7': "AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)",
        'last_14': "AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)",
        'last_30': "AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)",
        'last_90': "AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)",
        'all': ""
    }[period]
    
    query = f"""
        SELECT muscle_group, AVG(rest_days) as avg_rest
        FROM `{table_id}`
        WHERE 1=1 {date_filter}
        GROUP BY muscle_group
    """
    return client.query(query).to_dataframe()
```

---

### 6. Exercise Mapping Table Schema

**Question**: What schema should the `exercise_muscle_mapping` table use in BigQuery?

**Decision**:
```sql
CREATE TABLE exercise_muscle_mapping (
  exercise_name STRING NOT NULL,
  muscle_group_level1 STRING NOT NULL,
  muscle_group_level2 STRING NOT NULL,
  is_compound BOOLEAN,
  mapping_source STRING,  -- 'config' or 'fuzzy' or 'default'
  last_updated TIMESTAMP
)
```

**Rationale**:
- Mirrors the YAML config structure for consistency
- `exercise_name` as primary key (unique exercises)
- `mapping_source` tracks how the mapping was derived (useful for data quality)
- `last_updated` enables tracking config changes over time
- Simple flat schema (no complex relationships needed)

**Upload Strategy**:
- Parse `config/exercise_mapping.yaml` on each data upload
- Truncate and reload the table (WRITE_TRUNCATE) since it's a reference table
- Alternative: Use WRITE_APPEND with deduplication, but truncate is simpler for config-driven data

---

### 7. 1RM (One-Rep Max) Calculation

**Question**: How should 1RM be estimated from workout data (weight + reps)?

**Decision**: Use the Brzycki formula: 1RM = weight × (36 / (37 - reps))

**Rationale**:
- Widely accepted formula in strength training
- Accurate for rep ranges 1-10 (most common in workout data)
- Simple to implement and understand
- Alternative formulas (Epley, Lander) produce similar results

**Limitations & Handling**:
- Invalid for reps > 36: Return `None` or use max(weight) as fallback
- Best used for compound exercises (bench, squat, deadlift)
- Document in UI that 1RM is an estimate

**Implementation**:
```python
def calculate_1rm(weight, reps):
    if reps >= 36 or reps < 1:
        return None
    return weight * (36 / (37 - reps))
```

---

### 8. BigQuery View Refresh Timing

**Question**: When should BigQuery views be refreshed after data upload?

**Decision**: Execute view refresh immediately after successful workout data upload, before returning success to user

**Rationale**:
- Views in BigQuery are not materialized - they're just query definitions
- Creating/replacing views is near-instantaneous (DDL operation, not data operation)
- No actual data is recomputed until views are queried
- Sequential execution ensures views are always in sync with data

**Error Handling**:
- If view refresh fails, log warning but don't fail the upload
- Upload success depends on data upload only
- Views can be manually refreshed later if needed

**Implementation Flow**:
```python
# In modules/bigquery_uploader.py
def upload_dataframe(self, df):
    # 1. Upload workout data
    job = self.client.load_table_from_dataframe(df, table_id)
    job.result()  # Wait for completion
    
    # 2. Upload exercise mapping
    self.upload_exercise_mapping()
    
    # 3. Refresh views
    try:
        view_manager.refresh_all_views(self.client)
    except Exception as e:
        logger.warning(f"View refresh failed: {e}")
    
    return {'status': 'success', 'rows': len(df)}
```

---

## Summary of Key Decisions

| Area | Decision | Primary Benefit |
|------|----------|----------------|
| View Management | CREATE OR REPLACE VIEW via Python client | Simple, idempotent, version-controlled |
| Page Navigation | Streamlit native multi-page (pages/ dir) | Automatic routing, clean separation |
| Visualization | Plotly | Interactive, Streamlit native support |
| Rest Days Calc | Pairwise consecutive gaps average | Intuitive, handles irregular schedules |
| Time Filtering | BigQuery WHERE clauses | Efficient, reduces data transfer |
| Mapping Table | Flat schema matching YAML structure | Simple, consistent with config |
| 1RM Estimation | Brzycki formula | Industry standard, accurate 1-10 reps |
| View Refresh | Immediate after upload, non-blocking | Always synchronized, fails gracefully |

---

## Dependencies to Add

**New Python packages**:
- `plotly>=5.0.0` - Interactive visualizations

**No changes needed**:
- Existing dependencies cover all other requirements (pandas, google-cloud-bigquery, streamlit)

---

## No Outstanding Clarifications

All technology choices and implementation patterns are determined. Proceeding to Phase 1 (Design).
