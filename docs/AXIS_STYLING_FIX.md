# Axis Styling Support

## Issue
Users couldn't change the appearance of x-axis and y-axis lines. The color was hardcoded to gray (#999) and line width was fixed at 1px.

## Solution
Added support for customizable axis line styling:

### 1. Proposal Structure (`app.py`)
Added `axis_style` to the visual configuration:
```json
{
  "visual_config": {
    "axis_style": {
      "line_color": "#999999",
      "line_width": 1
    }
  }
}
```

### 2. Modification Parsing (`app.py`)
Updated `parse_modification_request()` to recognize:
- "Make axis lines thicker" → Increase `line_width` (e.g., to 2 or 3)
- "Make axis black" or "black axis lines" → Set `line_color` to "#000000"
- "Pure black axis" → Set `line_color` to "#000000"

Added `axis_style_updates` to modification structure:
```json
{
  "axis_style_updates": {
    "line_color": "#000000",
    "line_width": 2
  }
}
```

### 3. Applying Modifications (`app.py`)
Updated `apply_modifications_to_proposal()` to:
- Apply axis style updates to the proposal
- Create axis_style section if it doesn't exist

### 4. Chart Rendering (`plotly_chart_generator.py`)
Updated layout configuration to:
- Read axis styling from proposal
- Apply to both x-axis and y-axis
- Use defaults if not specified (gray #999999, width 1)

## Usage Examples
Users can now say:
- "Make the x-axis and y-axis lines thicker and pure black color"
- "Make axis lines black"
- "Thicker axis lines"
- "Change axis color to red"
- "Set axis line width to 3"

## Technical Details

### Plotly Parameters
- `linecolor`: Color of the axis line (hex color code)
- `linewidth`: Width of the axis line in pixels

### Default Values
- Color: `#999999` (gray)
- Width: `1` pixel

### Applied To
- X-axis line
- Y-axis line
- Both axes use the same styling

## Testing
1. Generate a chart
2. Request: "make the x-axis and y-axis lines thicker and pure black color"
3. Verify both axis lines appear thicker (2-3px) and black (#000000)
4. Test with different colors and widths

## Status
✅ Implemented and ready for testing
