"""
Direct chart generator for PCE YoY charts using Plotly.
Ensures 100% match with reference brand standard.
"""

import pandas as pd
import plotly.graph_objects as go


def generate_pce_yoy_chart(csv_data: pd.DataFrame) -> go.Figure:
    """
    Generate Plotly figure for PCE YoY data matching reference style.
    
    Args:
        csv_data: DataFrame with columns: date, key, value, lbl
        
    Returns:
        Plotly Figure object
    """
    # Pivot data from long to wide format
    df_wide = csv_data.pivot(index='date', columns='key', values='value').reset_index()
    
    # Extract data
    dates = pd.to_datetime(df_wide['date'])
    headline_data = df_wide['YoY_pce_headline']
    core_data = df_wide['YoY_pce_core']
    
    # Calculate middle index for label placement
    mid_index = len(dates) // 2
    mid_date = dates.iloc[mid_index]
    headline_mid_value = headline_data.iloc[mid_index]
    core_mid_value = core_data.iloc[mid_index]
    
    # Create figure
    fig = go.Figure()
    
    # Add Headline line (blue)
    fig.add_trace(go.Scatter(
        x=dates,
        y=headline_data,
        mode='lines',
        name='Headline',
        line=dict(color='#1f77b4', width=2.5, shape='spline'),
        showlegend=False
    ))
    
    # Add Core line (green)
    fig.add_trace(go.Scatter(
        x=dates,
        y=core_data,
        mode='lines',
        name='Core',
        line=dict(color='#2ca02c', width=2.5, shape='spline'),
        showlegend=False
    ))
    
    # Add horizontal dashed line at 2%
    fig.add_hline(
        y=2.0,
        line_dash="dash",
        line_color="black",
        line_width=1.5,
        annotation_text="",
        annotation_position="right"
    )
    
    # Add "Headline" label above blue line in middle
    fig.add_annotation(
        x=mid_date,
        y=headline_mid_value,
        text="Headline",
        showarrow=False,
        font=dict(size=14, color='#1f77b4', family='Arial', weight='bold'),
        yshift=20,
        xanchor='center',
        bgcolor='rgba(255,255,255,0.8)',
        borderpad=4
    )
    
    # Add "Core" label below green line in middle
    fig.add_annotation(
        x=mid_date,
        y=core_mid_value,
        text="Core",
        showarrow=False,
        font=dict(size=14, color='#2ca02c', family='Arial', weight='bold'),
        yshift=-20,
        xanchor='center',
        bgcolor='rgba(255,255,255,0.8)',
        borderpad=4
    )
    
    # Update layout to match reference style
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=40, t=40, b=60),
        hovermode='x unified',
        height=500,
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#999',
            tickfont=dict(size=11),
            dtick="M12",  # Show yearly ticks
            tickformat="%Y"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e0e0e0',
            showline=True,
            linecolor='#999',
            tickfont=dict(size=11),
            ticksuffix='%',
            zeroline=False
        )
    )
    
    return fig
