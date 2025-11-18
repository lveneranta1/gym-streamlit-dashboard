-- Workout Frequency by Exercise View
-- Pre-computes rest day metrics grouped by specific exercises

WITH workout_dates AS (
  SELECT DISTINCT
    DATE(date) as workout_date,
    exercise_name
  FROM `{project_id}.{dataset_id}.{table_id}`
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
