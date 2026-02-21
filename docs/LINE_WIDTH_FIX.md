# Chart Line Width (Thickness) Support

## Issue
Users couldn't change the thickness of chart lines (data series lines). The modification parser didn't support `line_width` updates.

## Solution
Added support for customizable line width for all series or individual series:

### 1. Modification Parsing (`app.py`)
Updated `parse_modification_request()` prompt to include:
- `all_series_line_width`: Change line width for all series at once
- `line_width` in `series_updates`: Change line width for specific series

Example modification structure:
```json
{
  "modifications": {
    "all_series_line_width": 5,
    "series_updates": [
      {"index": 0, "line_width": 5}
    ]
  }
}
```

### 2. Applying Modifications (`app.py`)
Updated `apply_modifications_to_proposal()` to:
- Apply `all_series_line_width` to all series when specified
- Apply `line_width` from individual series updates
- Preserve existing line_width if not being changed

### 3. Chart Rendering
The Plotly chart generator already reads `line_width` from series data:
```python
line=dict(
    color=series_info["color"],
    width=series_info["line_width"],  # Already supported
    shape=line_shape
)
```

## Distinction
Important to distinguish between:
- **Chart line thickness** (`series.line_width`): Thickness of data series lines (the actual chart lines)
- **Axis line thickness** (`axis_style.line_width`): Thickness of x-axis and y-axis lines

## Usage Examples
Users can now say:
- "Make the chart lines thickness to 5"
- "Make chart lines thicker"
- "Increase line thickness to 4"
- "Make first line thicker" (for specific series)
- "Thicker data lines"

The AI will parse these and apply the appropriate line width changes.

## Technical Details

### Plotly Parameter
- `line.width`: Width of the line in pixels

### Default Value
- `2` pixels (set during proposal creation)

### Applied To
- Individual series lines
- Can be set globally for all series or per-series

## Prompt Updates
Added examples to help AI distinguish:
- "Make chart lines thicker" → `all_series_line_width`
- "Make axis lines thicker" → `axis_style.line_width`

## Testing
1. Generate a chart
2. Request: "make the chart lines thickness to 5"
3. Verify all data series lines appear thicker (5px instead of 2px)
4. Test with individual series: "make first line thicker"

## Status
✅ Implemented and ready for testing
