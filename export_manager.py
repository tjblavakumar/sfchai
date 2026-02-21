"""
Export manager for generating standalone HTML and Python files.
"""

import os
import zipfile
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Optional


# Export directory
EXPORT_DIR = Path("downloads")
MAX_EXPORTS = 5  # Keep only last 5 exports


def ensure_export_dir():
    """Create export directory if it doesn't exist."""
    EXPORT_DIR.mkdir(exist_ok=True)


def cleanup_old_exports():
    """Keep only the last MAX_EXPORTS files."""
    if not EXPORT_DIR.exists():
        return
    
    # Get all zip files sorted by modification time
    zip_files = sorted(
        EXPORT_DIR.glob("*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # Remove old files
    for old_file in zip_files[MAX_EXPORTS:]:
        try:
            old_file.unlink()
        except Exception:
            pass


def generate_timestamp() -> str:
    """Generate timestamp in YYYYMMDD_HHMM format."""
    return datetime.now().strftime("%Y%m%d_%H%M")


def export_to_html(fig: go.Figure, csv_data: pd.DataFrame, proposal: Dict) -> str:
    """
    Export chart as standalone HTML file in a zip.
    
    Args:
        fig: Plotly figure
        csv_data: DataFrame with chart data
        proposal: Chart proposal
        
    Returns:
        Path to created zip file
    """
    ensure_export_dir()
    cleanup_old_exports()
    
    timestamp = generate_timestamp()
    zip_filename = EXPORT_DIR / f"{timestamp}_html.zip"
    
    # Create temporary files
    html_file = EXPORT_DIR / "chart.html"
    csv_file = EXPORT_DIR / "data.csv"
    readme_file = EXPORT_DIR / "README.txt"
    
    try:
        # Export HTML with inline Plotly
        fig.write_html(
            str(html_file),
            include_plotlyjs='inline',  # Embed Plotly for offline use
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
            }
        )
        
        # Export CSV
        csv_data.to_csv(csv_file, index=False)
        
        # Create README
        readme_content = f"""SF CHAI Chart Export
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Files Included:
- chart.html: Interactive chart (open in any web browser)
- data.csv: Source data used to create the chart
- README.txt: This file

How to Use:
1. Extract all files from this zip
2. Double-click chart.html to open in your browser
3. The chart is fully interactive - hover, zoom, pan
4. No internet connection required (Plotly is embedded)

Chart Details:
- Chart Type: {proposal.get('chart_type', 'line')}
- Series Count: {len(proposal['data_mapping']['series'])}
- Data Points: {len(csv_data)} rows

For questions or issues, refer to the SF CHAI documentation.
"""
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        # Create zip file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(html_file, 'chart.html')
            zipf.write(csv_file, 'data.csv')
            zipf.write(readme_file, 'README.txt')
        
        # Clean up temporary files
        html_file.unlink()
        csv_file.unlink()
        readme_file.unlink()
        
        return str(zip_filename)
    
    except Exception as e:
        # Clean up on error
        for f in [html_file, csv_file, readme_file]:
            if f.exists():
                f.unlink()
        raise e


def export_to_python(fig: go.Figure, csv_data: pd.DataFrame, proposal: Dict) -> str:
    """
    Export chart as Python script in a zip.
    
    Args:
        fig: Plotly figure
        csv_data: DataFrame with chart data
        proposal: Chart proposal
        
    Returns:
        Path to created zip file
    """
    ensure_export_dir()
    cleanup_old_exports()
    
    timestamp = generate_timestamp()
    zip_filename = EXPORT_DIR / f"{timestamp}_py.zip"
    
    # Create temporary files
    py_file = EXPORT_DIR / "chart.py"
    csv_file = EXPORT_DIR / "data.csv"
    readme_file = EXPORT_DIR / "README.txt"
    
    try:
        # Generate Python script
        python_code = generate_python_script(csv_data, proposal)
        
        with open(py_file, 'w') as f:
            f.write(python_code)
        
        # Export CSV
        csv_data.to_csv(csv_file, index=False)
        
        # Create README
        readme_content = f"""SF CHAI Chart Export - Python Script
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Files Included:
- chart.py: Python script to generate the chart
- data.csv: Source data (for reference)
- README.txt: This file

Requirements:
- Python 3.8 or higher
- Required packages (install with pip):
  pip install plotly pandas

How to Use:
1. Extract all files from this zip
2. Install required packages (see above)
3. Run: python chart.py
4. Chart will open in your default browser

The script includes:
- Data embedded in the code (fully standalone)
- All chart styling and configuration
- Comments explaining each section

You can modify the script to:
- Change colors, fonts, sizes
- Add/remove series
- Adjust annotations
- Customize any aspect of the chart

For questions or issues, refer to the SF CHAI documentation.
"""
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        # Create zip file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(py_file, 'chart.py')
            zipf.write(csv_file, 'data.csv')
            zipf.write(readme_file, 'README.txt')
        
        # Clean up temporary files
        py_file.unlink()
        csv_file.unlink()
        readme_file.unlink()
        
        return str(zip_filename)
    
    except Exception as e:
        # Clean up on error
        for f in [py_file, csv_file, readme_file]:
            if f.exists():
                f.unlink()
        raise e


def generate_python_script(csv_data: pd.DataFrame, proposal: Dict) -> str:
    """
    Generate Python script that recreates the chart.
    
    Args:
        csv_data: DataFrame with chart data
        proposal: Chart proposal
        
    Returns:
        Python script as string
    """
    # Convert data to embedded format
    data_dict = csv_data.to_dict('list')
    
    # Extract configuration
    series_list = proposal['data_mapping']['series']
    x_col = proposal['data_mapping']['x_axis_column']
    visual_config = proposal['visual_config']
    
    script = f'''"""
SF CHAI Generated Chart
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This script recreates the chart with all styling and data embedded.
You can modify any aspect of the chart by editing the code below.

Requirements:
- plotly (tested with 5.18.0+)
- pandas (tested with 2.0.0+)

Install with: pip install plotly pandas
"""

import plotly.graph_objects as go
import pandas as pd

# ============================================================================
# Data (embedded)
# ============================================================================

data = {repr(data_dict)}

# Create DataFrame
df = pd.DataFrame(data)

# ============================================================================
# Chart Configuration
# ============================================================================

# Series configuration
series_config = {repr(series_list)}

# Visual configuration
visual_config = {repr(visual_config)}

# ============================================================================
# Create Chart
# ============================================================================

fig = go.Figure()

# Add series
for series in series_config:
    csv_col = series['csv_column']
    series_name = series['series_name']
    color = series['color']
    line_style = series['line_style']
    line_width = series['line_width']
    
    # Determine line shape
    line_shape = "spline" if line_style == "smooth" else "linear"
    
    # Add trace
    fig.add_trace(go.Scatter(
        x=df['{x_col}'],
        y=df[csv_col],
        mode='lines',
        name=series_name,
        line=dict(
            color=color,
            width=line_width,
            shape=line_shape
        ),
        showlegend=False  # Using custom labels
    ))

# ============================================================================
# Add Annotations
# ============================================================================

# Horizontal lines
for hline in visual_config['annotations']['horizontal_lines']:
    y_value = hline['value']
    label = hline.get('label', '')
    color = hline.get('color', '#000000')
    style = hline.get('style', 'solid')
    font_size = hline.get('font_size', 10)
    
    fig.add_hline(
        y=y_value,
        line_dash="dash" if style == "dashed" else "solid",
        line_color=color,
        line_width=2
    )
    
    if label:
        fig.add_annotation(
            x=1, xref="paper",
            y=y_value,
            text=label,
            showarrow=False,
            xanchor="right",
            font=dict(size=font_size, color=color)
        )

# Vertical lines
for vline in visual_config['annotations']['vertical_lines']:
    x_value = vline['value']
    label = vline.get('label', '')
    color = vline.get('color', '#cccccc')
    style = vline.get('style', 'solid')
    font_size = vline.get('font_size', 10)
    
    fig.add_vline(
        x=x_value,
        line_dash="dash" if style == "dashed" else "solid",
        line_color=color,
        line_width=2
    )
    
    if label:
        fig.add_annotation(
            x=x_value,
            y=1, yref="paper",
            text=label,
            showarrow=False,
            yanchor="top",
            font=dict(size=font_size, color=color)
        )

# Shaded bands
for band in visual_config['annotations']['bands']:
    fig.add_vrect(
        x0=band['start'],
        x1=band['end'],
        fillcolor=band.get('color', '#d3d3d3'),
        opacity=0.3,
        layer="below",
        line_width=0
    )

# ============================================================================
# Add Series Labels
# ============================================================================

legend_type = visual_config['legend']['type']
label_positions = visual_config.get('label_positions', {{}})

if legend_type in ["inline", "inline_middle"]:
    for series in series_config:
        series_name = series['series_name']
        csv_col = series['csv_column']
        color = series['color']
        
        if legend_type == "inline":
            # Label at end
            label_x = df['{x_col}'].iloc[-1]
            label_y = df[csv_col].iloc[-1]
            xanchor = "left"
            xshift = 10
        else:  # inline_middle
            # Label in middle
            middle_idx = len(df) // 2
            label_x = df['{x_col}'].iloc[middle_idx]
            label_y = df[csv_col].iloc[middle_idx]
            xanchor = "center"
            xshift = 0
        
        position = label_positions.get(series_name, "top")
        yshift = 15 if position in ["top", "above"] else -15
        yanchor = "bottom" if position in ["top", "above"] else "top"
        
        fig.add_annotation(
            x=label_x,
            y=label_y,
            text=series_name,
            showarrow=False,
            font=dict(
                size=visual_config['fonts']['legend'],
                color=color,
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

# ============================================================================
# Layout Configuration
# ============================================================================

axis_style = visual_config.get('axis_style', {{}})
font_colors = visual_config.get('font_colors', {{}})
grid_config = visual_config.get('grid', {{}})

fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=60, r=100 if legend_type == "inline" else 40, t=40, b=60),
    hovermode='x unified',
    height=500,
    xaxis=dict(
        showgrid=grid_config.get('show', True),
        gridcolor=grid_config.get('color', '#e0e0e0'),
        showline=True,
        linecolor=axis_style.get('line_color', '#999999'),
        linewidth=axis_style.get('line_width', 1),
        tickfont=dict(
            size=visual_config['fonts']['axis_label'],
            color=font_colors.get('axis_label', '#666666')
        ),
        zeroline=False
    ),
    yaxis=dict(
        showgrid=grid_config.get('show', True),
        gridcolor=grid_config.get('color', '#e0e0e0'),
        showline=True,
        linecolor=axis_style.get('line_color', '#999999'),
        linewidth=axis_style.get('line_width', 1),
        tickfont=dict(
            size=visual_config['fonts']['axis_label'],
            color=font_colors.get('axis_label', '#666666')
        ),
        zeroline=False
    )
)

# ============================================================================
# Display Chart
# ============================================================================

# Show in browser
fig.show()

# Optionally save as HTML
# fig.write_html("chart.html")

print("Chart displayed successfully!")
print("You can modify this script to customize the chart further.")
'''
    
    return script
