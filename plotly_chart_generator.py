"""
Plotly-based chart generator with support for middle-of-line labels.
This addresses the limitation of ECharts for label positioning.
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional


def generate_plotly_chart(proposal: dict, csv_data: pd.DataFrame) -> go.Figure:
    """
    Generate a Plotly chart from proposal with support for middle-of-line labels.
    
    Args:
        proposal: Chart proposal with configuration
        csv_data: DataFrame with chart data
        
    Returns:
        Plotly Figure object
    """
    # Pivot data if needed
    if 'key' in csv_data.columns and 'value' in csv_data.columns:
        csv_data = csv_data.pivot(index='date', columns='key', values='value').reset_index()
    
    # Get x-axis data
    x_col = proposal["data_mapping"]["x_axis_column"]
    x_data = csv_data[x_col].tolist()
    
    # Get legend configuration
    legend_type = proposal["visual_config"]["legend"]["type"]
    label_positions = proposal["visual_config"].get("label_positions", {})
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for each series
    for series_info in proposal["data_mapping"]["series"]:
        csv_col = series_info["csv_column"]
        series_data = csv_data[csv_col].tolist()
        series_name = series_info["series_name"]
        
        # Determine line shape
        line_shape = "spline" if series_info["line_style"] == "smooth" else "linear"
        
        # Add trace
        fig.add_trace(go.Scatter(
            x=x_data,
            y=series_data,
            mode='lines',
            name=series_name,
            line=dict(
                color=series_info["color"],
                width=series_info["line_width"],
                shape=line_shape
            ),
            showlegend=False  # We'll add custom labels
        ))
    
    # Add annotations for labels
    if legend_type in ["inline", "inline_middle"]:
        for series_info in proposal["data_mapping"]["series"]:
            csv_col = series_info["csv_column"]
            series_data = csv_data[csv_col].tolist()
            series_name = series_info["series_name"]
            
            if legend_type == "inline":
                # Label at end of line
                label_x = x_data[-1]
                label_y = series_data[-1]
                xanchor = "left"
                xshift = 10
            else:  # inline_middle
                # Label in middle of line
                middle_index = len(series_data) // 2
                label_x = x_data[middle_index]
                label_y = series_data[middle_index]
                xanchor = "center"
                xshift = 0
            
            # Get position (above or below)
            position = label_positions.get(series_name, "top")
            # Ensure yshift is an integer
            yshift = 15 if position in ["top", "above"] else -15
            yanchor = "bottom" if position in ["top", "above"] else "top"
            
            # Ensure xshift is an integer
            xshift = int(xshift) if isinstance(xshift, (int, float)) else 0
            
            # Add annotation
            fig.add_annotation(
                x=label_x,
                y=label_y,
                text=str(series_name),  # Ensure text is string
                showarrow=False,
                font=dict(
                    size=int(proposal["visual_config"]["fonts"]["legend"]),  # Ensure int
                    color=str(series_info["color"]),  # Ensure string
                    family="Arial",
                    weight="bold"
                ),
                xanchor=xanchor,
                yanchor=yanchor,
                xshift=xshift,
                yshift=yshift,
                bgcolor="rgba(255, 255, 255, 0.8)",
                borderpad=4
            )
    
    # Add horizontal line annotations
    annotations = proposal["visual_config"]["annotations"]
    for hline in annotations.get("horizontal_lines", []):
        # Get the label text
        label_text = hline.get("label", "")
        y_value = float(hline.get("value"))  # Ensure it's a float
        
        # Add horizontal line
        fig.add_hline(
            y=y_value,
            line_dash="dash" if hline.get("style") == "dashed" else "solid",
            line_color=hline.get("color", "#000000"),
            line_width=2
        )
        
        # Add annotation separately if there's a label
        if label_text:
            # Get font size from annotation or use default
            font_size = hline.get("font_size", 10)
            fig.add_annotation(
                x=1,
                xref="paper",  # Use paper coordinates for x (0-1 range)
                y=y_value,
                text=label_text,
                showarrow=False,
                xanchor="right",
                font=dict(size=font_size, color=hline.get("color", "#000000"))
            )
    
    # Add vertical line annotations
    for vline in annotations.get("vertical_lines", []):
        # Get the value - could be string or number
        vline_value = vline.get("value")
        label_text = vline.get("label", "")
        
        # Add vertical line without annotation_text to avoid type errors
        fig.add_vline(
            x=vline_value,
            line_dash="dash" if vline.get("style") == "dashed" else "solid",
            line_color=vline.get("color", "#cccccc"),
            line_width=2
        )
        
        # Add annotation separately if there's a label
        if label_text:
            # Get font size from annotation or use default
            font_size = vline.get("font_size", 10)
            fig.add_annotation(
                x=vline_value,
                y=1,
                yref="paper",  # Use paper coordinates for y (0-1 range)
                text=label_text,
                showarrow=False,
                yanchor="top",
                font=dict(size=font_size, color=vline.get("color", "#cccccc"))
            )
    
    # Add shaded bands (vertical rectangles)
    for band in annotations.get("bands", []):
        start_value = band.get("start")
        end_value = band.get("end")
        label_text = band.get("label", "")
        color = band.get("color", "#d3d3d3")  # Default light gray
        
        # Add shaded rectangle without annotation to avoid type errors
        fig.add_vrect(
            x0=start_value,
            x1=end_value,
            fillcolor=color,
            opacity=0.3,
            layer="below",
            line_width=0
        )
        
        # Add annotation separately if there's a label
        if label_text:
            # Get font size from annotation or use default
            font_size = band.get("font_size", 10)
            # Calculate middle position for the label
            # For string x-axis, we need to find the index
            if isinstance(start_value, str):
                try:
                    start_idx = x_data.index(start_value)
                    end_idx = x_data.index(end_value)
                    mid_idx = (start_idx + end_idx) // 2
                    mid_x = x_data[mid_idx]
                except (ValueError, IndexError):
                    mid_x = start_value  # Fallback to start
            else:
                mid_x = (start_value + end_value) / 2
            
            fig.add_annotation(
                x=mid_x,
                y=1,
                yref="paper",
                text=label_text,
                showarrow=False,
                yanchor="top",
                font=dict(size=font_size, color=color)
            )
    
    # Update layout
    # Get axis styling
    axis_style = proposal["visual_config"].get("axis_style", {})
    axis_line_color = axis_style.get("line_color", "#999999")
    axis_line_width = axis_style.get("line_width", 1)
    
    # Get font colors
    font_colors = proposal["visual_config"].get("font_colors", {})
    axis_label_color = font_colors.get("axis_label", "#666666")
    axis_title_color = font_colors.get("axis_title", "#333333")
    
    # Get grid configuration
    grid_config = proposal["visual_config"].get("grid", {})
    grid_color = grid_config.get("color", "#e0e0e0")
    show_grid = grid_config.get("show", True)
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=100 if legend_type == "inline" else 40, t=40, b=60),
        hovermode='x unified',
        height=500,
        xaxis=dict(
            showgrid=show_grid,
            gridcolor=grid_color,
            showline=True,
            linecolor=axis_line_color,
            linewidth=axis_line_width,
            tickfont=dict(
                size=proposal["visual_config"]["fonts"]["axis_label"],
                color=axis_label_color
            ),
            zeroline=False
        ),
        yaxis=dict(
            showgrid=show_grid,
            gridcolor=grid_color,
            showline=True,
            linecolor=axis_line_color,
            linewidth=axis_line_width,
            tickfont=dict(
                size=proposal["visual_config"]["fonts"]["axis_label"],
                color=axis_label_color
            ),
            zeroline=False
        )
    )
    
    return fig


def convert_plotly_to_json(fig: go.Figure) -> dict:
    """
    Convert Plotly figure to JSON for storage/transmission.
    
    Args:
        fig: Plotly Figure object
        
    Returns:
        JSON-serializable dict
    """
    return fig.to_dict()


def render_plotly_chart(fig_json: dict) -> go.Figure:
    """
    Render Plotly chart from JSON.
    
    Args:
        fig_json: Plotly figure as JSON dict
        
    Returns:
        Plotly Figure object
    """
    return go.Figure(fig_json)
