-- Exercise Performance Metrics View
-- Pre-computes performance KPIs for each exercise over time

WITH exercise_sessions AS (
  SELECT
    DATE(date) as workout_date,
    EXTRACT(WEEK FROM date) as week_number,
    EXTRACT(MONTH FROM date) as month_number,
    EXTRACT(YEAR FROM date) as year,
    exercise_name,
    MAX(weight_kg) as max_weight,
    SUM(weight_kg * reps) as total_volume,
    -- Estimated 1RM using Brzycki formula
    MAX(
      CASE 
        WHEN reps < 36 AND reps >= 1 
        THEN weight_kg * (36.0 / (37.0 - reps))
        ELSE weight_kg
      END
    ) as estimated_1rm
  FROM `{project_id}.{dataset_id}.{table_id}`
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
