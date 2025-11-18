# SQL Views Documentation

This directory contains BigQuery view definitions for workout analytics.

## Views

### workout_frequency_by_muscle_group.sql
Pre-computes rest day metrics grouped by muscle group (Level 1 and Level 2).

**Output Columns:**
- `muscle_group_level1`: Primary muscle category (upper/lower/core/full_body)
- `muscle_group_level2`: Specific muscle (chest/back/quads/etc.)
- `total_workouts`: Total number of workout sessions
- `first_workout_date`: Earliest workout date
- `last_workout_date`: Most recent workout date
- `avg_rest_days`: Average days between workouts
- `min_rest_days`: Minimum rest period
- `max_rest_days`: Maximum rest period

### workout_frequency_by_exercise.sql
Pre-computes rest day metrics grouped by specific exercise.

**Output Columns:**
- `exercise_name`: Exercise name
- `total_workouts`: Total number of workout sessions
- `first_workout_date`: Earliest workout date
- `last_workout_date`: Most recent workout date
- `avg_rest_days`: Average days between workouts
- `min_rest_days`: Minimum rest period
- `max_rest_days`: Maximum rest period

### exercise_performance_metrics.sql
Pre-computes performance KPIs for each exercise over time.

**Output Columns:**
- `exercise_name`: Exercise name
- `workout_date`: Date of workout session
- `week_number`: Week number (for time grouping)
- `month_number`: Month number (for time grouping)
- `year`: Year (for time grouping)
- `session_index`: Sequential session number per exercise
- `max_weight`: Maximum weight lifted in session
- `total_volume`: Total volume (weight × reps)
- `estimated_1rm`: Estimated one-rep max (using Brzycki formula)
- `pct_change_1rm`: Percentage change in 1RM from previous session
- `pct_change_volume`: Percentage change in volume from previous session

## Usage

These views are automatically created and refreshed by the `BigQueryViewManager` class after each data upload.

The SQL files use template placeholders:
- `{project_id}`: GCP project ID
- `{dataset_id}`: BigQuery dataset ID
- `{table_id}`: Table name (default: `workouts`)

These placeholders are substituted at runtime by the view manager.

## Maintenance

When adding new views:
1. Create a new `.sql` file in this directory
2. Update `config/bigquery_config.yaml` to include the new view definition
3. The view will be automatically created on the next data upload
