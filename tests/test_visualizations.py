"""Unit tests for visualization module."""
import pytest
import pandas as pd
import plotly.graph_objects as go
from modules.visualizations import create_exercise_performance_chart


def test_create_exercise_performance_chart_empty():
    """Test chart creation with empty dataframe."""
    df = pd.DataFrame()
    fig = create_exercise_performance_chart(df, '1rm', 'index', False)
    
    assert isinstance(fig, go.Figure)
    # Should have annotation for empty state
    assert len(fig.layout.annotations) > 0


def test_create_exercise_performance_chart_with_data():
    """Test chart creation with actual data."""
    df = pd.DataFrame({
        'exercise_name': ['Bench Press'] * 5,
        'workout_date': pd.date_range('2025-01-01', periods=5),
        'session_index': [1, 2, 3, 4, 5],
        'week_number': [1, 1, 2, 2, 3],
        'month_number': [1, 1, 1, 1, 1],
        'year': [2025] * 5,
        'estimated_1rm': [100, 105, 102, 108, 110],
        'total_volume': [5000, 5200, 5100, 5400, 5500],
        'max_weight': [80, 82, 81, 85, 87],
        'pct_change_1rm': [None, 5.0, -2.9, 5.9, 1.9],
        'pct_change_volume': [None, 4.0, -1.9, 5.9, 1.9]
    })
    
    fig = create_exercise_performance_chart(df, '1rm', 'index', False)
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1  # At least one trace
    assert fig.data[0].type == 'bar'


def test_create_exercise_performance_chart_with_trend():
    """Test chart creation with trend line."""
    df = pd.DataFrame({
        'exercise_name': ['Squat'] * 5,
        'workout_date': pd.date_range('2025-01-01', periods=5),
        'session_index': [1, 2, 3, 4, 5],
        'week_number': [1, 1, 2, 2, 3],
        'month_number': [1, 1, 1, 1, 1],
        'year': [2025] * 5,
        'estimated_1rm': [150, 155, 152, 160, 165],
        'total_volume': [8000, 8200, 8100, 8500, 8700],
        'max_weight': [120, 125, 123, 128, 130],
        'pct_change_1rm': [None, 3.3, -1.9, 5.3, 3.1],
        'pct_change_volume': [None, 2.5, -1.2, 4.9, 2.4]
    })
    
    fig = create_exercise_performance_chart(df, 'total_volume', 'week', True)
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 2  # Bar + trend line
    assert fig.data[0].type == 'bar'
    assert fig.data[1].type == 'scatter'


def test_create_exercise_performance_chart_different_kpis():
    """Test chart creation with different KPI options."""
    df = pd.DataFrame({
        'exercise_name': ['Deadlift'] * 3,
        'workout_date': pd.date_range('2025-01-01', periods=3),
        'session_index': [1, 2, 3],
        'week_number': [1, 2, 3],
        'month_number': [1, 1, 1],
        'year': [2025] * 3,
        'estimated_1rm': [200, 205, 210],
        'total_volume': [10000, 10500, 11000],
        'max_weight': [160, 165, 170],
        'pct_change_1rm': [None, 2.5, 2.4],
        'pct_change_volume': [None, 5.0, 4.8]
    })
    
    # Test each KPI
    for kpi in ['1rm', 'total_volume', 'max_weight']:
        fig = create_exercise_performance_chart(df, kpi, 'index', False)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1
