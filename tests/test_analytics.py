"""Unit tests for analytics module."""
import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock
from modules.analytics import (
    get_time_filter,
    get_rest_days_by_muscle_group,
    get_rest_days_by_exercise,
    get_available_exercises,
    get_exercise_performance
)


def test_get_time_filter():
    """Test time filter SQL generation."""
    assert get_time_filter('all') == ''
    assert 'INTERVAL 7 DAY' in get_time_filter('last_7')
    assert 'INTERVAL 14 DAY' in get_time_filter('last_14')
    assert 'INTERVAL 30 DAY' in get_time_filter('last_30')
    assert 'INTERVAL 90 DAY' in get_time_filter('last_90')


def test_get_rest_days_by_muscle_group():
    """Test muscle group rest days query."""
    mock_client = Mock()
    mock_result = Mock()
    
    # Mock query result
    mock_df = pd.DataFrame({
        'muscle_group_level1': ['upper', 'lower'],
        'muscle_group_level2': ['chest', 'quads'],
        'total_workouts': [10, 8],
        'avg_rest_days': [3.5, 4.2]
    })
    mock_result.to_dataframe.return_value = mock_df
    mock_client.query.return_value = mock_result
    
    df = get_rest_days_by_muscle_group(mock_client, 'project', 'dataset', 'all')
    
    assert not df.empty
    assert len(df) == 2
    assert 'muscle_group_level1' in df.columns


def test_get_rest_days_by_exercise():
    """Test exercise rest days query."""
    mock_client = Mock()
    mock_result = Mock()
    
    # Mock query result
    mock_df = pd.DataFrame({
        'exercise_name': ['Bench Press', 'Squat'],
        'total_workouts': [15, 12],
        'avg_rest_days': [2.5, 3.0]
    })
    mock_result.to_dataframe.return_value = mock_df
    mock_client.query.return_value = mock_result
    
    df = get_rest_days_by_exercise(mock_client, 'project', 'dataset', 'all')
    
    assert not df.empty
    assert len(df) == 2
    assert 'exercise_name' in df.columns


def test_get_available_exercises():
    """Test available exercises query."""
    mock_client = Mock()
    mock_result = Mock()
    
    # Mock query result
    mock_df = pd.DataFrame({
        'exercise_name': ['Bench Press', 'Squat', 'Deadlift']
    })
    mock_result.to_dataframe.return_value = mock_df
    mock_client.query.return_value = mock_result
    
    exercises = get_available_exercises(mock_client, 'project', 'dataset')
    
    assert len(exercises) == 3
    assert 'Bench Press' in exercises


def test_get_exercise_performance():
    """Test exercise performance query."""
    mock_client = Mock()
    mock_result = Mock()
    
    # Mock query result
    mock_df = pd.DataFrame({
        'exercise_name': ['Bench Press'] * 5,
        'workout_date': pd.date_range('2025-01-01', periods=5),
        'estimated_1rm': [100, 105, 102, 108, 110],
        'total_volume': [5000, 5200, 5100, 5400, 5500]
    })
    mock_result.to_dataframe.return_value = mock_df
    mock_client.query.return_value = mock_result
    
    df = get_exercise_performance(mock_client, 'project', 'dataset', 'Bench Press', 'all')
    
    assert not df.empty
    assert len(df) == 5
    assert 'estimated_1rm' in df.columns
