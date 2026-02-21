# Axis Label Font Color Support

## Issue
Users couldn't change the color of axis label text (tick labels). The color was not configurable and used Plotly's default.

## Solution
Added support for customizable axis label and title font colors:

### 1. Proposal Structure (`app.py`)
Added `font_colors` to the visual configuration:
```json
{
  "visual_config": {
    "font_colors": {
      "axis_label": "#666666",
      "axis_title": "#333333"
    }
  }
}
```

### 2. Modification Parsing (`app.py`)
Updated `parse_modification_request()` to recognize:
- "Change axis label color" or "axis label font color" → Set `font_colors.axis_label`
- "Change axis title color" → Set `font_colors.axis_title`
- "Make axis labels black" → Set `font_colors.axis_label` to "#000000"
- "Pure black axis labels" → Set `font_colors.axis_label` to "#000000"

Added `font_color_updates` to modification structure:
```json
{
  "font_color_updates": {
    "axis_label": "#000000",
    "axis_title": "#000000"
  }
}
```

### 3. Applying Modifications (`app.py`)
Updated `apply_modifications_to_proposal()` to:
- Apply font color updates to the proposal
- Create font_colors section if it doesn't exist

### 4. Chart Rendering (`plotly_chart_generator.py`)
Updated axis configuration to:
- Read font colors from proposal
- Apply to both x-axis and y-axis tick labels
- Use defaults if not specified (axis_label: #666666, axis_title: #333333)
- Fixed duplicate `tickfont` definition in yaxis

## Distinction
This is different from axis line styling:
- **Axis label color** (`font_colors.axis_label`): Color of the tick labels (numbers/text along the axis)
- **Axis line color** (`axis_style.line_color`): Color of the axis line itself

## Usage Examples
Users can now say:
- "Change axis label font pure black"
- "Make axis labels black"
- "Set axis label color to red"
- "Change axis title color to blue"

## Technical Details

### Plotly Parameters
- `tickfont.color`: Color of the tick labels (hex color code)
- Applied to both xaxis and yaxis

### Default Values
- Axis label color: `#666666` (medium gray)
- Axis title color: `#333333` (dark gray)

### Applied To
- X-axis tick labels
- Y-axis tick labels
- Both axes use the same color

## Testing
1. Generate a chart
2. Request: "change axis label font pure black"
3. Verify tick labels on both axes appear in black (#000000)
4. Test with different colors

## Status
✅ Implemented and ready for testing
