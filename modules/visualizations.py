"""Visualization module for workout analytics charts."""
import pandas as pd
import plotly.graph_objects as go
from typing import Literal, Optional

# Type definitions
KPI = Literal['1rm', 'total_volume', 'max_weight']
XAxis = Literal['index', 'week', 'month', 'year']


def create_exercise_performance_chart(
    df: pd.DataFrame,
    kpi: KPI = '1rm',
    x_axis: XAxis = 'index',
    show_trend: bool = False
) -> go.Figure:
    """Create interactive exercise performance chart.
    
    Args:
        df: DataFrame from exercise_performance_metrics view
        kpi: KPI to display (1rm, total_volume, max_weight)
        x_axis: X-axis grouping (index, week, month, year)
        show_trend: Whether to show percentage change trend line
        
    Returns:
        Plotly Figure object
    """
    if df.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for this exercise",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Map KPI to column names
    kpi_columns = {
        '1rm': 'estimated_1rm',
        'total_volume': 'total_volume',
        'max_weight': 'max_weight'
    }
    
    kpi_labels = {
        '1rm': 'Estimated 1RM (kg)',
        'total_volume': 'Total Volume (kg)',
        'max_weight': 'Max Weight (kg)'
    }
    
    pct_change_columns = {
        '1rm': 'pct_change_1rm',
        'total_volume': 'pct_change_volume',
        'max_weight': 'pct_change_1rm'  # Use 1RM change as proxy for max weight
    }
    
    # Map x-axis to column names
    x_axis_columns = {
        'index': 'session_index',
        'week': 'week_number',
        'month': 'month_number',
        'year': 'year'
    }
    
    x_axis_labels = {
        'index': 'Session Number',
        'week': 'Week Number',
        'month': 'Month',
        'year': 'Year'
    }
    
    kpi_col = kpi_columns[kpi]
    x_col = x_axis_columns[x_axis]
    kpi_label = kpi_labels[kpi]
    x_label = x_axis_labels[x_axis]
    
    # Aggregate data by x-axis if needed (for week/month/year)
    if x_axis != 'index':
        df_agg = df.groupby(x_col).agg({
            kpi_col: 'max',  # Use max value for the period
            'workout_date': 'max',
            pct_change_columns[kpi]: 'mean'  # Average percentage change
        }).reset_index()
    else:
        df_agg = df.copy()
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add bar chart for KPI
    fig.add_trace(go.Bar(
        x=df_agg[x_col],
        y=df_agg[kpi_col],
        name=kpi_label,
        marker=dict(
            color=df_agg[kpi_col],
            colorscale='Blues',
            showscale=False
        ),
        hovertemplate=(
            f"<b>{x_label}: %{{x}}</b><br>"
            f"{kpi_label}: %{{y:.1f}}<br>"
            "<extra></extra>"
        ),
        yaxis='y1'
    ))
    
    # Add trend line if requested
    if show_trend and pct_change_columns[kpi] in df_agg.columns:
        pct_col = pct_change_columns[kpi]
        
        # Filter out None/NaN values
        trend_data = df_agg[df_agg[pct_col].notna()].copy()
        
        if not trend_data.empty:
            # Color based on positive/negative
            colors = ['green' if val >= 0 else 'red' for val in trend_data[pct_col]]
            
            fig.add_trace(go.Scatter(
                x=trend_data[x_col],
                y=trend_data[pct_col],
                name='% Change',
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=8, color=colors),
                hovertemplate=(
                    f"<b>{x_label}: %{{x}}</b><br>"
                    "% Change: %{y:.1f}%<br>"
                    "<extra></extra>"
                ),
                yaxis='y2'
            ))
    
    # Update layout
    title_text = f"{df['exercise_name'].iloc[0]} - {kpi_label}"
    
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=20)),
        xaxis=dict(title=x_label),
        yaxis=dict(
            title=kpi_label,
            side='left'
        ),
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add secondary y-axis if trend is shown
    if show_trend:
        fig.update_layout(
            yaxis2=dict(
                title='% Change',
                overlaying='y',
                side='right',
                showgrid=False
            )
        )
    
    return fig
