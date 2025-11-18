# Data Model: Workout Analytics Views & BigQuery Enhancements

**Feature**: 002-workout-analytics-views  
**Date**: 2025-11-18  
**Phase**: Phase 1 - Design

## Overview

This document defines the data structures, BigQuery schema extensions, and analytical views required for the workout analytics feature.

---

## BigQuery Tables

### 1. `exercise_muscle_mapping` (NEW)

Reference table mapping exercises to muscle groups, uploaded from `config/exercise_mapping.yaml`.

**Schema**:
```sql
CREATE TABLE exercise_muscle_mapping (
  exercise_name STRING NOT NULL,           -- Exercise name (e.g., "Bench Press")
  muscle_group_level1 STRING NOT NULL,     -- Primary category: upper/lower/core/full_body
  muscle_group_level2 STRING NOT NULL,     -- Specific muscle: chest/back/quads/etc.
  is_compound BOOLEAN,                     -- True for compound movements
  mapping_source STRING,                   -- 'config'/'fuzzy'/'default'
  last_updated TIMESTAMP                   -- When mapping was last updated
)
```

**Purpose**: Provides muscle group classifications for analytical queries without duplicating data in the workouts table.

**Update Strategy**: WRITE_TRUNCATE (replace entire table on each upload)

**Sample Data**:
| exercise_name | muscle_group_level1 | muscle_group_level2 | is_compound | mapping_source | last_updated |
|--------------|-------------------|-------------------|------------|---------------|-------------|
| Bench Press | upper | chest | true | config | 2025-11-18 10:00:00 |
| Squat | lower | quads | true | config | 2025-11-18 10:00:00 |
| Bicep Curl | upper | biceps | false | config | 2025-11-18 10:00:00 |

---

### 2. `workouts` (EXISTING)

Main workout data table (already exists, no schema changes required).

**Relevant Columns** (for this feature):
- `datetime` (TIMESTAMP) - Workout date/time
- `exercise_name` (STRING) - Exercise performed
- `weight` (FLOAT) - Weight used
- `reps` (INTEGER) - Repetitions performed
- `sets` (INTEGER) - Number of sets
- `muscle_group_level1` (STRING) - Already enriched during upload
- `muscle_group_level2` (STRING) - Already enriched during upload

---

## BigQuery Views

### 1. `workout_frequency_by_muscle_group` (NEW)

Pre-computes workout frequency metrics grouped by muscle group.

**View Definition**:
```sql
CREATE OR REPLACE VIEW `workout_frequency_by_muscle_group` AS
WITH workout_dates AS (
  SELECT DISTINCT
    DATE(datetime) as workout_date,
    muscle_group_level1,
    muscle_group_level2
  FROM workouts
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
GROUP BY muscle_group_level1, muscle_group_level2
```

**Output Columns**:
- `muscle_group_level1` - Primary muscle category
- `muscle_group_level2` - Specific muscle
- `total_workouts` - Total number of workout sessions
- `first_workout_date` - Earliest workout date
- `last_workout_date` - Most recent workout date
- `avg_rest_days` - Average days between workouts
- `min_rest_days` - Minimum rest period
- `max_rest_days` - Maximum rest period

---

### 2. `workout_frequency_by_exercise` (NEW)

Pre-computes workout frequency metrics grouped by specific exercise.

**View Definition**:
```sql
CREATE OR REPLACE VIEW `workout_frequency_by_exercise` AS
WITH workout_dates AS (
  SELECT DISTINCT
    DATE(datetime) as workout_date,
    exercise_name
  FROM workouts
),
date_gaps AS (
  SELECT
    exercise_name,
    workout_date,
    DATE_DIFF(
      workout_date,
      LAG(workout_date) OVER (
        PARTITION BY exercise_name 
        ORDER BY workout_date
      ),
      DAY
    ) as days_since_last_workout
  FROM workout_dates
)
SELECT
  exercise_name,
  COUNT(DISTINCT workout_date) as total_workouts,
  MIN(workout_date) as first_workout_date,
  MAX(workout_date) as last_workout_date,
  AVG(days_since_last_workout) as avg_rest_days,
  MIN(days_since_last_workout) as min_rest_days,
  MAX(days_since_last_workout) as max_rest_days
FROM date_gaps
WHERE days_since_last_workout IS NOT NULL AND days_since_last_workout > 0
GROUP BY exercise_name
```

**Output Columns**: Same as muscle group view but grouped by exercise_name

---

### 3. `exercise_performance_metrics` (NEW)

Pre-computes performance KPIs for each exercise over time.

**View Definition**:
```sql
CREATE OR REPLACE VIEW `exercise_performance_metrics` AS
WITH exercise_sessions AS (
  SELECT
    DATE(datetime) as workout_date,
    EXTRACT(WEEK FROM datetime) as week_number,
    EXTRACT(MONTH FROM datetime) as month_number,
    EXTRACT(YEAR FROM datetime) as year,
    exercise_name,
    MAX(weight) as max_weight,
    SUM(weight * reps * COALESCE(sets, 1)) as total_volume,
    -- Estimated 1RM using Brzycki formula
    MAX(
      CASE 
        WHEN reps < 36 AND reps >= 1 
        THEN weight * (36.0 / (37.0 - reps))
        ELSE weight
      END
    ) as estimated_1rm
  FROM workouts
  GROUP BY workout_date, week_number, month_number, year, exercise_name
),
indexed_sessions AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY exercise_name ORDER BY workout_date) as session_index
  FROM exercise_sessions
)
SELECT
  exercise_name,
  workout_date,
  week_number,
  month_number,
  year,
  session_index,
  max_weight,
  total_volume,
  estimated_1rm,
  -- Calculate percentage change from previous session
  ROUND(
    100.0 * (estimated_1rm - LAG(estimated_1rm) OVER (
      PARTITION BY exercise_name ORDER BY workout_date
    )) / NULLIF(LAG(estimated_1rm) OVER (
      PARTITION BY exercise_name ORDER BY workout_date
    ), 0),
    2
  ) as pct_change_1rm,
  ROUND(
    100.0 * (total_volume - LAG(total_volume) OVER (
      PARTITION BY exercise_name ORDER BY workout_date
    )) / NULLIF(LAG(total_volume) OVER (
      PARTITION BY exercise_name ORDER BY workout_date
    ), 0),
    2
  ) as pct_change_volume
FROM indexed_sessions
ORDER BY exercise_name, workout_date
```

