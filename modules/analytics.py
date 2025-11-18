"""Analytics module for workout data analysis."""
import pandas as pd
import streamlit as st
from google.cloud import bigquery
from typing import Optional, Dict, Any


class WorkoutAnalytics:
    """Analytics functions for workout data stored in BigQuery."""
    
    def __init__(self, client: bigquery.Client, project_id: str, dataset_id: str):
        """Initialize analytics with BigQuery client.
        
        Args:
            client: BigQuery client instance
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        self.client = client
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = "workouts"
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_workout_overview(_self) -> Dict[str, Any]:
        """Get overview statistics of all workouts.
        
        Returns:
            Dictionary with overview metrics
        """
        query = f"""
        SELECT 
            COUNT(DISTINCT DATE(date)) as total_workouts,
            COUNT(*) as total_exercises,
            SUM(weight_kg * reps) as total_volume_kg,
            COUNT(DISTINCT exercise_name) as unique_exercises
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        """
        
        try:
            result = _self.client.query(query).result()
            row = next(result)
            
            return {
                'total_workouts': row.total_workouts or 0,
                'total_exercises': row.total_exercises or 0,
                'total_volume_kg': row.total_volume_kg or 0,
                'unique_exercises': row.unique_exercises or 0
            }
        except Exception as e:
            st.error(f"Error fetching workout overview: {e}")
            return {
                'total_workouts': 0,
                'total_exercises': 0,
                'total_volume_kg': 0,
                'unique_exercises': 0
            }
    
    @st.cache_data(ttl=300)
    def get_workout_frequency_by_date(_self) -> pd.DataFrame:
        """Get workout frequency by date.
        
        Returns:
            DataFrame with date and workout_count columns
        """
        query = f"""
        SELECT 
            DATE(date) as date,
            COUNT(DISTINCT workout_name) as workout_count
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        GROUP BY date
        ORDER BY date
        """
        
        try:
            return _self.client.query(query).to_dataframe()
        except Exception as e:
            st.error(f"Error fetching workout frequency: {e}")
            return pd.DataFrame(columns=['date', 'workout_count'])
    
    @st.cache_data(ttl=300)
    def get_muscle_group_distribution(_self) -> pd.DataFrame:
        """Get distribution of exercises by muscle group.
        
        Returns:
            DataFrame with muscle_group, level, and exercise_count
        """
        query = f"""
        SELECT 'level1' as level, muscle_group_level1 as muscle_group, COUNT(*) as exercise_count
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        GROUP BY muscle_group_level1
        
        UNION ALL
        
        SELECT 'level2' as level, muscle_group_level2 as muscle_group, COUNT(*) as exercise_count
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        GROUP BY muscle_group_level2
        
        ORDER BY level, exercise_count DESC
        """
        
        try:
            return _self.client.query(query).to_dataframe()
        except Exception as e:
            st.error(f"Error fetching muscle group distribution: {e}")
            return pd.DataFrame(columns=['level', 'muscle_group', 'exercise_count'])
    
    @st.cache_data(ttl=300)
    def get_top_exercises(_self, limit: int = 10) -> pd.DataFrame:
        """Get most performed exercises.
        
        Args:
            limit: Maximum number of exercises to return
            
        Returns:
            DataFrame with exercise statistics
        """
        query = f"""
        SELECT 
            exercise_name,
            COUNT(*) as total_sets,
            AVG(weight_kg) as avg_weight,
            MAX(weight_kg) as max_weight,
            SUM(weight_kg * reps) as total_volume
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        GROUP BY exercise_name
        ORDER BY total_sets DESC
        LIMIT {limit}
        """
        
        try:
            return _self.client.query(query).to_dataframe()
        except Exception as e:
            st.error(f"Error fetching top exercises: {e}")
            return pd.DataFrame(columns=['exercise_name', 'total_sets', 'avg_weight', 'max_weight', 'total_volume'])
    
    @st.cache_data(ttl=300)
    def get_all_exercises(_self) -> pd.DataFrame:
        """Get list of all unique exercises.
        
        Returns:
            DataFrame with exercise names
        """
        query = f"""
        SELECT DISTINCT exercise_name
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        ORDER BY exercise_name
        """
        
        try:
            return _self.client.query(query).to_dataframe()
        except Exception as e:
            st.error(f"Error fetching exercises: {e}")
            return pd.DataFrame(columns=['exercise_name'])
    
    @st.cache_data(ttl=300)
    def get_exercise_performance(_self, exercise_name: str) -> pd.DataFrame:
        """Get performance data for a specific exercise over time.
        
        Args:
            exercise_name: Name of the exercise
            
        Returns:
            DataFrame with performance metrics by date
        """
        query = f"""
        SELECT 
            DATE(date) as date,
            MAX(weight_kg) as max_weight,
            AVG(weight_kg) as avg_weight,
            SUM(weight_kg * reps) as total_volume,
            COUNT(*) as total_sets
        FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
        WHERE exercise_name = @exercise_name
        GROUP BY date
        ORDER BY date
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("exercise_name", "STRING", exercise_name)
            ]
        )
        
        try:
            return _self.client.query(query, job_config=job_config).to_dataframe()
        except Exception as e:
            st.error(f"Error fetching exercise performance for {exercise_name}: {e}")
            return pd.DataFrame(columns=['date', 'max_weight', 'avg_weight', 'total_volume', 'total_sets'])
    
    @st.cache_data(ttl=300)
    def get_rest_days(_self, days: int = 30) -> pd.DataFrame:
        """Get rest days analysis for the last N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            DataFrame with rest day information
        """
        query = f"""
        WITH date_series AS (
            SELECT DATE_SUB(CURRENT_DATE(), INTERVAL day DAY) as date
            FROM UNNEST(GENERATE_ARRAY(0, {days - 1})) as day
        ),
        workout_dates AS (
            SELECT DISTINCT DATE(date) as date
            FROM `{_self.project_id}.{_self.dataset_id}.{_self.table_id}`
            WHERE DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
        )
        SELECT 
            ds.date,
            CASE WHEN wd.date IS NOT NULL THEN 'Workout' ELSE 'Rest' END as day_type
        FROM date_series ds
        LEFT JOIN workout_dates wd ON ds.date = wd.date
        ORDER BY ds.date DESC
        """
        
        try:
            return _self.client.query(query).to_dataframe()
        except Exception as e:
            st.error(f"Error fetching rest days: {e}")
            return pd.DataFrame(columns=['date', 'day_type'])
    
    def check_table_exists(_self) -> bool:
        """Check if the workouts table exists and has data.
        
        Returns:
            True if table exists and has data, False otherwise
        """
        try:
            table_ref = f"{_self.project_id}.{_self.dataset_id}.{_self.table_id}"
            table = _self.client.get_table(table_ref)
            return table.num_rows > 0
        except Exception:
            return False