-- KPI Workouts Table Query
-- This query generates workout KPIs across different time periods
-- Columns: type, kpi, date, metric, value
--
-- Types: workouts (workout visits related)
-- KPIs: visits, legs, push, pull, upper, lower, rest_days
-- Date Periods: 7D, 14D, 30D, 2MO, 3MO, 6MO, 1Y
-- Metrics: count, average, total, min, max

WITH 
time_periods AS (
  SELECT '7D' as period, DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) as start_date UNION ALL
  SELECT '14D', DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY) UNION ALL
  SELECT '30D', DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) UNION ALL
  SELECT '2MO', DATE_SUB(CURRENT_DATE(), INTERVAL 2 MONTH) UNION ALL
  SELECT '3MO', DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH) UNION ALL
  SELECT '6MO', DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH) UNION ALL
  SELECT '1Y', DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
),

enriched_workouts AS (
  SELECT 
    w.*,
    COALESCE(e.muscle_group_level1, 'unknown') as muscle_group_level1,
    COALESCE(e.muscle_group_level2, 'unknown') as muscle_group_level2,
    e.muscle_group_level3,
    e.is_compound
  FROM `streamlit-dashboard-venleevi.workout_data.workouts` w
  LEFT JOIN `streamlit-dashboard-venleevi.workout_data.exercise_muscle_mapping` e
    ON TRIM(LOWER(w.exercise_name)) = TRIM(LOWER(e.exercise_name))
),

-- Daily workout aggregations by date and muscle group
daily_workouts AS (
  SELECT 
    DATE(date) as workout_date,
    CASE 
      WHEN muscle_group_level2 = 'legs' THEN 'legs'
      WHEN muscle_group_level2 = 'push' THEN 'push'
      WHEN muscle_group_level2 = 'pull' THEN 'pull'
      WHEN muscle_group_level1 = 'upper' THEN 'upper'
      WHEN muscle_group_level1 = 'lower' THEN 'lower'
      ELSE 'other'
    END as workout_category,
    COUNT(*) as exercise_count,
    SUM(weight_kg * reps) as total_volume
  FROM enriched_workouts
  GROUP BY workout_date, workout_category
),

-- KPI: Total workout visits (unique workout days)
visits_kpi AS (
  SELECT 
    'workouts' as type,
    'visits' as kpi,
    tp.period as date,
    'count' as metric,
    CAST(COUNT(DISTINCT dw.workout_date) AS FLOAT64) as value
  FROM time_periods tp
  CROSS JOIN daily_workouts dw
  WHERE dw.workout_date >= tp.start_date
  GROUP BY tp.period
),

-- KPI: Rest days
rest_days_kpi AS (
  SELECT 
    'workouts' as type,
    'rest_days' as kpi,
    tp.period as date,
    'count' as metric,
    CAST(DATE_DIFF(CURRENT_DATE(), tp.start_date, DAY) - COUNT(DISTINCT dw.workout_date) AS FLOAT64) as value
  FROM time_periods tp
  CROSS JOIN daily_workouts dw
  WHERE dw.workout_date >= tp.start_date
  GROUP BY tp.period, tp.start_date
),

-- KPI: Muscle group specific workouts - count of workout days
muscle_group_count AS (
  SELECT 
    'workouts' as type,
    dw.workout_category as kpi,
    tp.period as date,
    'count' as metric,
    CAST(COUNT(DISTINCT dw.workout_date) AS FLOAT64) as value
  FROM time_periods tp
  CROSS JOIN daily_workouts dw
  WHERE dw.workout_date >= tp.start_date
    AND dw.workout_category IN ('legs', 'push', 'pull', 'upper', 'lower')
  GROUP BY tp.period, dw.workout_category
),

-- KPI: Average number of exercises per workout
muscle_group_avg_exercises AS (
  SELECT 
    'workouts' as type,
    dw.workout_category as kpi,
    tp.period as date,
    'average' as metric,
    ROUND(AVG(dw.exercise_count), 2) as value
  FROM time_periods tp
  CROSS JOIN daily_workouts dw
  WHERE dw.workout_date >= tp.start_date
    AND dw.workout_category IN ('legs', 'push', 'pull', 'upper', 'lower')
  GROUP BY tp.period, dw.workout_category
),

-- KPI: Total volume (weight * reps) for muscle group
muscle_group_total_volume AS (
  SELECT 
    'workouts' as type,
    dw.workout_category as kpi,
    tp.period as date,
    'total' as metric,
    CAST(ROUND(SUM(dw.total_volume), 2) AS FLOAT64) as value
  FROM time_periods tp
  CROSS JOIN daily_workouts dw
  WHERE dw.workout_date >= tp.start_date
    AND dw.workout_category IN ('legs', 'push', 'pull', 'upper', 'lower')
  GROUP BY tp.period, dw.workout_category
),

-- KPI: Minimum exercises in a single workout
muscle_group_min_exercises AS (
  SELECT 
    'workouts' as type,
    dw.workout_category as kpi,
    tp.period as date,
    'min' as metric,
    CAST(MIN(dw.exercise_count) AS FLOAT64) as value
  FROM time_periods tp
  CROSS JOIN daily_workouts dw
  WHERE dw.workout_date >= tp.start_date
    AND dw.workout_category IN ('legs', 'push', 'pull', 'upper', 'lower')
  GROUP BY tp.period, dw.workout_category
),

-- KPI: Maximum exercises in a single workout
muscle_group_max_exercises AS (
  SELECT 
    'workouts' as type,
    dw.workout_category as kpi,
    tp.period as date,
    'max' as metric,
    CAST(MAX(dw.exercise_count) AS FLOAT64) as value
  FROM time_periods tp
  CROSS JOIN daily_workouts dw
  WHERE dw.workout_date >= tp.start_date
    AND dw.workout_category IN ('legs', 'push', 'pull', 'upper', 'lower')
  GROUP BY tp.period, dw.workout_category
)

-- Combine all KPIs
SELECT * FROM visits_kpi
UNION ALL SELECT * FROM rest_days_kpi
UNION ALL SELECT * FROM muscle_group_count
UNION ALL SELECT * FROM muscle_group_avg_exercises
UNION ALL SELECT * FROM muscle_group_total_volume
UNION ALL SELECT * FROM muscle_group_min_exercises
UNION ALL SELECT * FROM muscle_group_max_exercises

ORDER BY 
  kpi,
  CASE metric
    WHEN 'count' THEN 1
    WHEN 'average' THEN 2
    WHEN 'total' THEN 3
    WHEN 'min' THEN 4
    WHEN 'max' THEN 5
  END,
  CASE date
    WHEN '7D' THEN 1
    WHEN '14D' THEN 2
    WHEN '30D' THEN 3
    WHEN '2MO' THEN 4
    WHEN '3MO' THEN 5
    WHEN '6MO' THEN 6
    WHEN '1Y' THEN 7
  END;