**Output Columns**:
- `exercise_name` - Exercise name
- `workout_date` - Date of workout session
- `week_number` - Week number (for time grouping)
- `month_number` - Month number (for time grouping)
- `year` - Year (for time grouping)
- `session_index` - Sequential session number per exercise
- `max_weight` - Maximum weight lifted in session
- `total_volume` - Total volume (weight × reps × sets)
- `estimated_1rm` - Estimated one-rep max
- `pct_change_1rm` - Percentage change in 1RM from previous session
- `pct_change_volume` - Percentage change in volume from previous session

---

## Python Data Models

### RestDaysMetric

Represents rest day analysis for a muscle group or exercise.

**Structure**:
```python
@dataclass
class RestDaysMetric:
    category: str                    # Muscle group or exercise name
    category_type: str               # 'muscle_group' or 'exercise'
    avg_rest_days: float            # Average days between workouts
    min_rest_days: int              # Minimum rest period
    max_rest_days: int              # Maximum rest period
    total_workouts: int             # Total number of workouts
    time_period: str                # 'all', 'last_7', 'last_14', etc.
    first_workout_date: date
    last_workout_date: date
```

---

### ExercisePerformance

Represents performance data for a specific exercise.

**Structure**:
```python
@dataclass
class ExercisePerformance:
    exercise_name: str
    workout_date: date
    max_weight: float
    total_volume: float
    estimated_1rm: float
    pct_change_1rm: Optional[float]
    pct_change_volume: Optional[float]
    session_index: int
    week_number: int
    month_number: int
    year: int
```

---

### AnalyticsSummary

High-level summary metrics for the analytics dashboard.

**Structure**:
```python
@dataclass
class AnalyticsSummary:
    time_period: str                         # 'all', 'last_7', etc.
    overall_avg_rest_days: float            # Overall average rest
    most_frequent_muscle_group: str          # Most trained muscle group
    least_frequent_muscle_group: str         # Least trained muscle group
    total_unique_exercises: int              # Number of unique exercises
    total_workouts: int                      # Total workout sessions
    date_range: tuple[date, date]           # (first_date, last_date)
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Data Upload (modules/bigquery_uploader.py)                      │
│    - Upload workouts table                                          │
│    - Upload exercise_muscle_mapping table (from YAML config)        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. View Refresh (modules/bigquery_views.py)                        │
│    - Execute CREATE OR REPLACE VIEW statements                      │
│    - workout_frequency_by_muscle_group                              │
│    - workout_frequency_by_exercise                                  │
│    - exercise_performance_metrics                                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. Analytics Page Load (pages/Analytics.py)                        │
│    - Query views with time period filters                          │
│    - Transform to Python data models                                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Visualization (modules/visualizations.py)                       │
│    - Generate Plotly charts                                         │
│    - Display in Streamlit                                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Query Performance Considerations

1. **View Efficiency**: Views are not materialized, so queries execute against base tables. With <50k workout records, performance should be acceptable (<1s)

2. **Date Filtering**: Always include date filters in WHERE clauses to leverage BigQuery's date partitioning (if configured)

3. **Caching**: Streamlit's `@st.cache_data` decorator will cache query results to avoid redundant BigQuery calls during the same session

4. **Index Optimization**: Not needed at this scale; BigQuery automatically optimizes query execution

---

## Data Validation Rules

1. **Rest Days Calculation**:
   - Must have at least 2 workout dates to calculate average
   - Exclude gaps of 0 days (same-day workouts)
   - Handle NULL values from LAG() function (first workout in series)

2. **1RM Estimation**:
   - Only calculate for reps in range [1, 35]
   - Return NULL for invalid rep ranges
   - Use max(weight) as fallback for high-rep sets

3. **Time Period Filters**:
   - 'all': No date restriction
   - 'last_7': DATE >= CURRENT_DATE - 7
   - 'last_14': DATE >= CURRENT_DATE - 14
   - 'last_30': DATE >= CURRENT_DATE - 30
   - 'last_90': DATE >= CURRENT_DATE - 90

4. **Muscle Group Validation**:
   - All exercises must have valid muscle_group_level1 and level2
   - Unmapped exercises use 'unknown' category
   - Join with exercise_muscle_mapping table for enrichment

---

## Future Extensibility

- **Materialized Views**: If data grows beyond 100k records, consider materializing views for performance
- **Additional Metrics**: Easy to add new calculated fields to performance metrics view (e.g., velocity, intensity)
- **Historical Snapshots**: Could track view results over time for trend analysis
- **Per-User Partitioning**: When adding multi-user support, partition tables by user_id
