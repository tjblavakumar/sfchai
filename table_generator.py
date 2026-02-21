"""
Table data generation for chart comparison tables.
"""

import pandas as pd
from typing import Dict, List, Optional


def calculate_table_data(csv_data: pd.DataFrame, table_config: dict, series_info: List[dict]) -> Optional[Dict]:
    """
    Calculate table data from CSV for period comparisons.
    
    Args:
        csv_data: DataFrame with chart data
        table_config: Table configuration from proposal
        series_info: List of series configurations
        
    Returns:
        Dict with table data or None if table not shown
    """
    if not table_config.get("show", False):
        return None
    
    # Get configuration
    periods = table_config.get("periods", 2)
    metrics = table_config.get("metrics", ["value", "change_pct"])
    series_names = table_config.get("series_names", [])
    
    # If no series names specified, use all series
    if not series_names:
        series_names = [s["series_name"] for s in series_info]
    
    # Get last N rows
    if len(csv_data) < periods:
        periods = len(csv_data)
    
    last_rows = csv_data.tail(periods)
    
    # Build table data
    table_data = {
        "periods": [],
        "series": {}
    }
    
    # Get period labels (dates or indices)
    date_column = csv_data.columns[0]
    for idx in range(len(last_rows)):
        period_value = last_rows.iloc[idx][date_column]
        # Format date if it's a timestamp
        if pd.api.types.is_datetime64_any_dtype(type(period_value)):
            period_label = period_value.strftime("%Y-%m")
        else:
            period_label = str(period_value)
        table_data["periods"].append(period_label)
    
    # Calculate metrics for each series
    for series in series_info:
        series_name = series["series_name"]
        if series_name not in series_names:
            continue
        
        csv_col = series["csv_column"]
        if csv_col not in csv_data.columns:
            continue
        
        values = last_rows[csv_col].tolist()
        
        series_data = {
            "values": values,
            "metrics": {}
        }
        
        # Calculate requested metrics
        if "change_abs" in metrics and len(values) >= 2:
            # Absolute change from first to last
            series_data["metrics"]["change_abs"] = values[-1] - values[0]
        
        if "change_pct" in metrics and len(values) >= 2:
            # Percentage change from first to last
            if values[0] != 0:
                series_data["metrics"]["change_pct"] = ((values[-1] - values[0]) / abs(values[0])) * 100
            else:
                series_data["metrics"]["change_pct"] = 0
        
        table_data["series"][series_name] = series_data
    
    return table_data


def format_table_value(value: float, metric_type: str = "value") -> str:
    """
    Format a value for display in the table.
    
    Args:
        value: Numeric value
        metric_type: Type of metric (value, change_pct, change_abs)
        
    Returns:
        Formatted string
    """
    if pd.isna(value):
        return "N/A"
    
    if metric_type == "change_pct":
        # Format as percentage with sign
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.1f}%"
    elif metric_type == "change_abs":
        # Format with sign
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.2f}"
    else:
        # Regular value
        return f"{value:.2f}"


def create_table_text(table_data: Dict, table_config: dict, series_info: List[dict]) -> List[Dict]:
    """
    Create text lines for table annotation with color information.
    
    Args:
        table_data: Calculated table data
        table_config: Table configuration
        series_info: List of series configurations with colors
        
    Returns:
        List of dicts with text and color for each line
    """
    if not table_data:
        return []
    
    lines = []
    metrics = table_config.get("metrics", ["value", "change_pct"])
    
    # Create color map from series info
    color_map = {s["series_name"]: s["color"] for s in series_info}
    
    # Header row with periods (no color, use default)
    header = "  " + "  ".join(table_data["periods"])
    if "change_pct" in metrics:
        header += "  Chg%"
    if "change_abs" in metrics:
        header += "  Chg"
    lines.append({"text": header, "color": "#333333"})
    
    # Data rows for each series with their respective colors
    for series_name, series_data in table_data["series"].items():
        row = series_name[:4]  # Abbreviate series name
        
        # Add values
        for value in series_data["values"]:
            row += f"  {format_table_value(value, 'value')}"
        
        # Add change metrics
        if "change_pct" in metrics and "change_pct" in series_data["metrics"]:
            row += f"  {format_table_value(series_data['metrics']['change_pct'], 'change_pct')}"
        
        if "change_abs" in metrics and "change_abs" in series_data["metrics"]:
            row += f"  {format_table_value(series_data['metrics']['change_abs'], 'change_abs')}"
        
        # Use series color
        series_color = color_map.get(series_name, "#333333")
        lines.append({"text": row, "color": series_color})
    
    return lines
