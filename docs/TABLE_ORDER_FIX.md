# Data Table Order and Font Fix

## Issues Fixed

### 1. Table Row Order (FIXED)
**Problem**: Header was appearing at the bottom instead of top
```
Wrong:
Head    1.43     1.52   +6.3%
Core    1.84     1.74   -5.4%
2024-11  2024-12  Chg%    <- Header at bottom!
```

**Solution**: Reversed the y-offset calculation for bottom-anchored tables
- For `yanchor="bottom"`: Header gets highest offset (appears at top)
- Formula: `y_offset = (total_lines - 1 - i) * line_height`
- This makes header appear above data rows

**Result**:
```
Correct:
      2024-11  2024-12  Chg%    <- Header at top
Head    1.43     1.52   +6.3%
Core    1.84     1.74   -5.4%
```

### 2. Font Family Support (ADDED)
**Problem**: Font was hardcoded to "Courier New, monospace"

**Solution**: Added `font_family` configuration
- Added to data_table config in proposal
- Added to AI vision analysis prompt
- Added to modification parser
- Defaults to "Arial" to match chart legend

**Usage**:
- "Change table font to Arial"
- "Use Helvetica for table"
- AI detects font from reference image

## Configuration

### Updated data_table Structure
```json
{
  "data_table": {
    "show": true,
    "position": "bottom_right",
    "periods": 2,
    "metrics": ["value", "change_pct"],
    "series_names": [],
    "font_size": 10,
    "font_family": "Arial"  // NEW
  }
}
```

### Font Family Options
- "Arial" (default, matches legend)
- "Helvetica"
- "Courier New" (monospace for alignment)
- "Times New Roman"
- Any standard web font

## Technical Details

### Y-Offset Calculation
```python
if yanchor == "bottom":
    # Reverse order: header at top
    y_offset = (total_lines - 1 - i) * line_height
else:  # top
    # Normal order: header first
    y_offset = -i * line_height
```

### Line Spacing
- `line_height = font_size * 1.5`
- Provides comfortable spacing between rows
- Adjusts automatically with font size

### Rendering Order
1. Calculate total lines
2. For each line (header, then data rows):
   - Calculate y_offset based on anchor
   - Create annotation with proper offset
   - Apply series color
   - Add background/border only to header

## Testing

### Verify Order
1. Generate chart with table
2. Check header appears at top
3. Check data rows appear below header
4. Verify proper spacing

### Verify Font
1. Default should be Arial
2. Should match legend font
3. Can be changed via chat
4. AI should detect from reference

## User Commands

### Change Font
- "Change table font to Arial"
- "Use Helvetica for table"
- "Make table font match legend"

### Other Commands (Still Work)
- "Show data table"
- "Show last 3 months"
- "Make table bigger"
- "Move table to bottom left"

## Status
✅ Fixed - Ready for testing
