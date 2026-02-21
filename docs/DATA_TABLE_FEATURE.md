# Data Table Feature

## Overview
The data table feature adds a comparison table to your chart, typically showing the last N periods with values and percentage changes. This is commonly used in financial and economic charts to highlight recent trends.

## How It Works

### 1. AI Detection
When you upload a reference chart image, the AI vision analysis automatically detects if there's a data table present and extracts:
- Position (bottom_right, bottom_left, etc.)
- Number of periods shown
- Metrics displayed (values, % change, absolute change)
- Font size

### 2. Auto-Calculation
The system automatically calculates table data from your CSV:
- Extracts last N rows (periods)
- Calculates percentage change between first and last period
- Calculates absolute change
- Formats values appropriately

### 3. Rendering
The table is rendered as a Plotly annotation with:
- Monospace font for proper alignment
- Semi-transparent background
- Border for visibility
- Positioned as specified

## Usage

### Show/Hide Table
- "Show data table"
- "Add comparison table"
- "Hide table"
- "Remove table"

### Customize Periods
- "Show last 3 months in table"
- "Display last 2 periods"
- "Change table to show 4 periods"

### Adjust Font Size
- "Make table bigger"
- "Increase table font size to 12"
- "Smaller table text"

### Change Position
- "Move table to bottom left"
- "Put table at top right"

## Table Structure

### Default Layout
```
      2024-11  2024-12  Chg%
Head    1.43     1.52   +6.3%
Core    1.84     1.74   -5.4%
```

### Components
- **Header Row**: Period labels + metric columns
- **Data Rows**: Series name (abbreviated) + values + changes
- **Metrics**: 
  - Values from each period
  - Chg% (percentage change from first to last)
  - Chg (absolute change, optional)

## Configuration

### In Proposal
```json
{
  "data_table": {
    "show": true,
    "position": "bottom_right",
    "periods": 2,
    "metrics": ["value", "change_pct"],
    "series_names": ["Headline", "Core"],
    "font_size": 10
  }
}
```

### Position Options
- `bottom_right` - Bottom right corner (default)
- `bottom_left` - Bottom left corner
- `bottom_center` - Bottom center
- `top_right` - Top right corner
- `top_left` - Top left corner

### Metrics Options
- `value` - Show period values
- `change_pct` - Show percentage change
- `change_abs` - Show absolute change

## Technical Details

### Calculation Logic
1. Extract last N rows from CSV
2. For each series:
   - Get values for each period
   - Calculate: `change_pct = ((last - first) / |first|) * 100`
   - Calculate: `change_abs = last - first`
3. Format values with appropriate precision

### Formatting
- Values: 2 decimal places
- Percentage: 1 decimal place with % sign
- Sign: + for positive, - for negative
- Alignment: Monospace font ensures columns align

### Rendering
- Uses Plotly `add_annotation()` with paper coordinates
- Background: Semi-transparent white (0.9 opacity)
- Border: Light gray (#cccccc)
- Padding: 8px
- Font: Courier New (monospace)

## Examples

### Basic Table
```
User: "Show data table"
Result: Table appears at bottom right with last 2 periods
```

### Custom Periods
```
User: "Show last 3 months in table"
Result: Table shows 3 periods instead of 2
```

### Larger Font
```
User: "Make table bigger"
Result: Font size increases (e.g., from 10 to 12)
```

### Different Position
```
User: "Move table to bottom left"
Result: Table repositions to bottom left corner
```

## Limitations

1. **Minimum Data**: Requires at least 2 periods in CSV for change calculations
2. **Series Names**: Abbreviated to 4 characters for compact display
3. **Alignment**: Works best with monospace fonts
4. **Export**: Table is part of the chart image when exported

## Best Practices

1. **Periods**: 2-3 periods work best for readability
2. **Font Size**: 10-12px recommended
3. **Position**: Bottom right is standard for financial charts
4. **Metrics**: Include change_pct for trend visibility
5. **Series**: Limit to 2-4 series for compact display

## Troubleshooting

### Table Not Showing
- Check if `show: true` in configuration
- Verify CSV has enough rows (minimum 2)
- Ensure series names match CSV columns

### Misaligned Columns
- Table uses monospace font (Courier New)
- If still misaligned, check for very long values

### Values Incorrect
- Verify CSV data is numeric
- Check that last N rows contain expected data
- Ensure date column is first column

### Table Too Small/Large
- Adjust font_size (default: 10)
- Recommended range: 8-14px

## Future Enhancements

Potential improvements:
- Custom column headers
- More metric types (min, max, average)
- Color coding (green for positive, red for negative)
- Conditional formatting
- Multiple table support
- HTML table option for better styling
