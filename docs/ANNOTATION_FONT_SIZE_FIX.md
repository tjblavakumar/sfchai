# Annotation Font Size Support

## Issue
Users couldn't change the font size of annotation labels (horizontal lines, vertical lines, bands). The font size was hardcoded to 10px.

## Solution
Added support for custom font sizes on all annotation types:

### 1. Modification Parsing (`app.py`)
Updated `parse_modification_request()` prompt to include:
- `update_horizontal_line_font_size`: Set font size for all horizontal line labels
- `update_vertical_line_font_size`: Set font size for all vertical line labels  
- `update_band_font_size`: Set font size for all band labels
- Individual annotations can also specify `font_size` when added

### 2. Applying Modifications (`app.py`)
Updated `apply_modifications_to_proposal()` to:
- Apply font size updates to all existing annotations of each type
- Preserve font_size when adding new annotations

### 3. Chart Rendering (`plotly_chart_generator.py`)
Updated all annotation rendering to:
- Read `font_size` from annotation data
- Use default of 10 if not specified
- Apply to horizontal lines, vertical lines, and bands

## Data Structure
Annotations now support optional `font_size` field:

```json
{
  "horizontal_lines": [
    {
      "value": 2.0,
      "label": "Target",
      "color": "#000000",
      "style": "dashed",
      "font_size": 16
    }
  ],
  "vertical_lines": [
    {
      "value": "2020",
      "label": "Event",
      "font_size": 14
    }
  ],
  "bands": [
    {
      "start": "2019-12",
      "end": "2020-02",
      "label": "Covid",
      "color": "#d3d3d3",
      "font_size": 12
    }
  ]
}
```

## Usage Examples
Users can now say:
- "Increase the font size of horizontal annotation label text to 16"
- "Make the horizontal line label bigger, at least 16 font size"
- "Change vertical line label font to 14"
- "Set band label font size to 12"

The AI will parse these requests and apply the font size changes to all annotations of that type.

## Testing
1. Generate a chart with horizontal line annotations
2. Request: "increase the font size horizontal annotation label text. it should be at least 16 font size"
3. Verify the horizontal line label appears larger (16px instead of 10px)
4. Test with vertical lines and bands as well

## Status
✅ Implemented and ready for testing
