"""Unit tests for BigQuery view management."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from modules.bigquery_views import BigQueryViewManager


def test_bigquery_view_manager_init():
    """Test BigQueryViewManager initialization."""
    mock_client = Mock()
    manager = BigQueryViewManager(mock_client, 'test-project', 'test-dataset')
    
    assert manager.client == mock_client
    assert manager.project_id == 'test-project'
    assert manager.dataset_id == 'test-dataset'
    assert manager.sql_dir == Path('sql/views')


def test_load_view_sql():
    """Test loading view SQL from file."""
    mock_client = Mock()
    manager = BigQueryViewManager(mock_client, 'test-project', 'test-dataset')
    
    # This will work if SQL files exist
    try:
        sql = manager.load_view_sql('workout_frequency_by_muscle_group', 'workouts')
        assert 'test-project' in sql
        assert 'test-dataset' in sql
        assert 'workouts' in sql
    except FileNotFoundError:
        pytest.skip("SQL file not found")


def test_create_or_update_view():
    """Test creating/updating a view."""
    mock_client = Mock()
    mock_query_job = Mock()
    mock_client.query.return_value = mock_query_job
    
    manager = BigQueryViewManager(mock_client, 'test-project', 'test-dataset')
    
    # Mock the load_view_sql method
    with patch.object(manager, 'load_view_sql', return_value='SELECT 1'):
        result = manager.create_or_update_view('test_view')
        
        assert result is True
        mock_client.query.assert_called_once()


def test_refresh_all_views():
    """Test refreshing all views."""
    mock_client = Mock()
    manager = BigQueryViewManager(mock_client, 'test-project', 'test-dataset')
    
    view_configs = [
        {'name': 'view1', 'sql_file': 'view1.sql'},
        {'name': 'view2', 'sql_file': 'view2.sql'}
    ]
    
    # Mock create_or_update_view
    with patch.object(manager, 'create_or_update_view', return_value=True):
        results = manager.refresh_all_views(view_configs)
        
        assert len(results) == 2
        assert results['view1'] is True
        assert results['view2'] is True
